# Workflow implementation delivery

The user authorized implementation with: "OK, now implement the workflow agents
and the whole design". This report records implementation of the reviewed package
in `workflow-design/`; its earlier design-only statements remain historical.

## Delivered behavior

- Each definition is one Markdown file with scalar YAML metadata under
  `.hai_env/workflows/`. Presence provides registration; no catalogue was added.
- The shared parser checks one entry, named results, explicit artifact bindings,
  reachable transitions, return paths and finite attempt limits. Formats remain
  author-defined, including binary files, empty files and directories.
- The runtime supports discovery, structural validation, run start/inspection,
  preparation, execution reporting, result acceptance, pause, resume, cancellation
  and explicit retry. Every run belongs to one Activity, with separate attempt
  output directories below `.hai_env/workflow-runs/<activity-id>/<run-id>/`.
- Preparation reserves the Activity's single workflow execution slot. Immutable
  inputs, pinned definitions, accepted evidence and chained transition events
  support safe continuation. Identical completion acknowledgements do not advance
  twice. Ambiguous effects and conflicting partial records require inspection.
- Activity closure checks unfinished runs and writers. Archival preserves stable
  run paths; the host must include associated runs when exporting Activity material.
- The golden workflow-definition-manager package was authored, installed through
  the existing package runtime, registered and validated. Golden and installed
  files match. The manager owns authoring/review, rather than agent dispatch.
- Core conventions, execution/startup procedures, the template, runtime commands,
  test runner and user-facing README describe the new optional feature.
- `change-assessment` and `customer-request` definitions are installed and valid.
  The latter has not been executed against the product.

## Verification

Observed platform: Windows, Python 3.14.7. Tests use workspace-contained Activity
test folders, disabled bytecode writes and no new third-party dependency.

| Check | Observed result |
| --- | --- |
| Definition parser | 23 tests successful, including one platform capability skip. |
| Agent packages | 75 tests successful, including six platform capability skips. |
| Configuration | 13 tests successful, including three platform capability skips. |
| Startup | 66 tests successful, including eight platform capability skips. |
| Existing runtime plus integrated workflow tests | 218 tests successful, including ten platform capability skips. |
| Activity suite | 16 tests passed. |
| Chronicle suite | 17 tests successful, including one platform capability skip. |
| Final workflow/runtime integration subset after additional limit/config/archive checks | 33 tests successful, including one platform capability skip. |
| Content-assessment boundary | Additional focused test passed: existing output with declined host assessment does not advance; correction can complete the same attempt. |
| Interrupted allocation | Three focused checks passed: unexplained empty/partial attempt folders and existing run UUID destinations are preserved and refused; retained preparation replay still works. |
| Final independent runtime check | All 25 workflow runtime tests passed after recovery amendments, without skips. |
| Actual host pilot | `change-assessment` finished with accepted `feasible` outcome after a real separately launched solution architect produced the declared artifact and ended its writers. |
| CLI discovery | Both installed definitions reported valid with no writes. |
| Independent review | No remaining material finding in reviewed scope; retained under invocation `f0caac64-10c5-4980-9012-9fe5f61eb93a/`. |
| Whitespace | `git diff --check` passed. |

Independent review found and verified corrections for ordinary artifact descendants
being mistaken for runtime metadata and predecessor executors incorrectly retaining
ownership after a handoff. Seven mutation previews were independently checked for
zero filesystem changes. Final targeted tests cover disabled-feature configuration,
separate per-step/total limit reporting and actual Activity archival with stable
run reads and rejected closed-owner mutation. Root review also found and corrected
unexplained allocation-folder reuse; a new run or attempt must have a fresh destination.

The broad runtime result predates the last focused additions; its unchanged areas
were not rerun solely to increase the test count. Tests that require unavailable
Windows link creation report skips. Linux/macOS execution remains unverified.

## Acceptance coverage and responsibility

| Scenarios | Evidence or execution boundary |
| --- | --- |
| A1-A4 | Parser fixtures and installed example validation cover grammar, references, incoming data and arbitrary named results. |
| A5-A7 | Runtime evidence checks reject absent/changed/unsafe artifacts. The host must assess the author's written expectations; file existence alone is insufficient. |
| A8-A10, A18, A20-A21 | Runtime fixtures cover distinct returns/attempts, limits, isolated runs and preparation ownership; independent review exercises preview safety. |
| A11-A14, A22-A23 | Tests cover current ownership, closed-owner mutation rejection, definition pinning, role drift, retained partial evidence, stale projection recovery, explicit effect reconciliation and completion replay. |
| A15-A17 | Missing workflow collection permits ordinary work; missing role/model or disabled settings block affected preparation; cancellation retains effects until writers stop. |
| A24 | Binary, empty and directory outputs are accepted without a content-shape whitelist. Author-required meaning and tools remain host checks. |
| A25 | The archival integration test closes only a synthetic Activity, retains run bytes/paths and permits inspection. No general export command was introduced; retention guidance explicitly includes associated runs. |
| A26 | Real installation/registration, installed package validation and exact golden/installed comparison. |

A19 remains retired. No current-task approval rule was added to core or tests.

## Actual pilot

Run: `e1e8a718-d108-49ea-bec5-24572793827b`, owned by this Activity. The applied
assignment resolved installed solution-architect to `gpt-6.1-sol/high`; actual
host task `/root/workflow_pilot_architect` used Activity invocation
`9b442266-8056-46d9-af41-d32da5aab0ff` and received pinned inputs and exact output
destinations. The agent produced the declared
[assessment](../../../workflow-runs/1b440d51-819b-4299-862b-0182f0f4fca5/e1e8a718-d108-49ea-bec5-24572793827b/attempts/assess/attempt-0001/assessment.md).
The host read it against the authored result/expectations, observed the agent's
ended-writers handoff and accepted `feasible` through complete-step. Final state:
`finished`, revision 4, outcome `feasible`. The workflow closure gate reports no
unfinished run or unresolved workflow writer; the Activity remains active.

This pilot demonstrates one real read-only assignment and acceptance. Multi-role
handoffs, loops, interruption and cancellation have fixture evidence; they were
not exercised against product changes in a live customer-request run.

## Boundaries and remaining limits

The host launches actual agents, verifies termination and evaluates content. Runtime
records enforce cooperative contracts; they do not authenticate host statements,
provide OS isolation or guarantee exactly-once external effects. Product changes
remain at their normal maintained locations; attempt receipts identify their evidence.

Serial execution and full retained-state/artifact checks favor correctness and
simple recovery. No large-run performance claim or benchmark is made. Definition
grammar intentionally supports a documented YAML/Markdown subset.

Specification management remains disabled in this workspace. Selecting the
customer-request workflow does not authorize enabling it; its final documentation
step requires valid feature configuration before execution.

Chronicle synchronization encountered unsupported host item `ContextCompaction`
at source position 1852. The best-effort policy permits work to continue; missing
coverage is not claimed as synchronized. Existing retained chronicle evidence was
preserved. Workflow regression checks do not establish full live transcript coverage.

No commit, release, publication or closure of the user's Activity is part of this
delivery.
