package main

import (
	"bufio"
	"bytes"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

const (
	version      = "0.2.1"
	maxMessage   = 1 << 20
	stateVersion = 1
)

type state struct {
	Version         int    `json:"version"`
	Client          string `json:"client"`
	Origin          string `json:"origin,omitempty"`
	Endpoint        string `json:"endpoint,omitempty"`
	OneName         string `json:"one_name,omitempty"`
	GrantID         string `json:"grant_id,omitempty"`
	Token           string `json:"token,omitempty"`
	ExpiresAt       string `json:"expires_at,omitempty"`
	RequestID       string `json:"request_id,omitempty"`
	Verifier        string `json:"verifier,omitempty"`
	UserCode        string `json:"user_code,omitempty"`
	VerifyURI       string `json:"verification_uri,omitempty"`
	PendingUntil    string `json:"pending_until,omitempty"`
	SessionID       string `json:"-"`
	Verified        bool   `json:"-"`
	IntervalSeconds int    `json:"interval_seconds,omitempty"`
	LastPoll        string `json:"last_poll,omitempty"`
}

type rpcRequest struct {
	JSONRPC string          `json:"jsonrpc"`
	ID      json.RawMessage `json:"id,omitempty"`
	Method  string          `json:"method"`
	Params  json.RawMessage `json:"params,omitempty"`
}

type rpcResponse struct {
	JSONRPC string          `json:"jsonrpc,omitempty"`
	ID      json.RawMessage `json:"id,omitempty"`
	Result  json.RawMessage `json:"result,omitempty"`
	Error   *rpcError       `json:"error,omitempty"`
}
type rpcError struct {
	Code    int             `json:"code"`
	Message string          `json:"message"`
	Data    json.RawMessage `json:"data,omitempty"`
}

type connector struct {
	mu       sync.Mutex
	client   string
	stateDir string
	st       state
	nextID   int64
}

func main() {
	client := flag.String("client", "", "codex or claude-code")
	stateDir := flag.String("state-dir", "", "private state directory")
	showVersion := flag.Bool("version", false, "print version")
	flag.Parse()
	if *showVersion {
		fmt.Println(version)
		return
	}
	if *client != "codex" && *client != "claude-code" {
		fmt.Fprintln(os.Stderr, "--client must be codex or claude-code")
		os.Exit(2)
	}
	dir, err := resolveStateDir(*client, *stateDir)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	c := &connector{client: *client, stateDir: dir}
	if st, err := loadState(dir, *client); err == nil {
		c.st = st
	} else if !errors.Is(err, os.ErrNotExist) {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	if c.st.Client == "" {
		c.st = state{Version: stateVersion, Client: *client}
	}
	c.serve()
}

func (c *connector) serve() {
	s := bufio.NewScanner(os.Stdin)
	s.Buffer(make([]byte, 4096), maxMessage)
	w := bufio.NewWriter(os.Stdout)
	defer w.Flush()
	for s.Scan() {
		var req rpcRequest
		if len(s.Bytes()) > maxMessage || json.Unmarshal(s.Bytes(), &req) != nil {
			writeRPC(w, nil, nil, &rpcError{Code: -32700, Message: "invalid_json"})
			w.Flush()
			continue
		}
		if req.JSONRPC != "2.0" || req.Method == "" {
			writeRPC(w, req.ID, nil, &rpcError{Code: -32600, Message: "invalid_request"})
			w.Flush()
			continue
		}
		if len(req.ID) == 0 || string(req.ID) == "null" {
			if strings.HasPrefix(req.Method, "notifications/") {
				_, _ = c.call(req.Method, req.Params)
			}
			continue
		}
		res, err := c.call(req.Method, req.Params)
		if err != nil {
			writeRPC(w, req.ID, nil, typedError(err))
		} else {
			writeRPC(w, req.ID, res, nil)
		}
		if req.Method == "tools/call" && err == nil {
			var args struct {
				Name string `json:"name"`
			}
			_ = json.Unmarshal(req.Params, &args)
			if args.Name == "maurice.connection_check" || args.Name == "maurice.disconnect" {
				c.mu.Lock()
				verified := c.st.Verified
				c.mu.Unlock()
				if verified || args.Name == "maurice.disconnect" {
					_, _ = w.WriteString("{\"jsonrpc\":\"2.0\",\"method\":\"notifications/tools/list_changed\"}\n")
				}
			}
		}
		w.Flush()
	}
}

func writeRPC(w *bufio.Writer, id json.RawMessage, result any, rpcErr *rpcError) {
	v := map[string]any{"jsonrpc": "2.0", "id": json.RawMessage(id)}
	if rpcErr != nil {
		v["error"] = rpcErr
	} else {
		v["result"] = result
	}
	b, _ := json.Marshal(v)
	_, _ = w.Write(append(b, '\n'))
}

func typedError(err error) *rpcError {
	msg := err.Error()
	code := -32000
	if strings.HasPrefix(msg, "grant_invalid:") {
		code = -32001
		msg = strings.TrimPrefix(msg, "grant_invalid:")
	}
	if strings.HasPrefix(msg, "out_of_scope:") {
		code = -32002
		msg = strings.TrimPrefix(msg, "out_of_scope:")
	}
	return &rpcError{Code: code, Message: msg}
}

func (c *connector) call(method string, raw json.RawMessage) (any, error) {
	switch method {
	case "initialize":
		requested := "2025-06-18"
		var p struct {
			ProtocolVersion string `json:"protocolVersion"`
		}
		if len(raw) > 0 {
			_ = json.Unmarshal(raw, &p)
			if p.ProtocolVersion == "2025-03-26" || p.ProtocolVersion == "2025-06-18" {
				requested = p.ProtocolVersion
			}
		}
		return map[string]any{"protocolVersion": requested, "capabilities": map[string]any{"tools": map[string]any{"listChanged": true}}, "serverInfo": map[string]string{"name": "maurice-connector", "version": version}}, nil
	case "notifications/initialized", "ping":
		return map[string]any{}, nil
	case "tools/list":
		return c.toolsList()
	case "tools/call":
		var p struct {
			Name      string          `json:"name"`
			Arguments json.RawMessage `json:"arguments"`
		}
		if err := json.Unmarshal(raw, &p); err != nil || p.Name == "" {
			return nil, errors.New("invalid_tools_call")
		}
		v, err := c.toolCall(p.Name, p.Arguments)
		if err != nil {
			return toolErrorResult(err), nil
		}
		if p.Name == "maurice.search" || p.Name == "maurice.explain" || p.Name == "maurice.execute" {
			return v, nil
		}
		return toolResult(v), nil
	default:
		return nil, fmt.Errorf("method_not_supported:%s", method)
	}
}

func toolResult(v any) map[string]any {
	b, _ := json.Marshal(v)
	return map[string]any{"content": []map[string]string{{"type": "text", "text": string(b)}}, "structuredContent": v}
}
func toolErrorResult(err error) map[string]any {
	code := safeRemoteCode(strings.SplitN(err.Error(), ":", 2)[0])
	return map[string]any{"content": []map[string]string{{"type": "text", "text": err.Error()}}, "structuredContent": map[string]any{"code": code, "message": err.Error()}, "isError": true}
}

func localTools() []map[string]any {
	return []map[string]any{
		{"name": "maurice.connection_status", "description": "Etat redacte de la connexion One.", "inputSchema": schema(map[string]any{"type": "object", "properties": map[string]any{}, "additionalProperties": false})},
		{"name": "maurice.connect", "description": "Demarre un pairing One explicite.", "inputSchema": schema(map[string]any{"type": "object", "properties": map[string]any{"one_url": map[string]string{"type": "string"}}, "required": []string{"one_url"}, "additionalProperties": false})},
		{"name": "maurice.disconnect", "description": "Oublie seulement la connexion locale ou la demande en cours. Les autorisations existantes doivent être révoquées dans One.", "inputSchema": schema(map[string]any{"type": "object", "properties": map[string]any{}, "additionalProperties": false})},
		{"name": "maurice.connection_check", "description": "Observe une fois le pairing puis verifie le catalogue.", "inputSchema": schema(map[string]any{"type": "object", "properties": map[string]any{}, "additionalProperties": false})},
	}
}
func schema(v map[string]any) map[string]any { return v }

func (c *connector) toolsList() (any, error) {
	c.mu.Lock()
	connected := c.st.Token != "" && c.st.Endpoint != ""
	verified := c.st.Verified
	c.mu.Unlock()
	t := localTools()
	if connected && !verified {
		if _, err := c.check(); err != nil {
			return map[string]any{"tools": t}, nil
		}
	}
	if !connected {
		return map[string]any{"tools": t}, nil
	}
	remote, err := c.remoteRPC("tools/list", nil)
	if err != nil {
		return map[string]any{"tools": t}, nil
	}
	var obj struct {
		Tools []map[string]any `json:"tools"`
	}
	if err := json.Unmarshal(remote.Result, &obj); err != nil {
		return nil, errors.New("invalid_tools_list")
	}
	return map[string]any{"tools": append(t, obj.Tools...)}, nil
}

func (c *connector) toolCall(name string, args json.RawMessage) (any, error) {
	switch name {
	case "maurice.connection_status":
		c.mu.Lock()
		hasToken := c.st.Token != ""
		c.mu.Unlock()
		if hasToken {
			return c.check()
		}
		return c.status(), nil
	case "maurice.connect":
		var p struct {
			OneURL string `json:"one_url"`
		}
		if json.Unmarshal(args, &p) != nil {
			return nil, errors.New("invalid_one_url")
		}
		return c.connect(p.OneURL)
	case "maurice.connection_check":
		return c.check()
	case "maurice.disconnect":
		return c.disconnect()
	case "maurice.search", "maurice.explain", "maurice.execute":
		unlock, err := acquireStateLock(c.stateDir)
		if err != nil {
			return nil, err
		}
		defer unlock()
		latest, err := loadState(c.stateDir, c.client)
		if errors.Is(err, os.ErrNotExist) {
			return nil, errors.New("not_connected")
		}
		if err != nil {
			return nil, errors.New("state_unavailable")
		}
		c.mu.Lock()
		if latest.Token != c.st.Token || latest.Endpoint != c.st.Endpoint {
			c.st = latest
		}
		ok := c.st.Token != ""
		c.mu.Unlock()
		if !ok {
			return nil, errors.New("not_connected")
		}
		value, err := c.remoteTool(name, args)
		if err != nil {
			c.revokeOnGrantInvalid(err)
			return nil, err
		}
		if failure := toolFailure(value); failure != nil {
			c.revokeOnGrantInvalid(failure)
		}
		return value, nil
	default:
		return nil, errors.New("tool_not_found")
	}
}

func (c *connector) status() map[string]any {
	c.mu.Lock()
	defer c.mu.Unlock()
	if st, err := loadState(c.stateDir, c.client); err == nil {
		if st.Token == c.st.Token && st.Endpoint == c.st.Endpoint {
			st.Verified, st.SessionID = c.st.Verified, c.st.SessionID
		}
		c.st = st
	}
	result := map[string]any{"client": c.client, "status": "disconnected"}
	if c.st.Origin != "" {
		// A remembered explicit target is a proposal, never an implicit reconnect.
		result["one_origin"] = c.st.Origin
		result["one_name"] = c.st.OneName
	}
	if c.st.RequestID != "" && c.st.Token == "" {
		result["status"] = "pending"
		if !parseTime(c.st.PendingUntil).After(time.Now()) {
			result["status"] = "expired"
		}
		result["one_origin"] = c.st.Origin
		result["verification_uri"] = c.st.VerifyURI
		result["user_code"] = c.st.UserCode
		result["expires_at"] = c.st.PendingUntil
	}
	if c.st.Token != "" {
		if c.st.Verified {
			result["status"] = "connected"
		} else {
			result["status"] = "configured_unverified"
		}
		result["one_origin"] = c.st.Origin
		result["endpoint"] = c.st.Endpoint
		result["grant_id"] = c.st.GrantID
		result["expires_at"] = c.st.ExpiresAt
	}
	return result
}

// disconnect abandons local credentials, including pending verifier material.
// It never claims to revoke an authorization on an unavailable One.
func (c *connector) disconnect() (any, error) {
	unlock, err := acquireStateLock(c.stateDir)
	if err != nil {
		return nil, err
	}
	defer unlock()
	latest, err := loadState(c.stateDir, c.client)
	if err != nil && !errors.Is(err, os.ErrNotExist) {
		return nil, errors.New("state_unavailable")
	}
	c.mu.Lock()
	defer c.mu.Unlock()
	previous := c.st
	c.st = state{Version: stateVersion, Client: c.client}
	if err := c.saveLocked(); err != nil {
		c.st = previous
		return nil, err
	}
	result := map[string]any{"status": "disconnected", "client": c.client}
	if latest.Token != "" || latest.RequestID != "" {
		result["authorization_may_remain_on_one"] = true
		result["previous_one_origin"] = latest.Origin
		result["next_action"] = "Revoke or refuse the previous authorization in One; local disconnect does not revoke it."
	}
	return result, nil
}

func (c *connector) connect(raw string) (any, error) {
	candidate, err := url.Parse(strings.TrimSpace(raw))
	if err == nil && candidate != nil && candidate.Fragment == "/" && (candidate.Path == "/one" || candidate.Path == "/one/" || candidate.Path == "/maurice" || candidate.Path == "/maurice/") {
		candidate.Fragment = ""
		raw = candidate.String()
	}
	origin, err := normalizeOrigin(raw)
	if err != nil {
		return nil, err
	}
	unlock, err := acquireStateLock(c.stateDir)
	if err != nil {
		return nil, err
	}
	defer unlock()
	if st, e := loadState(c.stateDir, c.client); e == nil {
		c.mu.Lock()
		c.st = st
		c.mu.Unlock()
	} else if !errors.Is(e, os.ErrNotExist) {
		return nil, e
	}
	c.mu.Lock()
	defer c.mu.Unlock()
	if c.st.Token != "" {
		return nil, errors.New("active_connection")
	}
	if c.st.RequestID != "" && !parseTime(c.st.PendingUntil).After(time.Now()) {
		c.st.RequestID, c.st.Verifier = "", ""
	}
	if c.st.RequestID != "" && c.st.Token == "" && c.st.Origin != origin {
		return nil, errors.New("active_pairing")
	}
	if c.st.RequestID != "" && c.st.Token == "" && c.st.Origin == origin {
		return map[string]any{"status": "pending", "request_id": c.st.RequestID, "user_code": c.st.UserCode, "verification_uri": c.st.VerifyURI, "expires_at": c.st.PendingUntil, "interval_seconds": c.st.IntervalSeconds, "one_name": c.st.OneName, "one_origin": c.st.Origin}, nil
	}
	verifier, challenge, err := pairSecret()
	if err != nil {
		return nil, err
	}
	body, _ := json.Marshal(map[string]string{"client_id": c.client, "code_challenge": challenge})
	var out struct {
		Schema          string `json:"schema"`
		RequestID       string `json:"request_id"`
		UserCode        string `json:"user_code"`
		VerificationURI string `json:"verification_uri"`
		ExpiresAt       string `json:"expires_at"`
		OneName         string `json:"one_name"`
		OneOrigin       string `json:"one_origin"`
		IntervalSeconds int    `json:"interval_seconds"`
	}
	if err := c.httpJSON(origin+"/one/api/assistant-pairing/start", body, "", &out); err != nil {
		return nil, err
	}
	if err := validatePairStart(out, origin); err != nil {
		return nil, err
	}
	if out.IntervalSeconds < 1 || out.IntervalSeconds > 300 {
		return nil, errors.New("invalid_pairing_start")
	}
	outOrigin, _ := normalizeOrigin(out.OneOrigin)
	c.st = state{Version: stateVersion, Client: c.client, Origin: origin, RequestID: out.RequestID, Verifier: verifier, UserCode: out.UserCode, VerifyURI: out.VerificationURI, PendingUntil: out.ExpiresAt, OneName: out.OneName, IntervalSeconds: out.IntervalSeconds}
	if err := c.saveLocked(); err != nil {
		return nil, err
	}
	return map[string]any{"status": "pending", "schema": out.Schema, "request_id": out.RequestID, "user_code": out.UserCode, "verification_uri": out.VerificationURI, "expires_at": out.ExpiresAt, "interval_seconds": out.IntervalSeconds, "one_name": out.OneName, "one_origin": outOrigin}, nil
}

func validatePairStart(out struct {
	Schema          string `json:"schema"`
	RequestID       string `json:"request_id"`
	UserCode        string `json:"user_code"`
	VerificationURI string `json:"verification_uri"`
	ExpiresAt       string `json:"expires_at"`
	OneName         string `json:"one_name"`
	OneOrigin       string `json:"one_origin"`
	IntervalSeconds int    `json:"interval_seconds"`
}, origin string) error {
	if out.Schema != "agentmaurice.assistant_pairing/v1" || len(out.RequestID) != 43 || out.UserCode == "" || out.OneOrigin == "" {
		return errors.New("invalid_pairing_start")
	}
	if len(out.UserCode) != 8 || strings.IndexFunc(out.UserCode, func(r rune) bool { return !(r >= 'A' && r <= 'Z' || r >= '0' && r <= '9' || r == '_' || r == '-') }) >= 0 {
		return errors.New("invalid_pairing_user_code")
	}
	if b, e := base64.RawURLEncoding.DecodeString(out.RequestID); e != nil || len(b) != 32 {
		return errors.New("invalid_pairing_request_id")
	}
	o, err := normalizeOrigin(out.OneOrigin)
	if err != nil || o != origin {
		return errors.New("pairing_origin_mismatch")
	}
	u, err := url.Parse(out.VerificationURI)
	if err != nil || u.User != nil || u.RawQuery != "" || u.Fragment == "" {
		return errors.New("invalid_verification_uri")
	}
	vo, err := normalizeOrigin(u.Scheme + "://" + u.Host)
	if err != nil || vo != origin || u.Path != "/one/" || u.Fragment != "/assistant-pairing/"+out.RequestID {
		return errors.New("invalid_verification_uri")
	}
	if t, err := time.Parse(time.RFC3339, out.ExpiresAt); err != nil || !t.After(time.Now()) || t.After(time.Now().Add(15*time.Minute)) {
		return errors.New("invalid_pairing_expiration")
	}
	return nil
}

func (c *connector) check() (any, error) {
	unlock, err := acquireStateLock(c.stateDir)
	if err != nil {
		return nil, err
	}
	defer unlock()
	if st, e := loadState(c.stateDir, c.client); e == nil {
		c.mu.Lock()
		c.st = st
		c.mu.Unlock()
	} else if !errors.Is(e, os.ErrNotExist) {
		return nil, e
	}
	c.mu.Lock()
	if c.st.Token != "" {
		c.mu.Unlock()
		return c.proveConnection()
	}
	if c.st.RequestID == "" || c.st.Verifier == "" {
		c.mu.Unlock()
		return map[string]any{"status": "disconnected"}, nil
	}
	origin, reqID, verifier := c.st.Origin, c.st.RequestID, c.st.Verifier
	c.mu.Unlock()
	body, _ := json.Marshal(map[string]string{"request_id": reqID, "code_verifier": verifier})
	var out struct {
		Status    string `json:"status"`
		Schema    string `json:"schema"`
		Token     string `json:"token"`
		Endpoint  string `json:"endpoint"`
		GrantID   string `json:"grant_id"`
		ExpiresAt string `json:"expires_at"`
		OneName   string `json:"one_name"`
		OneOrigin string `json:"one_origin"`
	}
	c.mu.Lock()
	if c.st.IntervalSeconds > 0 && time.Since(parseTime(c.st.LastPoll)) < time.Duration(c.st.IntervalSeconds)*time.Second {
		c.mu.Unlock()
		return nil, errors.New("poll_interval_not_elapsed")
	}
	c.st.LastPoll = time.Now().UTC().Format(time.RFC3339Nano)
	if err := c.saveLocked(); err != nil {
		c.mu.Unlock()
		return nil, err
	}
	c.mu.Unlock()
	err = c.httpJSON(origin+"/one/api/assistant-pairing/poll", body, "", &out)
	if err != nil {
		return nil, err
	}
	if out.Status != "connected" {
		if out.Status == "denied" || out.Status == "expired" || out.Status == "consumed" {
			c.mu.Lock()
			c.st.RequestID, c.st.Verifier, c.st.IntervalSeconds, c.st.LastPoll = "", "", 0, ""
			_ = c.saveLocked()
			c.mu.Unlock()
			if out.Status == "consumed" {
				return nil, errors.New("pairing_consumed")
			}
		}
		return map[string]any{"status": out.Status}, nil
	}
	if out.Schema != "agentmaurice.assistant_pairing/v1" || out.Token == "" || out.Endpoint == "" || out.GrantID == "" || !parseTime(out.ExpiresAt).After(time.Now()) {
		return nil, errors.New("invalid_pairing_result")
	}
	if out.OneOrigin != "" {
		oo, err := normalizeOrigin(out.OneOrigin)
		if err != nil || oo != origin {
			return nil, errors.New("pairing_origin_mismatch")
		}
	}
	if err := validateEndpoint(out.Endpoint, origin); err != nil {
		return nil, err
	}
	c.mu.Lock()
	c.st.Token, c.st.Endpoint, c.st.GrantID, c.st.ExpiresAt, c.st.OneName, c.st.Origin, c.st.RequestID, c.st.Verifier, c.st.LastPoll = out.Token, out.Endpoint, out.GrantID, out.ExpiresAt, out.OneName, origin, "", "", ""
	err = c.saveLocked()
	c.mu.Unlock()
	if err != nil {
		return nil, err
	}
	if _, err := c.proveConnection(); err != nil {
		return nil, err
	}
	return c.status(), nil
}

func (c *connector) proveConnection() (any, error) {
	c.mu.Lock()
	c.st.Verified = false
	c.st.SessionID = ""
	c.mu.Unlock()
	init, err := c.remoteRPC("initialize", map[string]any{"protocolVersion": "2025-06-18", "capabilities": map[string]any{}, "clientInfo": map[string]string{"name": "maurice-connector", "version": version}})
	if err != nil {
		c.revokeOnGrantInvalid(err)
		return nil, err
	}
	var initObj map[string]any
	if json.Unmarshal(init.Result, &initObj) != nil || initObj["protocolVersion"] == nil {
		return nil, errors.New("invalid_remote_initialize")
	}
	tools, err := c.remoteRPC("tools/list", nil)
	if err != nil {
		c.revokeOnGrantInvalid(err)
		return nil, err
	}
	var cat struct {
		Tools []map[string]any `json:"tools"`
	}
	if json.Unmarshal(tools.Result, &cat) != nil || len(cat.Tools) != 3 {
		return nil, errors.New("invalid_remote_tools_catalog")
	}
	seen := map[string]bool{}
	for _, tool := range cat.Tools {
		name, ok := tool["name"].(string)
		if !ok || (name != "maurice.search" && name != "maurice.explain" && name != "maurice.execute") || seen[name] {
			return nil, errors.New("invalid_remote_tools_catalog")
		}
		if _, ok := tool["inputSchema"].(map[string]any); !ok {
			return nil, errors.New("invalid_remote_tools_schema")
		}
		seen[name] = true
	}
	value, err := c.remoteTool("maurice.search", json.RawMessage(`{"query":""}`))
	if err == nil {
		err = toolFailure(value)
	}
	if err != nil {
		c.revokeOnGrantInvalid(err)
		return nil, err
	}
	c.mu.Lock()
	c.st.Verified = true
	if err := c.saveLocked(); err != nil {
		c.st.Verified = false
		c.mu.Unlock()
		return nil, err
	}
	c.mu.Unlock()
	return c.status(), nil
}

func (c *connector) revokeOnGrantInvalid(err error) {
	if !strings.HasPrefix(err.Error(), "grant_invalid:") {
		return
	}
	c.mu.Lock()
	defer c.mu.Unlock()
	c.st.Token, c.st.Endpoint, c.st.GrantID, c.st.ExpiresAt, c.st.SessionID, c.st.Verified = "", "", "", "", "", false
	_ = c.saveLocked()
}

func (c *connector) remoteTool(name string, args json.RawMessage) (any, error) {
	res, err := c.remoteRPC("tools/call", map[string]any{"name": name, "arguments": json.RawMessage(args)})
	if err != nil {
		return nil, err
	}
	var v any
	if err := json.Unmarshal(res.Result, &v); err != nil {
		return nil, errors.New("invalid_tool_result")
	}
	if _, ok := v.(map[string]any); !ok {
		return nil, errors.New("invalid_tool_result")
	}
	return v, nil
}

func toolFailure(v any) error {
	obj, ok := v.(map[string]any)
	if !ok {
		return errors.New("invalid_tool_result")
	}
	bad, _ := obj["isError"].(bool)
	if !bad {
		return nil
	}
	code := "remote_tool_error"
	for _, key := range []string{"structuredContent", "structured_content"} {
		if value, ok := obj[key].(map[string]any); ok {
			if failure, ok := value["error"].(map[string]any); ok {
				if text, ok := failure["code"].(string); ok {
					code = safeRemoteCode(text)
				}
			}
		}
	}
	if code == "grant_invalid" {
		return errors.New("grant_invalid:remote_grant_invalid")
	}
	return errors.New(code)
}
func safeRemoteCode(code string) string {
	switch code {
	case "grant_invalid", "out_of_scope", "rate_limited", "quota_exhausted", "invalid_input", "approval_denied", "requires_approval", "request_failed":
		return code
	}
	return "remote_tool_error"
}

func (c *connector) remoteRPC(method string, params any) (rpcResponse, error) {
	c.mu.Lock()
	endpoint, token, session := c.st.Endpoint, c.st.Token, c.st.SessionID
	origin := c.st.Origin
	c.mu.Unlock()
	if err := validateEndpoint(endpoint, origin); err != nil {
		return rpcResponse{}, err
	}
	id := c.nextRequestID()
	req := rpcRequest{JSONRPC: "2.0", ID: json.RawMessage(fmt.Sprintf("%d", id)), Method: method}
	if params != nil {
		req.Params, _ = json.Marshal(params)
	}
	body, _ := json.Marshal(req)
	var res rpcResponse
	if err := c.httpRPC(endpoint, body, token, session, &res); err != nil {
		return res, err
	}
	if string(res.ID) != string(req.ID) || res.JSONRPC != "2.0" {
		return res, errors.New("invalid_mcp_response_id")
	}
	if res.Error != nil {
		code := safeRemoteCode(res.Error.Message)
		if code == "grant_invalid" {
			return res, errors.New("grant_invalid:remote_grant_invalid")
		}
		return res, errors.New(code)
	}
	if len(res.Result) == 0 {
		return res, errors.New("invalid_mcp_response")
	}
	return res, nil
}
func (c *connector) nextRequestID() int64 {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.nextID++
	return c.nextID
}

func (c *connector) httpRPC(endpoint string, body []byte, token, session string, out *rpcResponse) error {
	req, _ := http.NewRequest(http.MethodPost, endpoint, bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json, text/event-stream")
	if token != "" {
		req.Header.Set("Authorization", "Bearer "+token)
	}
	if session != "" {
		req.Header.Set("Mcp-Session-Id", session)
	}
	resp, err := httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode == http.StatusUnauthorized {
		return errors.New("grant_invalid:remote_grant_invalid")
	}
	if resp.StatusCode == http.StatusForbidden {
		return errors.New("out_of_scope:remote_forbidden")
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("remote_http_%d", resp.StatusCode)
	}
	b, err := readRPCBody(resp)
	if err != nil {
		return err
	}
	if json.Unmarshal(b, out) != nil {
		return errors.New("invalid_mcp_response")
	}
	if sid := resp.Header.Get("Mcp-Session-Id"); sid != "" {
		c.mu.Lock()
		c.st.SessionID = sid
		c.mu.Unlock()
	}
	return nil
}

func readRPCBody(resp *http.Response) ([]byte, error) {
	if !strings.Contains(resp.Header.Get("Content-Type"), "text/event-stream") {
		b, err := io.ReadAll(io.LimitReader(resp.Body, maxMessage+1))
		if err != nil {
			return nil, err
		}
		if len(b) > maxMessage {
			return nil, errors.New("response_too_large")
		}
		return b, nil
	}
	scanner := bufio.NewScanner(io.LimitReader(resp.Body, maxMessage+1))
	scanner.Buffer(make([]byte, 4096), maxMessage)
	var data []string
	size := 0
	for scanner.Scan() {
		line := scanner.Text()
		size += len(line) + 1
		if size > maxMessage {
			return nil, errors.New("response_too_large")
		}
		if line == "" && len(data) > 0 {
			b := []byte(strings.Join(data, "\n"))
			data = nil
			var reply rpcResponse
			if json.Unmarshal(b, &reply) == nil && len(reply.ID) > 0 {
				return b, nil
			}
			continue
		}
		if strings.HasPrefix(line, "data:") {
			data = append(data, strings.TrimPrefix(strings.TrimPrefix(line, "data:"), " "))
		}
	}
	if err := scanner.Err(); err != nil {
		return nil, errors.New("invalid_mcp_stream")
	}
	if len(data) > 0 {
		return []byte(strings.Join(data, "\n")), nil
	}
	return nil, errors.New("missing_mcp_reply")
}

var httpClient = &http.Client{Timeout: 10 * time.Second, CheckRedirect: func(_ *http.Request, _ []*http.Request) error { return errors.New("redirect_refused") }}

func (c *connector) httpJSON(endpoint string, body []byte, token string, out any) error {
	req, _ := http.NewRequest(http.MethodPost, endpoint, bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json, text/event-stream")
	if token != "" {
		req.Header.Set("Authorization", "Bearer "+token)
	}
	resp, err := httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	b, err := io.ReadAll(io.LimitReader(resp.Body, maxMessage+1))
	if err != nil {
		return err
	}
	if len(b) > maxMessage {
		return errors.New("response_too_large")
	}
	if resp.StatusCode == 401 {
		return errors.New("grant_invalid:remote_grant_invalid")
	}
	if resp.StatusCode == 403 {
		return errors.New("out_of_scope:remote_forbidden")
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("remote_http_%d", resp.StatusCode)
	}
	if strings.Contains(resp.Header.Get("Content-Type"), "text/event-stream") {
		b = sseData(b)
	}
	if json.Unmarshal(b, out) != nil {
		return errors.New("invalid_pairing_response")
	}
	return nil
}
func sseData(b []byte) []byte {
	var data []string
	for _, line := range strings.Split(strings.ReplaceAll(string(b), "\r\n", "\n"), "\n") {
		if line == "" {
			if len(data) > 0 {
				candidate := []byte(strings.Join(data, "\n"))
				if json.Valid(candidate) {
					return candidate
				}
				data = nil
			}
			continue
		}
		if strings.HasPrefix(line, "data:") {
			data = append(data, strings.TrimPrefix(strings.TrimPrefix(line, "data:"), " "))
		}
	}
	if len(data) > 0 {
		return []byte(strings.Join(data, "\n"))
	}
	return b
}

func pairSecret() (string, string, error) {
	b := make([]byte, 32)
	if _, err := rand.Read(b); err != nil {
		return "", "", err
	}
	v := base64.RawURLEncoding.EncodeToString(b)
	h := sha256.Sum256([]byte(v))
	return v, base64.RawURLEncoding.EncodeToString(h[:]), nil
}

func parseTime(s string) time.Time { t, _ := time.Parse(time.RFC3339Nano, s); return t }

func normalizeOrigin(raw string) (string, error) {
	u, err := url.Parse(strings.TrimSpace(raw))
	if err != nil || u.Scheme == "" || u.Host == "" || u.User != nil || u.RawQuery != "" || u.Fragment != "" {
		return "", errors.New("invalid_one_origin")
	}
	if u.Path != "" && u.Path != "/" && u.Path != "/one" && u.Path != "/one/" && u.Path != "/maurice" && u.Path != "/maurice/" {
		return "", errors.New("invalid_one_path")
	}
	u.Path = ""
	u.RawPath = ""
	u.Host = strings.ToLower(u.Host)
	if u.Scheme == "http" {
		host := u.Hostname()
		if host != "localhost" && host != "127.0.0.1" && host != "::1" {
			return "", errors.New("http_requires_loopback")
		}
	} else if u.Scheme != "https" {
		return "", errors.New("https_required")
	}
	return strings.TrimRight(u.String(), "/"), nil
}

func validateEndpoint(raw, origin string) error {
	u, err := url.Parse(raw)
	if err != nil || u.User != nil || u.RawQuery != "" || u.Fragment != "" || u.Path == "" {
		return errors.New("invalid_mcp_endpoint")
	}
	endpointOrigin, err := normalizeOrigin(u.Scheme + "://" + u.Host)
	if err != nil {
		return errors.New("invalid_mcp_endpoint")
	}
	allowed, err := normalizeOrigin(origin)
	if err != nil {
		return errors.New("invalid_mcp_origin")
	}
	if endpointOrigin == allowed {
		return nil
	}
	// A local One may expose its stdio relay on another loopback port.
	host := strings.ToLower(u.Hostname())
	if u.Scheme == "http" && (host == "localhost" || host == "127.0.0.1" || host == "::1") {
		originURL, _ := url.Parse(allowed)
		originHost := originURL.Hostname()
		if originHost == host {
			return nil
		}
	}
	return errors.New("mcp_endpoint_origin_mismatch")
}

func resolveStateDir(client, explicit string) (string, error) {
	dir := explicit
	if dir == "" && os.Getenv("MAURICE_CONNECTOR_STATE_ROOT") != "" {
		dir = filepath.Join(os.Getenv("MAURICE_CONNECTOR_STATE_ROOT"), client)
	}
	if dir == "" {
		key := "PLUGIN_DATA"
		if client == "claude-code" {
			key = "CLAUDE_PLUGIN_DATA"
		}
		if root := os.Getenv(key); root != "" {
			dir = filepath.Join(root, "connector", client)
		}
	}
	if dir == "" {
		base, err := os.UserConfigDir()
		if err != nil {
			return "", err
		}
		dir = filepath.Join(base, "agentmaurice", "connector", client)
	}
	dir, err := filepath.Abs(dir)
	if err != nil {
		return "", err
	}
	if err = checkStateParents(dir); err != nil {
		return "", err
	}
	_, statErr := os.Lstat(dir)
	if statErr != nil && !errors.Is(statErr, os.ErrNotExist) {
		return "", statErr
	}
	if errors.Is(statErr, os.ErrNotExist) {
		if err = os.MkdirAll(dir, 0700); err != nil {
			return "", err
		}
		if err = makePrivate(dir, true); err != nil {
			return "", err
		}
	}
	info, err := os.Lstat(dir)
	if err != nil || !info.IsDir() {
		return "", errors.New("unsafe_state_dir")
	}
	if err = checkPrivate(dir, info); err != nil {
		return "", err
	}
	return dir, nil
}
func checkStateParents(dir string) error {
	for path := filepath.Clean(dir); ; path = filepath.Dir(path) {
		info, err := os.Lstat(path)
		if err != nil && !errors.Is(err, os.ErrNotExist) {
			return err
		}
		if err == nil && info.Mode()&os.ModeSymlink != 0 {
			// macOS system aliases, before any application-owned path.
			if path != "/var" && path != "/tmp" {
				return errors.New("unsafe_state_path_symlink")
			}
		}
		if filepath.Dir(path) == path {
			break
		}
	}
	return nil
}
func statePath(dir, client string) string { return filepath.Join(dir, client+".json") }
func loadState(dir, client string) (state, error) {
	var st state
	path := statePath(dir, client)
	info, err := os.Lstat(path)
	if err != nil {
		return st, err
	}
	if err = checkPrivate(path, info); err != nil || !info.Mode().IsRegular() {
		return st, errors.New("unsafe_state_file")
	}
	f, err := os.Open(path)
	if err != nil {
		return st, err
	}
	defer f.Close()
	opened, err := f.Stat()
	if err != nil || !os.SameFile(info, opened) {
		return st, errors.New("state_file_changed")
	}
	b, err := io.ReadAll(io.LimitReader(f, maxMessage+1))
	if err != nil {
		return st, err
	}
	if len(b) > maxMessage || json.Unmarshal(b, &st) != nil || st.Client != client || st.Version != stateVersion {
		return st, errors.New("invalid_state")
	}
	st.Verified = false
	st.SessionID = ""
	return st, nil
}
func (c *connector) saveLocked() error {
	if err := checkStateParents(c.stateDir); err != nil {
		return err
	}
	info, err := os.Lstat(c.stateDir)
	if err != nil {
		return err
	}
	if err = checkPrivate(c.stateDir, info); err != nil {
		return err
	}
	path := statePath(c.stateDir, c.client)
	if existing, err := os.Lstat(path); err == nil {
		if err = checkPrivate(path, existing); err != nil {
			return err
		}
	} else if !errors.Is(err, os.ErrNotExist) {
		return err
	}
	b, err := json.Marshal(c.st)
	if err != nil {
		return errors.New("invalid_state")
	}
	f, err := os.CreateTemp(c.stateDir, "."+c.client+"-*.tmp")
	if err != nil {
		return err
	}
	tmp := f.Name()
	defer os.Remove(tmp)
	if err = makePrivate(tmp, false); err == nil {
		_, err = f.Write(append(b, '\n'))
	}
	if err == nil {
		err = f.Sync()
	}
	closeErr := f.Close()
	if err == nil {
		err = closeErr
	}
	if err != nil {
		return err
	}
	return os.Rename(tmp, path)
}
