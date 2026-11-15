# Workflow solution specification — draft 0.4

Storage revision: the user now requires runs inside their owning Activity at
`<activity>/workflow-runs/<run-id>/`, without another Activity-ID level. Runs
move with the Activity on archival. Earlier drafts are preserved in the Activity
revision files; this storage decision supersedes their external-root proposal.

For section-by-section explanations, examples and review decisions, read the
[plain-language companion](02a-solution-reading-guide.md). This specification
retains the detailed design; the companion does not change its proposed behavior.

This is the proposed normative contract for version 1. Draft 0.3 records the
user's acceptance of one final result per attempt, returns to earlier steps and
per-step/total-run attempt limits. The remaining detailed contract is still under review. “MUST” describes proposed
implementation behavior, not a currently available capability. Requirements U1–U20
and review choices are in [requirements](01-requirements.md) and [review guide](00-review-guide.md).

## 1. Ownership and concepts

| Entity | Owner | Meaning |
| --- | --- | --- |
| Definition | Workflow-definition-manager, under user scope | Reusable single-file process. |
| Definition validation | Core tooling for structure; manager for meaning | Evidence about a file, not permission or readiness to execute. |
| Run | Core persistence, host coordination | One pinned execution inside exactly one Activity. |
| Step | Host assignment to registered agent | Instruction plus input/output/result contract. |
| Attempt | One execution of a step | Immutable identity, resolved inputs, produced files and accepted or rejected result. |
| Result | Agent proposes, host accepts | One workflow-defined completion label supported by its specified files. |
| Transition | Definition selects, core checks, host dispatches | Next step or terminal outcome after accepted completion. |
| Interruption | Host/runtime evidence | Missing prerequisite, process failure or uncertain external effect; not a fabricated business result. |

Agents retain their own rules, procedures and configuration. Host coordination
does not grant an agent orchestration rights. A workflow cannot override policy,
enable an integration, broaden task authority or close an Activity. Direct role
execution and separate invocations remain distinct; independent verification uses
an executor independent of the implementation author where current policy requires it.

## 2. Locations and identity

```text
.hai_env/workflows/
  customer-request.md                 # Whole reusable definition

<activity>/workflow-runs/<run-uuid>/
  definition.md                       # Exact pinned bytes
  state.json                          # Runtime-owned progress projection
  events.jsonl                        # Runtime-owned append-only transitions
  inputs/<input-name>[.<suffix>]      # Exact initial file/directory snapshots
  attempts/<step-id>/<attempt-0001>/
    assignment.json                   # Frozen assignment and input identities
    result.json                       # One accepted completion, runtime-owned
    rejection-0001.json                # Retained invalid submission, when needed
    <declared-output-artifacts>
```

Run metadata, snapshots and produced artifacts use the owning Activity's dedicated
workflow-runs subfolder, separate from its general files area. Each run is one
direct child named by its UUID; the containing Activity supplies ownership without
an additional Activity-ID directory. A configured Activity record store also holds
the runs belonging to those Activities.

Activity archival moves its run directories with it. The runtime resolves the owner
by stable Activity UUID and combines its current or archived path with the run UUID.
Closed owners make runs read-only. Closure checks their run records and verifies
writers have ended; there is no second lifecycle or global current-run pointer.
Missing or ambiguous owner identity is reported. Durable references identify the
Activity and run IDs or an Activity-relative path, rather than the reusable active
folder name. Copy/export and retention naturally include the runs with their owner.
Legacy external runs need explicit byte-preserving relocation, without an automatic
fallback or a split between old and new storage.

Workflow names, step IDs, input/output names, result names and terminal names use
`[a-z][a-z0-9]*(?:-[a-z0-9]+)*`, at most 64 characters. Names are unique within
their own namespaces and compared case-insensitively for filesystem collisions.
Workflow filename is `<name>.md`, lowercase, one direct child of workflows.
Run UUID is stable; repeat executions always get different UUIDs. Attempt numbering
is per step, monotonically increasing with at least four digits; never reuse a failed
or cancelled attempt directory. Source definition name + revision + SHA-256 identifies
the selected process. When a known predecessor or pinned run is in review scope,
matching revision with different bytes produces a warning and a distinct pinned
identity, never silent equivalence. Pure file validation does not scan unrelated
history to infer a predecessor.

The definition collection has no generated catalogue in version 1. `workflow list`
validates immediate `.md` entries and reports valid and invalid entries separately.
Global workflows and definition precedence are outside this version. The new
manager has a golden source package and an independently installed workspace copy.

## 3. Exact single-file definition format

UTF-8, LF or CRLF accepted; parse lines without changing original bytes or hashes.
No BOM. Required frontmatter between `---` lines, followed by one H1 and exactly
the H2 sections `Purpose`, `Inputs`, `Outcomes`, `Steps`, in that order:

```markdown
---
workflow_format: 1
name: example
revision: 1
entry: inspect
max_step_attempts: 3
max_run_attempts: 12
---
# Example

## Purpose
Explain when to choose this process and the intended outcome.

## Inputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| request | activity:input.md | markdown | Actual supplied request, with source attribution. |

## Outcomes
| Name | Meaning |
| --- | --- |
| assessed | Requested assessment delivered. |

## Steps
### inspect
#### Agent
business-analyst
#### Instruction
Analyze the supplied request and produce an assessment supported by evidence.
#### Inputs
| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| request | workflow:request | yes | markdown | Supplied request. |
#### Outputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| assessment | attempt:assessment.md | markdown | Findings, unknowns, source references and recommendation. |
#### Results
| Name | When | Outputs | Next |
| --- | --- | --- | --- |
| assessed | Assessment meets the requested scope and evidence criteria. | assessment | end:assessed |
```

Frontmatter is intentionally a restricted YAML scalar subset: exact six keys
shown; integer values use decimal digits and must be positive, except format must
equal 1; name/entry are bare identifiers. No quoting, aliases, tags, nested values,
comments, duplicate or unknown keys. This can be parsed deterministically with the
standard library without claiming full YAML support. No automatic YAML evaluation.
Revision is a positive document revision, not a product release version.

Each H3 under Steps is a step ID and has exactly the H4 sections `Agent`,
`Instruction`, `Inputs`, `Outputs`, `Results`, in that order. Agent contains one
bare canonical role name. Structural validation checks its syntax; registration,
configuration and capability are separate execution-readiness checks. Instruction is nonempty Markdown, allowing lists and
ordinary descriptive links, but no H1–H4 headings or code fences that imitate the
structural headings. A step may reference a role-owned procedure by path in its
instruction; that reference does not copy its implementation or create another role.

Each contract section contains exactly one pipe table with the headers shown.
Leading/trailing whitespace around cells is ignored. Cells contain nonempty
single-line literal text; no pipes, multiline cells, escaped pipes or executable
expressions. Source/Location/Name/Format/Required/Next are bare tokens, without
backticks or links. Instruction prose can carry the longer explanation.
Inputs tables may be header-only. Outputs and Results must each have at least
one row. Output names in Results are a comma-separated nonempty list of distinct
names from that step's Outputs table; order does not affect file acceptance.
Every declared output is used by at least one result. No implicit result, default
transition, wildcard, fall-through, directory scan or shell expansion is permitted.

Results are not restricted to success/failure: `approved`, `needs-clarification`,
`rejected`, `partially-supported` and domain-specific names are equally valid.
Every row supplies nonempty selection criteria, required evidence outputs and
exactly one Next value: `step:<id>` or `end:<outcome>`. Outcomes are declared in
the workflow Outcomes table, independently of result names. There is no fixed
number or vocabulary of business results/outcomes.

## 4. File contracts and bindings

| Position | Allowed reference | Resolution |
| --- | --- | --- |
| Workflow input Location | `workspace:<path>` | Existing authorized file or directory below workspace root. |
| Workflow input Location | `activity:<path>` | Existing file or directory below the owning Activity record. |
| Step input Source | `workflow:<input-name>` | Exact initial snapshot made at run start. |
| Step input Source | `incoming:<output-name>` | File named by the immediately preceding accepted result in this run. |
| Step output Location | `attempt:<path>` | Exact relative path under this attempt directory. |

Paths are literal portable relative paths using `/`. New artifact base names use
lowercase kebab-case by default, with the exact suffix or directory name specified
by the workflow author. There is no extension or format whitelist: `.xlsx`, `.png`,
`.zip`, datasets and other formats are permitted. Existing source spelling is
preserved. Format is a nonempty author-defined description of the expected
representation, not an engine enum or an executable validator. Reject absolute paths, traversal,
empty components, control characters, Windows reserved names, alternate streams,
escaping links/junctions and aliases. Validate resolved ancestors before creation
and recheck before acceptance. Never normalize an unsafe supplied path into validity.
Inputs cannot read Git metadata, secrets/config/profile stores or another Activity's
managed records; explicit user authority for an exception must be resolved outside
this format rather than inferred from a reference. Product input selection remains
subject to task authority and should be limited to the actual required files.
Outputs cannot use the runtime-reserved attempt-root names `assignment.json`,
`result.json` or `rejection-<number>.json`; reject any case/alias collision with those
files and with another declared output. Generated result metadata cannot substitute
for an agent's declared evidence artifact.

At start all workflow input artifacts must exist and meet the author-specified format and
expectations. Core snapshots files byte-for-byte and directories as relative-path
manifests plus their exact file contents, recording original locations and hashes. Initial snapshots are immutable: later scope changes
need a new run with new inputs. User answers obtained during a clarification step
are attributable attempt evidence, not silent edits of the initial request snapshot.

Each edge is checked against its own result's output list. Required `incoming:x`
must be present on every incoming edge to that target; optional sources may be
absent and are explicitly passed as absent. The entry step must not require an
incoming value. There is no “last known file” lookup across old attempts or other
runs. A consuming input must declare the same Format description as its producer output;
the author and manager ensure that the description and Expectations actually agree. Local input name can
differ from producer name; Source is the explicit binding. Identical names alone
do not pass files. The host translates these resolved bindings to the agent's
procedure-local inputs explicitly.

Assignment records identify input producer run/step/attempt/result, path and hash.
Agents treat predecessor artifacts as read-only. A file changing between assignment
and acceptance blocks completion. Products edited by the agent remain in their
canonical destinations; evidence reports list exact modified workspace paths,
before/after hashes where available, checks and outstanding effects. Workflow output
contracts in version 1 describe evidence files under attempts, not a new mechanism
for writing arbitrary product destinations. In particular a specification-update
receipt points to the specification manager's configured tree; no second tree is
created inside the run and no enablement is inferred.

Core validates existence, declared location, regular file/directory type, safe
ancestry and stable content hashes. It does not assume UTF-8, a file extension,
nonempty content, JSON object shape or a particular document format. Empty files,
JSON arrays/scalars and binary outputs are valid when the authored expectations
allow them. For a directory, record a sorted manifest of relative paths, entry
kinds and file hashes, including empty directories; reject links, special-device
entries and paths escaping that artifact. Recheck the whole manifest at acceptance.
Nested output declarations that overlap an output directory are rejected to avoid
ambiguous ownership and hashing.

The workflow author states the format checks in Expectation and the step instruction
and identifies the appropriate tool/role evidence. The assigned agent performs them;
the coordinator evaluates the actual check evidence. A parser or test can be used
when available and authorized, but the format cell cannot execute code. Unsupported
format-verification tools block a dependent acceptance rather than pretending a check
passed. These safety and evidence checks do not restrict the author to particular
formats. A plausible filename or matching hash alone does not establish quality.

## 5. Graph and result semantics

Exactly one declared entry. All steps and terminal outcomes must be reachable from
it. Every step must have a possible graph path to a terminal; this structural check
does not claim the result conditions will occur. Cycles and self-transitions are
allowed within finite run limits. Result labels are local to their step. No automatic
interpretation of `When` as Python, shell, JavaScript or a general expression language.

The agent proposes exactly one label in a structured completion submission. The
host checks that label's When criterion and output Expectations using file evidence
and actual tool/check results, and supplies an acceptance assessment to core. If
several criteria are true, the host must resolve the ambiguity from the definition
or user; row order is not priority. A revised definition needs a new run; the host
cannot invent precedence inside an existing run. Manager review should prevent
overlapping or uncovered business conditions before selection.

Core accepts only the active attempt, expected state revision, declared label,
all required evidence and host assessment. A runtime-owned `result.json` records
result label, accepted input/output paths+hashes, assessment, actual executor,
time and transition. The file list is derived from the pinned definition, not
arbitrary paths proposed by the agent. Additional scratch is retained but cannot
satisfy undeclared evidence. Unselected result files, if any, remain unaccepted.

Only acceptance permits the transition. The next dispatch occurs on a separate
host action, after refreshed role/config/authority checks. Last step acceptance
sets run status `finished` and its declared terminal outcome; never closes Activity.

If a step cannot write its failure evidence (crash, missing permissions, tool loss),
core records an execution interruption and blocks; it does not route a fabricated
failure result. An agent may produce a declared failure result when it really can
write and substantiate the required evidence. User-input waits keep the same
attempt waiting; a clarification is not automatically a failed result.

## 6. Run/attempt states, serialization and recovery

Run progress states are `ready`, `prepared`, `running`, `waiting`, `blocked`, `paused`,
`cancelling`, `cancelled`, `finished`. These administrative states do not limit the
arbitrary business result/outcome labels. State includes format version, run and
Activity UUIDs, definition name/revision/hash, creation/update timestamps, current
step and attempt, total attempt count, state revision, initial snapshots, latest
accepted transition, progress state, terminal outcome or null, block reason or null,
and actual executor identity/liveness evidence when available. Attempt lifecycle is
`allocated`, `running`, `waiting`, `blocked`, `accepted`, `cancelled`; block reasons
distinguish invalid output, missing authority, unavailable agent and uncertain effect.

At most one run per Activity holds execution ownership: prepared/running/waiting,
blocked with an unfinished allocated attempt, or cancellation pending. Allocation
reserves ownership before launch; there is no unowned gap between prepare-step and
record-execution. A run blocked before any allocation holds no writer reservation.
Pausing releases ownership
only after all its writers are verified stopped. A ready run has no active writer;
any number of ready/paused/finished runs may coexist. Ad hoc Activity work remains
possible but cannot modify locked inputs/artifacts or conflict with active writers.
Run records use existing core cooperative locking plus expected state revision,
artifact fingerprints and step attempt identity. This is not OS isolation.

| Trigger | Transition and retained evidence |
| --- | --- |
| Start | Create exclusive run UUID, definition/input snapshots; ready at entry. |
| Prepare | Check limits and prerequisites; allocate one attempt, reserve Activity execution ownership and become prepared. Repeating prepare while that attempt exists cannot allocate another. |
| Dispatch | From prepared, hand off the assignment and, for a spawn, existing invocation folder; running only after actual execution starts. |
| Need human answer | waiting, with actual question and attributable later response; no invented approval. |
| Valid completion | accepted attempt; next step ready or run finished with declared outcome. |
| Invalid completion | blocked with rejection evidence; same attempt may correct files and resubmit before acceptance. |
| Worker/tool failure | blocked with known partial effects; retry needs ended writer and effect reconciliation. |
| Pause | paused only after writer termination; otherwise retain blocking/cancellation state. |
| Resume | Check owning Activity, definition snapshot, inputs and pinned role evidence. Resume ready work or a known never-started prepared attempt. Previously started unaccepted work becomes blocked until explicit effect reconciliation and retry. |
| Cancel | cancelling while liveness unknown; cancelled only when relevant writers ended. Accepted effects remain. |
| Retry or explicit return to an earlier step | New attempt, never reuse accepted result paths; count against limits. |
| Limit exhausted | blocked reason attempt-limit; no automatic extra invocation or assumed terminal result. |

Both limits are required positive integers. max_step_attempts counts each allocated
attempt for that step, including failed launches; max_run_attempts counts all
allocated attempts. A resumed waiting attempt or identical completion retry does
not allocate/count again. Limits are frozen in the definition; exceeding them
requires a new run or future explicitly designed amendment, not a hidden override.

Runtime writes a numbered append-only event with operation ID, expected/new state
revision and enough transition data to rebuild progress, then updates its state
projection. Exclusive event sequence and expected revision prevent two hosts from
accepting the same attempt differently. Accepted output and result hashes are part
of the event. All files for acceptance must exist and be stable before that event.
On restart, matching event/state is normal; a valid committed event ahead of state
can rebuild the projection idempotently. A partial final event, unexplained file,
missing accepted result or hash conflict blocks further writes pending explicit
reconciliation. No blanket cleanup, truncation or automatic rollback.

Repeated identical completion for an already accepted attempt returns the retained
acceptance. Core checks for that matching retained acceptance **before** rejecting
the request's now-stale expected revision. It compares submitted label/assessment
and currently verified evidence against the accepted record, returns its original
operation identity/revision, and makes no writes. Changed label/files/assessment is
a conflict. For an unaccepted attempt the current expected revision is mandatory.
Prepared-attempt replay returns the same assignment only for the same step and
unchanged resolved inputs; a conflicting prepare or attempt owner is rejected.
Product side effects
before a crash cannot be inferred from a run event: inspect actual repository or
external state, reuse service idempotency support where available, and never blindly
repeat an unknown mutation. No exactly-once external execution guarantee is claimed.

Rework never changes an old accepted result; it produces new attempts. New input
hashes create new lineage; downstream work on the newly traversed path must be
executed again. Prior downstream evidence remains historical and is not current
acceptance for revised inputs. Initial definition bytes are pinned; role definitions
are referenced with observed hashes at dispatch. A changed role, configuration or
tool capability on resume requires compatibility review and recorded decision;
role snapshotting is evidence, not permission to execute an unregistered old role.

## 7. Proposed runtime interfaces

All commands below are future additions to `.hai/tools/hai.py`; JSON request files
stay within the workspace. Existing preview/`--apply`, provenance, errors, locks
and changed-files conventions apply. Reads never create records. Mutations need
valid core context and the sole current owning Activity. No operation spawns agents
inside Python; host dispatch remains explicit.

| Operation | Request/behavior |
| --- | --- |
| workflow list | No request; report immediate definitions, validity and issues. |
| workflow validate | `definition` workspace-relative path; parse/graph/contract evidence and diagnostics. No agent execution or product writes. |
| workflow start | `activity_id`, `definition`, provenance; preview resolved initial files/readiness; apply snapshots a new UUID run. |
| workflow show | `activity_id`, `run_id`; read state, history, current dependencies, including archived Activity. |
| workflow prepare-step | Activity/run IDs, `expected_revision`, provenance; preview assignment, apply exclusive attempt allocation. Host supplies actual handle and start evidence via record-execution. |
| workflow record-execution | Activity/run IDs, `step_id`, `attempt_id`, expected revision, `status`, actual executor/liveness evidence, provenance; handle known running/waiting/blocked lifecycle changes, never claim unobserved launch. |
| workflow complete-step | Activity/run IDs, `step_id`, `attempt_id`, expected revision, proposed `result`, host `assessment` and provenance; derive file set, validate and accept or retain rejection without advancing. |
| workflow pause/resume/cancel | IDs, revision, provenance and actual writer/effect evidence as needed; do not waive prerequisites or undo effects. |
| workflow retry-step | Activity/run IDs, `step_id`, `attempt_id`, expected revision, ended-writer/effect-resolution evidence, provenance; new allocation only if limits permit. |

Start/prepare may return unavailable prerequisites separately from definition
validity. Core `workflow validate` structural results are `valid` or `invalid`;
semantic review/readiness are explicitly `not_checked` unless separately assessed.
The manager returns semantic findings with actual scope. No “valid” file implies
the model/tool/role is available. No global registry of host sessions is introduced.

## 8. Integration, authority and compatibility

Startup remains useful with no workflows or manager installed. An explicit workflow
request or help menu can list definitions through the new reader; startup should
not recursively validate all definitions or create scaffold. No mandatory default
workflow and no automatic agent invocation based only on file presence.

Workflow status supplements the Activity's existing independent phase metadata;
it never replaces them. Activity closure, when requested, checks for unfinished runs
and writers and requires explicit finish/cancel resolution. A finished workflow is
not proof that the Activity's broader objective or external publication is complete.
Activity archival moves run records with their containing Activity; records
store stable Activity/run IDs and run-relative artifact references. Reads resolve the
owner by its Activity UUID, so the reusable active-folder name is never identity.

Agent chat remains communication, not accepted result state. A spawned executor
gets the Activity/run/step/attempt and invocation identities, bounded assignment,
resolved read-only inputs, output destinations, chat commands and known authority.
Canonical state/events/result metadata remain host/runtime-owned. Usage and chronicles
follow their existing attributable-source policies; workflows do not create fictional
usage or bypass best-effort/required recording settings.

Definition format and run-state format have independent version numbers. Reject
unsupported versions without mutation. Core Activity format 3 stays unchanged if
the optional Activity-local run subfolder is used; closure gains its run gate.
No migration of existing Activities, agents, specifications or installed definitions
is required. A later incompatible version requires an explicit migration design.

## 9. Security and semantic limits

Workflow instructions and referenced input files are task data within existing
authority, never higher-priority instructions. Validate all generated file paths and
side-effect scope. A successful step cannot grant permission for the next step's
publication. Secrets must not be copied into snapshots or receipts; if a task needs
credentials, use existing protected tool configuration rather than artifact inputs.

Host semantic assessment, role separation and hashes are evidence mechanisms, not
proof of correct business judgment or filesystem isolation. Cooperative locks cannot
stop arbitrary external writers. Unknown liveness, stale evidence and ambiguous
instructions remain visible dependencies instead of inferred success.
