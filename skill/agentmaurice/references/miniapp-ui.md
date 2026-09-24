# MiniApp user interface

Load this reference before writing a MiniApp that a person will use. A MiniApp
shows only what its documents declare: the Viewer has no component library to
look up.

## What the Viewer renders

`ui.renderer: "component"` with `ui.component: "<name>"` is a label, not a
widget. Without one of the blocks below, the Viewer renders that label as
plain text and nothing else: no field, no button, no state. If
`maurice viewer open` returns a UI tree whose only node is a `text` node with
the component name, the MiniApp has no usable interface yet.

Three blocks produce a real interface. Combine them in one MiniApp.

| Block | Declared in | Renders |
|---|---|---|
| Form | the target Workflow's `forms`, used by a `form.submit` event | a button titled with the form title, opening a form with its fields |
| Detail view | `ui.configuration.detail_view` | an optional label and one value read from the MiniApp state |
| List view | `ui.configuration.list_view` | a refresh button and a table bound to a state array |

## Form from the target Workflow

Declare the form on the Workflow, then point a `form.submit` event of the
MiniApp at that Workflow. The first `form.submit` event whose Workflow declares
`forms` provides the MiniApp form.

- Workflow `forms[]`: `id`, `title`, `fields[]`, optional
  `actions_on_submit`.
- Each field: `name`, `type` (`string`, `text`, `number`, `boolean`,
  `select`, `date`, `file`), `required`; optional `title` (the label shown,
  otherwise `name`), `description` (placeholder), `default`, `options`
  (`value`, `label`) for `select`.
- Submitted values are stored in the MiniApp state under the field names.
  Map them in the event input with `"{{ state.<field> }}"`.
- `result_to_state` stores the Workflow output under that state key; show it
  with a detail view.

## Detail view

```json
"configuration": {
  "detail_view": { "state_key": "result", "field": "message", "label": "Answer" }
}
```

It shows `state.result.message` under the label. Without `field`, it shows
`state.<state_key>` itself. Give the key an initial value in `initial_state`
so the first render is not empty.

## List view

```json
"configuration": {
  "list_view": {
    "state_key": "contacts",
    "refresh_event": "refresh-contacts",
    "refresh_label": "Refresh",
    "columns": ["path", "size"],
    "column_labels": { "path": "File", "size": "Bytes" },
    "row_click_event": "select-contact"
  }
}
```

- `refresh_event` names an event with trigger `action.click`; its Workflow
  result goes to `state_key` with `result_to_state`. The state value must be
  an array of objects; `columns` are object keys.
- `row_click_event` names an event with trigger `table.row_click`; the clicked
  row is `{{ event.payload.item.<column> }}` in that event input.

## Complete example

A module that greets a person. It installs with `maurice app add --dev`,
`app plan`, `app apply`, and renders a working form in the One Viewer.

`agents/main/workflows/greet.json`:

```json
{
  "$schema": "agentmaurice.workflow/v2", "schema_version": 2,
  "workflow_id": "greet", "kind": "workflow", "title": "Greet", "version": "1",
  "forms": [{
    "id": "greet-form", "title": "Greet someone",
    "fields": [{ "name": "name", "type": "string", "required": true, "title": "First name" }],
    "actions_on_submit": ["compute"]
  }],
  "actions": [{
    "id": "compute", "type": "code_execution",
    "code": "return {message: 'Hello ' + context.name};",
    "context": { "name": "{{ name }}" }, "output_key": "greeting"
  }],
  "output": { "message": "{{ greeting.message }}" }
}
```

`agents/main/miniapps/greeter.json`:

```json
{
  "$schema": "agentmaurice.miniapp/v2", "schema_version": 2,
  "miniapp_id": "greeter", "kind": "miniapp", "title": "Greeter", "version": "1",
  "ui": {
    "renderer": "component", "component": "greeter",
    "configuration": { "detail_view": { "state_key": "result", "field": "message", "label": "Answer" } }
  },
  "state_schema": { "type": "object", "properties": { "name": { "type": "string" }, "result": { "type": "object" } } },
  "initial_state": { "name": "", "result": { "message": "" } },
  "events": [{
    "event_id": "submit-greet", "trigger": "form.submit",
    "workflow": { "workflow_id": "greet", "input": { "name": "{{ state.name }}" } },
    "result_to_state": "result"
  }]
}
```

## Values and types

A value made of one expression keeps its type: `"{{ state.items }}"` passes
the array itself to the Workflow, and `"context": {"items": "{{ items }}"}`
gives `code_execution` the array. Text mixed with expressions stays text.

## Check what a person sees

1. Publish the MiniApp on the Application surface:
   `maurice app surface set <applicationId> --file surface.json` with
   `{"public_surface": {"version": "0.1.0", "miniapps": [{"agent_id": "<agent>",
   "miniapp_id": "greeter", "version": "1"}]}}`, then
   `maurice app surface publish <applicationId>`.
2. Open it: `maurice app display open <applicationKey> --agent <agent>
   --miniapp greeter --idempotency-key <key>` returns a local link; the One
   home lists the Application, whose page lists its published MiniApps.
3. Drive it without a browser: `maurice viewer connect --deployment <agent>`,
   `viewer open`, `viewer submit <instance> <event> --expected-state-version
   <n>`, `viewer show`. A failing event returns its cause in
   `error.details.cause`.

To change the module, bump its version or commit and run `maurice app add` and
`app plan`/`app apply` again: the reinstall keeps the same Agent, viewer keys
and surface.
