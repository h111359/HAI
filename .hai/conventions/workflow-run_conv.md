# Workflow run convention

## Ownership and storage

Core manages `<activity>/workflow-runs/<run-id>/`. The runtime resolves the owning
Activity's current or archived folder by its stable UUID; no Activity-ID directory
is repeated inside workflow-runs. Every run has one
immutable owning Activity UUID, one pinned definition.md, initial input snapshots,
state.json, append-only events.jsonl and attempt directories below attempts/.
Every new run receives a unique UUID. Every step attempt gets a new monotonically
numbered directory; accepted attempts are never reused or overwritten.

Only the sole current active owning Activity permits mutations. Closed owners permit
read-only inspection. Runs move with their Activity during archival and are included
with it in export/retention. Durable references use the Activity UUID and run UUID
or Activity-relative run path, rather than a cached active folder path. No second
Activity lifecycle or global current-run pointer is introduced. A configured Activity
store also contains its workflow runs; no separate run-root setting exists.

Legacy `.hai_env/workflow-runs/<activity-id>/` evidence requires an explicitly
authorized, byte-preserving relocation before dependent operations. Runtime does
not silently read an external fallback, ignore it during closure or split an
Activity's runs across both layouts. Pinned definitions, assignment/result records,
events and historical source references remain unchanged during relocation.

## Host and core boundaries

The host coordinates assignments and actual execution. Core tools do not spawn
models, discover billing sources, approve product scope or assess arbitrary formats.
The host supplies observed execution capability, actual agent handle/liveness and
attributable output assessment. A workflow cannot enable integrations or authorize
publication. Direct role execution and actual separate invocations remain distinct.

The host MUST obtain a normal Activity invocation allocation before each separate
spawn and pass both invocation and workflow run/step/attempt identities. Agent
scratch stays with that invocation; declared outputs go to the attempt. Runtime
state/events/assignment/result records remain core-owned. Activity chat is shared
communication, not accepted workflow state or execution permission.

## Progress and ownership

Runs distinguish ready, prepared, running, waiting, blocked, paused, cancelling,
cancelled and finished progress. These administrative labels do not limit authored
result/outcome names. Prepared/running/waiting or an unfinished blocked/cancelling
attempt holds the Activity's one workflow execution slot. Preparation reserves that
slot before launch, so another run cannot start writing in the gap before launch
confirmation. Multiple ready, safely paused and finished runs may coexist.

Waits retain actual questions/answers. Invalid outputs block transition; the same
unaccepted attempt can correct its outputs before acceptance. Missing authority,
tools, input files or unknown effects are explicit block reasons, never guessed
success. Pausing/cancelling releases writers only after their termination is known.
Cancellation does not undo completed changes. A paused previously started attempt
needs actual effect reconciliation and an explicit new attempt before further work;
a known never-started prepared assignment can resume without replaying work.

max_step_attempts counts allocated attempts of a step, including failed launches;
max_run_attempts counts all allocated attempts. Continuing a waiting attempt or
repeating an identical completion report does not allocate again. Reaching either
limit blocks further dispatch. There is no hidden in-place override of a pinned
definition's limits.

## Acceptance, persistence and recovery

An accepted completion requires the active step/attempt, declared result, all
required stable outputs, unchanged consumed inputs and attributable host assessment.
File/directory formats are unrestricted: file contents and directory manifests
(relative paths, kinds and hashes, including empty directories) establish integrity,
not meaning. Unsafe descendants, overlapping artifacts and scope conflicts block.

Every mutation uses the existing core lock and an expected run-state revision.
Core records actual changes as numbered events and derives current state from the
committed transition. An event ahead of a matching stale state projection can rebuild
that projection without repeating agent work. Truncated events, missing accepted
outputs, conflicting records or partial writes remain preserved and block dependent
mutation; no automatic deletion, truncation or rollback is permitted.

Core MUST check for an identical retained acceptance before rejecting its now-stale
request revision. Repeating an accepted label/assessment with unchanged files returns
the original acceptance and does not advance twice. Changed completion information
is a conflict. Prepared-attempt replay cannot allocate a second attempt.

A crash between a product/tool effect and recording its result requires inspection
of the real effect. Neither an absent result record nor a new conversation proves
the effect failed. The host MUST NOT blindly repeat unknown writes. Existing service
idempotency mechanisms may help; workflow records do not guarantee exactly-once
external execution or OS-level isolation.

Returns to earlier steps create new attempt/input lineage and require subsequent
work to use the new evidence. Earlier accepted results stay historical. Current
input, role, configuration and capability checks can invalidate continuation, even
when the run's definition is unchanged. A changed reusable definition affects new
runs; existing runs keep their snapshots. Unsupported formats require explicit
compatibility work rather than silent conversion.

## Completion and recording

Finishing a run records its authored terminal outcome; it never closes the Activity.
Requested Activity closure MUST resolve all unfinished runs and uncertain writers.
Chronicles and usage retain existing source-attribution and best-effort/required
policies. No workflow operation invents transcript coverage, charges, approvals or
future results. Optional workflow absence must not block ordinary HAI startup/work.

## References

- [Definition convention](workflow_conv.md) — inputs, outputs and result contracts.
- [Execute workflow](../procedures/execute-workflow.md) — host procedure and authority.
- [Runtime commands](../tools/runtime/README.md) — actual accepted request fields.
- [Agent convention](agent_conv.md) — execution mode and independent review.
