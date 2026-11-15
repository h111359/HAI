# Worked examples — draft 0.3

Storage revision: the user now requires runs inside their owning Activity at
`<activity>/workflow-runs/<run-id>/`, without another Activity-ID level. Runs
move with the Activity on archival. Earlier drafts are preserved in the Activity
revision files; this storage decision supersedes their external-root proposal.

Everything below is illustrative. No example has been installed or executed.

## Complete definition files

- [Customer request](examples/customer-request.md): analyst, architect, developer,
  independent verification and specification-manager, including a clarification loop.
- [Change assessment](examples/change-assessment.md): one role and three custom results.

Each linked file contains the entire workflow; it has no required step sidecars.
Links here are review navigation, not workflow includes. Approval would permit a
later implementation to install selected examples under `.hai_env/workflows/`.

## Normal customer-request trace

Assume an active Activity A, a request to add a configurable CSV export, all required
roles/tools available, explicit product-edit authority, and specification management
enabled with an already compatible maintained tree. This workspace currently has
specification management disabled, so these are hypothetical readiness assumptions.

Let R be run UUID `11111111-1111-4111-8111-111111111111`. Its root is
`<Activity-A>/workflow-runs/R/`. This shorthand is explanatory; actual stored
paths contain the UUID, not the letter R. All paths below are relative to that root.

| Accepted attempt | Consumed file | Result | Accepted evidence | Next |
| --- | --- | --- | --- | --- |
| clarify/attempt-0001 | inputs/request.md | ready | attempts/clarify/attempt-0001/requirements.md | design |
| design/attempt-0001 | preceding requirements.md | designed | attempts/design/attempt-0001/solution-design.md | implement |
| implement/attempt-0001 | preceding solution-design.md | implemented | attempts/implement/attempt-0001/implementation-evidence.md and developer-checks.json | verify |
| verify/attempt-0001 | preceding implementation-evidence.md and developer-checks.json | accepted | attempts/verify/attempt-0001/verified-handoff.md | document |
| document/attempt-0001 | preceding verified-handoff.md | documented | attempts/document/attempt-0001/documentation-receipt.md | end:delivered |

Five allocated attempts, one finished run, Activity A still active. No Git commit,
push or external deployment follows from this process. The specification tree is
updated by its owner; the receipt remains run evidence, not a replacement tree.

## Artifact contents, illustrated

Example `requirements.md`:

```markdown
# Clarified CSV export request
Source: initial request snapshot and attributable customer answers.
Scope: export the current filtered table to UTF-8 CSV using a configurable separator.
Exclusions: scheduled exports, email delivery and deployment.
Acceptance: exported rows match the current filter; commas, quotes and Unicode
round-trip correctly; existing exports retain their documented default behavior.
Open decisions: none required for design.
```

Example `clarification-questions.md` on a different path:

```markdown
# Clarification needed
Requirements producer: clarify/attempt-0001 (actual accepted hash recorded by runtime).
Complete prior clarified baseline: include the entire accepted requirements artifact
and its attributable answers verbatim here, including scope, exclusions and criteria.
Question: should an empty result create a header-only CSV or prevent download?
Why needed: determines API behavior, UI messaging and acceptance tests.
Blocked decision: empty-result behavior only; no customer preference is assumed.
```

Example `developer-checks.json` (fictional, not performed test evidence):

```json
{
  "checks": [
    {"name": "csv-round-trip", "status": "passed", "evidence": "record actual invocation and output here"},
    {"name": "filter-preservation", "status": "passed", "evidence": "record actual invocation and output here"}
  ],
  "limitations": ["Deployment is outside this assignment"]
}
```

The author may require valid JSON and meaningful check entries for this output;
the runtime does not impose JSON or a nonempty-object rule on all artifacts.
The host must reject this illustrative
placeholder as real evidence; it needs actual command/results, scoped tests and
acceptance mapping. This distinction prevents a syntactically valid file from
being mistaken for a verified implementation.

Example `documentation-receipt.md` structure:

```markdown
# Specification update receipt
Configured root: exact workspace-relative value from the owner's validated settings.
Source: accepted verified-handoff producer identity and actual content hash.
Updated files: exact paths, before/after hashes and relevant subject identifiers.
Result: CSV separator and empty-result behavior reconciled to verified implementation.
Checks: actual specification consistency results, with limits.
```

Those statements must be filled with observed facts at execution. A receipt with
unresolved placeholders cannot satisfy the step Expectations.

## Clarification return and attempt preservation

1. Analyst attempt 1 returns ready with requirements.
2. Architect attempt 1 returns needs-clarification with clarification-questions.md.
3. Host resolves the next analyst assignment: request from the initial snapshot,
   architect-questions, including the full accepted clarified baseline and earlier
   answers, from **that accepted architect result**. It does not read an
   older questions file based on a filename match.
4. Analyst attempt 2 obtains a user answer, records its attribution, and returns
   new complete requirements. Attempt 1 remains unchanged.
5. Architect attempt 2 consumes analyst attempt 2, then returns designed.
6. Developer, verifier and documenter proceed normally: seven allocated attempts.

If the analyst cannot obtain the necessary answer, insufficient-input writes its
own questions evidence and terminates needs-input. If the analyst is still waiting
for an answer, the attempt remains waiting and no result is accepted. If clarification
cycles reach the per-step limit, no fourth analyst attempt is allocated; the run
blocks with attempt-limit, retaining the final accepted architect questions.

## Failure and invalid evidence

| Situation | Actual behavior |
| --- | --- |
| Developer reports failed and writes implementation-failure.md with actual effects. | Accept failed if the criterion/evidence hold; terminate failed. |
| Developer process crashes without the failure file. | Record interruption and block; do not take the failed transition. |
| Developer reports implemented but developer-checks.json is missing. | Reject completion and retain blocked attempt; verifier is not dispatched. |
| JSON parses but checks are unrun while result requires required checks to pass. | Host declines acceptance; syntax is not semantic verification. |
| QA finds a reproducible defect. | Write findings and finish changes-requested. A later authorized workflow can take those findings as a declared initial input. |
| Documentation is disabled or a required tree migration lacks approval. | Block dependent work; never change the setting or migrate just to finish. |
| Result name is unknown or two criteria appear equally applicable. | Block acceptance; do not choose by table order. |

The first example deliberately stops on QA defects. A later workflow can define
a QA-to-developer return when its file contracts supply everything needed for repair.
That is supported by the model; this example does not imply implicit access to a
previous design or old implementation attempt.

## Multiple runs in one Activity

After R is finished, run S with UUID `22222222-2222-4222-8222-222222222222` can use
change-assessment in Activity A. It snapshots Activity A's input at its own start
and writes assessment.md only under S/attempts/assess/attempt-0001/. It cannot replace
R's files. One Activity can have many such runs. To consume findings from R, S's
definition must explicitly declare a `workspace:` initial input pointing to the
intended R artifact; core validates same-Activity ownership, original acceptance and
current content hash in the owning Activity's run store. There is no run-to-run call or transition. A prior workflow
artifact is ordinary explicitly bound initial evidence, not inherited global context.

If R is paused with verified ended writers, S may execute. R's future resume
rechecks product/input compatibility, because S may have changed the product even
though their evidence directories are separate. Concurrent active writers are not
supported in the first version.

## Proposed records and requests

These are shape examples, not files created by a workflow runtime. Hash placeholders
represent actual 64-character SHA-256 values in real records.

Start request:

```json
{
  "activity_id": "<owning-activity-uuid>",
  "definition": ".hai_env/workflows/customer-request.md",
  "provenance": {"source": "actual user assignment", "reason": "follow the customer request process"}
}
```

Ready run state after accepted analyst result (required fields illustrated):

```json
{
  "workflow_run_format": 1,
  "activity_id": "<owning-activity-uuid>",
  "run_id": "11111111-1111-4111-8111-111111111111",
  "definition": {"name": "customer-request", "revision": 1, "sha256": "<actual-hash>", "snapshot": "definition.md"},
  "created_at": "<actual-utc-time>",
  "updated_at": "<actual-utc-time>",
  "revision": 4,
  "status": "ready",
  "current_step": "design",
  "current_attempt": null,
  "attempt_count": 1,
  "step_attempt_counts": {"clarify": 1},
  "inputs": {"request": {"source": "activity:input.md", "snapshot": "inputs/request.md", "sha256": "<actual-hash>"}},
  "last_accepted": {"step": "clarify", "attempt": "attempt-0001", "result": "ready", "record": "attempts/clarify/attempt-0001/result.json"},
  "outcome": null,
  "block_reason": null,
  "executor": null
}
```

Frozen assignment to architect:

```json
{
  "assignment_format": 1,
  "activity_id": "<owning-activity-uuid>",
  "run_id": "11111111-1111-4111-8111-111111111111",
  "step_id": "design",
  "attempt_id": "attempt-0001",
  "agent": "solution-architect",
  "definition_sha256": "<pinned-definition-hash>",
  "agent_definition_sha256": "<observed-role-hash>",
  "inputs": {"requirements": {"producer_step": "clarify", "producer_attempt": "attempt-0001", "path": "attempts/clarify/attempt-0001/requirements.md", "sha256": "<accepted-hash>"}},
  "output_root": "attempts/design/attempt-0001/",
  "instruction_source": "definition.md#design",
  "authority_reference": "<actual-Activity-assignment-reference>"
}
```

Completion submission after the host reviews the architect's produced files:

```json
{
  "activity_id": "<owning-activity-uuid>",
  "run_id": "11111111-1111-4111-8111-111111111111",
  "step_id": "design",
  "attempt_id": "attempt-0001",
  "expected_revision": 7,
  "result": "designed",
  "assessment": {"accepted": true, "author": "actual-host-identity", "evidence": "actual design coverage and prerequisite checks"},
  "provenance": {"source": "actual architect handoff plus host review", "reason": "accept the design result"}
}
```

`step_id` is required in completion/record-execution/retry requests because attempt
numbering is local to each step. An ID-only ambiguous request is rejected.

Accepted result.json must include format, Activity/run/step/attempt IDs, result label,
accepted_at, input/output paths and hashes, host assessment, actual executor and
transition. An accepted event includes its operation UUID, sequence, old/new revisions,
result-record path/hash and resulting progress. The event is committed only after
that result and evidence are stable. A crash after result creation but before an
event leaves prepared evidence requiring reconciliation; a matching committed event
with stale state projection is recoverable without executing the agent again.
