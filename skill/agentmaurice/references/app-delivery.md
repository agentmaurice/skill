# Application delivery

Load this reference after apply and verification when the user requested a
delivered application outcome.

Report:

- what was built and for which Agent and environment;
- the applied `plan_id`, resource revisions, and source commit;
- Workflows, MiniApps, and Modules created, changed, preserved, or removed;
- end-user authentication and credential-reference assumptions;
- automatic tests and runtime/provenance verification;
- how an authorized caller opens the MiniApp or invokes the Workflow;
- remaining gaps, drift, or manual operational steps.

For a MiniApp, identify the Workflow used for each business side effect and
the verified viewer/bootstrap surface. For a Workflow, identify its public
invocation capability and observed result. For Modules, report catalog
identity, version, source URL, resolved commit, content hash, contributed
resources, and verification results.

Never report success solely because apply returned. Require `spec verify` to
match desired state, observed state, provenance, and blocking tests. If apply
partially committed before a test failure, say so explicitly and report the
current revisions and recovery plan.
