# Activity convention

## Layout and ownership

New Activities use layout version 2. Their only root document is README.md. The
runtime records activity_layout_version: 2 in system/state.json, independently of
the environment state format and conversation format. Missing layout markers on
legacy root state.json mean layout 1. Unknown versions, mixed layouts, unsafe
paths and duplicate Activity identities require explicit resolution.

```text
<activity>/
  README.md                         Human entry point and final report
  results/<deliverable>/            Reviewable Activity outputs
  evidence/                         Retained proof, reviews and verification
  history/<document>/<timestamp>/   Exact predecessors and migration recovery
  work/coordinator/                 Disposable coordinator material
  work/test-work/                   Disposable test fixtures
  work/agents/<role>/<uuid>/        Allocated participant work, manifest retained
  system/state.json                 Identity, lifecycle and phase metadata
  system/log.md                     Append-only work and decision history
  system/chat.jsonl                 Persistent typed conversation
  system/usage.md                   Readable usage summary, when available
  system/usage.json                 Usage bindings and checkpoint
  system/recording.json             Always-enabled source reconciliation state
  workflow-runs/<run-id>/            Optional run records and declared outputs
```

Only README.md and system/state.json, system/log.md and system/chat.jsonl are
created initially. Other folders/files appear only with meaningful content.
Runtime validates the root bucket names; agents MUST NOT invent additional root
files or folders. Human-readable JSON deliverables still belong in results:
purpose and ownership determine placement, rather than filename extension.

README.md states or links the objective, original message identity, useful outputs
and evidence. Its managed navigation is derived from existing paths, never a second
status database. The coordinator may revise its authored sections with provenance;
material revisions retain exact predecessors. Closure appends the final result,
performed/skipped checks, limitations, unresolved work and recording coverage to
README.md. Layout 2 has no separate input.md or outcome.md and no virtual aliases.

Results and evidence are retained; work is disposable only after its meaningful
outputs have been collected and writers/effects reconciled. The initial generation
contract declares expected artifact purpose, exact destination, owner and retention.
Canonical product code/specifications and reusable resources keep their normal
locations outside the Activity. Results are Activity-specific review deliverables.

## Conversation and recording

The host MUST persist each received human instruction verbatim through typed chat
before dependent substantive work, independently of native-source availability.
It MUST distinguish human instructions, assistant replies, agent coordination and
legacy imported context. Generated summaries never replace original human messages.
Initial message IDs identify original records; original source identities/timestamps
are retained when observed and MUST NOT be invented. The runtime append timestamp
is the actual capture time. See the [conversation contract](activity-chat_conv.md).

The host MUST persist assistant reply text with truthful delivery status. A reply
written before transmission is prepared, not proven delivered; only actual observed
delivery permits delivered status. No background hook or automatic host interception
is claimed. Agents use the append API for coordination and cannot treat an agent
message or prepared reply as human authorization. Chat is required in layout 2 and
the single conversation record, including source-backed imports.

The host MUST NOT manually rewrite runtime state, log, chat, usage, checkpoints or
workflow metadata. Core operations own those records. Log entries are append-only,
UTC-dated meaningful actions/decisions/checks/failures; posting chat does not require
a duplicate log entry. The coordinator maintains summaries and declared outputs.

## Generation, naming and retention

- The coordinator MUST declare review outputs under results/ and verification
  evidence under evidence/ before assigning their creation. Runtime record supports
  explicit paths in these buckets and rejects overlapping destinations.
- Agents MUST put their scratch below their allocated work folder. The coordinator
  MUST put temporary requests/scripts below work/coordinator/; tests use work/test-work/.
- When supported, the coordinator MUST send requests in memory or through --request-stdin. Routine chat
  reads, status updates and successful commands MUST NOT generate permanent request
  and response files. Necessary failed-operation diagnostics remain attributable.
- The coordinator MUST consolidate meaningful verification into evidence/verification.md
  and retain detailed raw files only for reproducibility, failure investigation or
  an explicit requirement. It MUST preserve failures and their later resolution.
- Material document revisions MUST preserve exact predecessors under history/ with
  author/source, actual UTC date, reason, predecessor and dependent impact.
- Human file/folder names use lowercase words separated by hyphens, except README.md
  and exact machine-contract names. Numbered prefixes indicate actual reading order.
  UTC history names use YYYYMMDD_HHMMSS plus an unused sequence where needed.
- work-cleanup previews exact selected work paths and requires host confirmation of
  ended writers and retained evidence. It MUST NOT remove allocation manifests,
  results/evidence/history/system/run records or follow links. Closure does not
  silently delete unexplained material; the coordinator reconciles disposal first.

## Identity, lifecycle and state

Every Activity is one direct child of configured activities.location (default
.hai_env/activities). At most one is active and it uses 00000000_000000_active.
There is no global current pointer or alternate store fallback. State requires:

| Field | Meaning |
| --- | --- |
| activity_id | Unique stable UUID, unchanged by migration, rename or archival. |
| lifecycle | active or closed. |
| created_at | Actual Activity initialization UTC time. |
| closed_at | Null while active; actual UTC closure time. |
| outcome | Null while active; completed, cancelled or stopped when closed. |
| implementation_started_at | Null until first real implementation attempt; never reset. |
| steps | clarification, analysis, planning, implementation, verification, independently not_started/in_progress/completed/skipped. |
| activity_layout_version | 2 for the current layout; absent means legacy 1 only. |
| initial_message_id | Original instruction or explicitly imported legacy-context message ID, or null until supplied. |

Times use YYYY-MM-DDTHH:MM:SSZ. State and JSON records reject duplicate keys.
Lifecycle does not imply phase completion. Analysis alone can meet an objective;
implementation claims require the original start marker and appropriate checks.
Unsupported states are not silently repaired. Stores, record folders and canonical
artifacts must be contained nonlinked paths; hard-link aliases are rejected.

## Closure, archival and compatibility

Closure requires resolved workflow runs and ended known writers. It appends the
final report to README.md and preserves its predecessor in history/readme/.
Usage is refreshed under system/, and recording reconciles the unified chat with explicit coverage gaps and independent mandatory obligations. Closed folders use YYYYMMDD_HHMMSS_short-label, matching actual
UTC closure time; labels contain one to five lowercase alphanumeric words separated
by hyphens. Collisions use _02, _03, etc. All contained runs and records move with
the Activity. Durable references use stable IDs plus Activity-relative paths.

Existing layout-1 archives remain readable with their original state.json,
input.md, log.md and outcome.md; normal reads/startup never move them. An explicit
activity migrate-layout operation converts the selected current Activity by default,
preserving original bytes/provenance and reporting partial/conflicting operations.
Explicit allow_closed: true may migrate a specifically selected archive while a
separate work Activity is active. It preserves closure timestamps/outcome and the
original final-report bytes; retired agent material stays under durable history.
Other archives remain unchanged. Migration never labels a whole legacy input
artifact as a verified human message.
New create defaults to layout 2; explicit layout_version: 1 remains available for
compatibility callers and legacy regression fixtures. Legacy creation is not the
normal host flow. Canonical fields and original lifecycle timestamps survive.

Closed-record supplements append attributed evidence without reopening or rewriting
historical claims. New substantive work uses a new linked Activity. No commit,
publication, migration or Activity closure is inferred from a discussion alone.

## References

- [Artifact placement](artifact-placement_conv.md).
- [Conversation](activity-chat_conv.md), [invocations](agent-invocation_conv.md).
- [Workflow runs](workflow-run_conv.md), [usage](activity-usage_conv.md).
- [Chronicles](chronicles_conv.md), [runtime commands](../tools/runtime/README.md).
