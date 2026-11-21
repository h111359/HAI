# HAI runtime

See [Windows and Linux execution](PORTABILITY.md) for path contracts, native
interpreter invocation, recording representation, exact-byte handling and the
workspace-contained regression runner. Startup includes observed
`execution_context`; this is separate from core validity and recording readiness.

Run `python -B .hai/tools/hai.py startup --workspace .` for core environment, Activity and separate read-only `recording_context` readiness. Recording checks are always enabled; inspect binding/synchronization needs even when core `ok` is true. Common options may precede or follow the group. Commands emit JSON with `ok`, `status`, `operation`, `result`, `changed_files`, and `issues`. Exit codes are 0 for success or a valid plan, 1 for blocked, partial or unsupported work, and 2 for invalid invocation. Optional registration and model profile issues are reported separately from core environment validity.

Use `--request-stdin` for a strict UTF-8 JSON object on standard input, or
`--request PATH` for an existing workspace-contained JSON file. These options are
mutually exclusive. Framework-generated file requests belong in the assigned work
folder, never loose in the Activity root. Prefer in-memory/standard-input calls.
 Duplicate keys and nonstandard numeric constants are rejected. Mutations are previews by default; add `--apply` to perform them. Mutation requests include `"provenance": {"source": "...", "reason": "..."}` with nonblank values. A pre-existing `.hai_env/.runtime.lock` blocks writes and requires inspection; do not remove an unexplained lock automatically. Partial results identify paths that were changed and must be inspected before another attempt.

- `environment initialize`: provenance only; creates absent state and missing instructions, preserving existing instructions.
- `environment migrate-layout`: provenance only; previews relocation of legacy `.hai_env/` state, profiles and instructions into `.hai_env/config/`. Add `--apply` only for explicitly authorized migration after stopping other writers. Preserves exact bytes and optional profile absence; retains recovery copies and a migration manifest. Mixed, conflicting or incomplete layouts require explicit reconciliation, never automatic overwrite or retry. See [migration procedure](../../procedures/migrate-environment-layout.md).
- `environment configure`: `changes` accepts `activities.location`; changing a location does not move content. Recording is always enabled and has no mode/cadence controls.
- `environment migrate-specification`: provenance only; previews or executes the scoped format-2 migration using its existing backup and candidate safeguards.
- `profiles check` reads optional profiles. `profiles configure` takes `changes` naming `light`, `standard`, or `advanced`; all three model IDs must be present after the update. This does not establish host model availability.
- `configuration read` takes `role`. `configuration update` takes `role`, provenance and `changes` keyed by names declared in that installed role's contract.

For example, preview `environment configure` with `{"provenance":{"source":"user request","reason":"choose Activity store"},"changes":{"activities.location":".hai_env/records"}}` through --request-stdin. Add --apply only for the authorized change.

Workflow modules provide Activity, package, recording and host operations. A host capability check reports availability; the runtime does not install dependencies or download packages implicitly.

## Role packages and migration

`roles` is the package command group; `packages` remains its neutral equivalent.
Use `roles audit`, `roles validate`, `roles install`, `roles register` and `roles resolve` with the package operation contracts below.
The former agents command group is not an alias.

`roles migrate` previews the explicit name migration; its request contains
provenance. Apply requires the current expected_snapshot plus writers_ended:true.
It converts legacy package roots, ROLE.md entries, role contracts and reusable
workflow definitions, while retaining originals under the current Activity history
and a status marker at .hai_env/config/role-migration.json. Source and installed
packages are converted independently; historical runs/manifests and saved values
retain their bytes. Mixed or partial layouts require explicit reconciliation.
See [migration procedure](../../procedures/migrate-roles.md).

Startup reports role_context independently of core validity. Legacy names block
role-dependent work but allow independent core administration. New contracts use
contract_format_version 3, new configurable workflows workflow_format 3, and invocation
manifests version 2; these are separate formats, not a release version.

## Skills and role composition

`skills validate` takes definition, a contained SKILL.md path. Native skills keep
free-form task instructions; HAI does not impose ROLE.md headings, role model
metadata or empty configuration contracts on them. `skills list` inspects installed
skills; `skills resolve` takes name and resolves only .hai_env/skills/<name>/SKILL.md.
It reports missing capabilities without falling back to root source collections.

`skills install` takes source, name and provenance, with optional replace and an
exact reviewed_differences list for a replacement. Preview is read-only; apply
stages/validates the complete local package, rechecks inputs and preserves the old
installed package. Installing a skill does not invoke it or authorize task effects.

Roles declare available skills through metadata.hai-skills. Their definitions keep
responsibilities, limits and any genuinely role-specific resources. Procedures and
configuration contracts are optional when unnecessary; owner settings still have
one authoritative contract/location. Direct skill use does not adopt its former
role, and workflow assignments leave skill selection to the assigned role.

`skills migrate` is the explicit candidate-based package migration for existing
source/installed role snapshots. Inspect the preview and exact candidate/target
identities, supply its expected preview and ended-writer evidence for apply, and
retain the Activity-owned recovery copies and migration marker. Partial or
incompatible states require inspected recovery rather than automatic merging.
See the [skill tools](../skills/README.md) for supported validation and boundaries.

## Workflow commands

Use `<absolute-python> -B .hai/tools/hai.py workflow <operation> --workspace .`
with `--request-stdin` or a workspace-contained request. Preview is the default;
`--apply` performs mutations under the runtime lock. Pure definition validation
requires no optional role, skill, model or output configuration. A valid file does
not authorize execution or prove semantic quality.

| Operation | Request fields | Behavior |
| --- | --- | --- |
| `list` | None | Installed Markdown definitions in .hai_env/workflows, with per-file structural issues; no run starts. |
| `validate` | `definition` | Validate selected workspace-relative source/template/installed file structurally. |
| `install` | `definition`, optional `locations`, `expected_installed_sha256`, `provenance` | Format-3 installation preview returns each location purpose/contents; apply requires actual human choices. Reuse/update preserves selected bases. |
| `show` | `activity_id`, `run_id` | Inspect verified retained evidence, including closed Activities; never repair storage. |
| `start` | `activity_id`, `definition`, `provenance` | Pin installed definition and immutable initial snapshots. Format 3 requires valid separate settings and reserves the Activity slot from start; no worker launches. |
| `prepare-step` | Common fields and readiness below | Check exact accepted inputs, safe destinations and limits; allocate one numbered assignment. Replay does not allocate again. |
| `record-execution` | Common, `step_id`, `attempt_id`, `status`, `executor`, `details` | Record observed running/waiting/blocked work; does not start it. |
| `complete-step` | Common, `step_id`, `attempt_id`, `result`, `assessment`, `executor`, optional `human_approval` | Validate selected result, inputs, outputs and ended writers; stage accepted copies and record one transition, or preserve rejection/partial evidence. |
| `pause`, `cancel` | Common, `executor` when present | Require actual writer status; cancellation does not undo product effects. |
| `resume` | Common, readiness | Recheck a paused never-started assignment; started work needs effect reconciliation. |
| `retry-step` | Common, `step_id`, `attempt_id`, `executor`, `effect_resolution`, readiness | Reconcile actual stopped attempt effects and allocate a fresh bounded execution. |

Common run-mutation fields are `activity_id`, `run_id`, integer
`expected_revision` from show, and provenance with nonblank source/reason. Install
is environment configuration, so takes no Activity ID. Only the sole current
owning Activity can mutate runs. Read operations reject --apply.

For installation, first preview `{"definition":"<selected-workflow-definition>.md"}`.
Present returned questions to the human. Apply with their actual choices:

```json
{
  "definition": "<selected-workflow-definition>.md",
  "locations": {"handoffs": "<human-chosen-base>", "completion": "<human-chosen-base>"},
  "provenance": {"source": "actual human location choices", "reason": "authorized installation"}
}
```

Placeholders above are not defaults. Locations are workspace-root-relative bases;
outputs add a run UUID directory and authored step/execution filename. Identical
shared bases are allowed; nested/case-aliased/protected/escaping or linked bases
block. A safe dedicated .hai_env/workflow-outputs base can be chosen; config,
installed collections, source roots and Activity storage cannot be outputs.
Settings live once in `.hai_env/config/workflows/<name>.json`, separate from the
reusable definition. A compatible definition update requires inspected
`expected_installed_sha256`, preserves chosen values and saves exact predecessor
bytes. Changed location contracts or partial installations stop without repair.
Installation starts no run. Missing/unsafe settings block the workflow, not core startup.

Readiness contains actual `runtime` model/effort support, an `authority` reference,
and `prerequisite_assessment` with `accepted: true`, `author`, `evidence`. Runtime
checks registered role, its available skill dependencies, optional owned configuration
contract and model profile; missing capability blocks affected assignment. Roles
choose skills. Workflow selection grants no further permission or automatic spawn.
An output `assessment` has the same accepted/author/evidence fields; the host
substantantiates the authored result condition and actual artifact quality.

An executor names its actual host `handle`, `mode` direct/spawned, Boolean
`writers_ended` and `evidence`. Spawned mode also requires an existing allocated
`invocation_id` for the owning Activity/role. Complete requires observed ended
writers. Host statements are not independently authenticated or an OS sandbox.

Format-3 assignments expose `execution_number`, exact output `path`, input retained
`path` relative to the Activity run, `configured_path`, producing `acceptance_key`,
`producer_step`, `producer_result`, `output_name` and content evidence. Initial
inputs are pinned snapshots. Required accepted sources use step/result/output;
`feedback:<output>` is explicitly historical immediate predecessor feedback:
its identity/content subtree is retained while separately declared accepted
requirements/design/approval continue to enforce live freshness. Never guess input
paths from filenames. Superseded, unaccepted, missing or changed required handoffs block.

Human-gated results require a real typed received human instruction after checkpoint
preparation and a host semantic attestation bound to the assignment. Natural human
approval in the presented context is sufficient; the human need not echo a token.
`human_approval` has exactly:

```json
{
  "message_id": "<actual recorded received human instruction UUID>",
  "message_sha256": "<SHA-256 of canonical complete message JSON>",
  "checkpoint_sha256": "<assignment checkpoint_sha256>",
  "accepted": true,
  "author": "<actual host identity>",
  "evidence": "<observed approval in this checkpoint context>"
}
```

Canonical message JSON uses ensure_ascii=true, sorted keys and compact comma/colon
separators, UTF-8, without newline (workflow_lineage.canonical). Runtime retains
exact message/hash and verifies typed role, received delivery, sequence and challenge.
An arbitrary approval evidence string or agent coordination record is insufficient.
This verifies host-attributed records and semantic attestation, not independent
human authentication. Source-backed recording validation remains its own contract.
Material scope/design changes invalidate stale approval. QA pass and human acceptance
are distinct required sources before Backlog-manager completion; updating the
canonical backlog still requires its owner's actual authority.

Runs retain definition, pinned configuration, initial snapshots, assignments,
accepted copies, input lineage, events and state below the owning Activity's
workflow-runs/<run-uuid>/. Configured handoffs are checked before dependent work;
internal accepted bytes/hashes remain authoritative and inspectable after archival
even when configured copies are unavailable. Product outputs retain their existing
owners. Formats 2 and 3 do not materialize files under stable final names.
Workflow completion never closes the Activity.

Format-1/2 historical definitions and run-format-1 evidence retain their original
interpretation and bytes. Format 3 creates run-format 2 and assignment-format 3;
new semantics never reinterpret an older run. Initial/accepted snapshots and event
hashes are immutable. Conflicting/truncated/uncommitted staging blocks and reports
retained changed paths without automatic rollback or repair. Identical accepted
completion replay returns the recorded result before the stale revision guard;
conflicting result/assessment/approval does not advance again. Per-step and run
limits remain pinned and retries never overwrite earlier accepted attempts.
Use `**/workflow-runs/** -text` when versioning evidence to prevent line-ending
conversion. Resolve archived evidence using stable Activity/run IDs, not cached
active-folder absolute paths. Optional workflow absence does not block ordinary work.

### Format-4 workflow files

`workflow start` accepts an optional `paths` object for a format-4 definition.
Send this example through `--request-stdin` with the actual current Activity
ID and provenance.

```json
{
  "activity_id": "<current Activity UUID>",
  "definition": ".hai_env/workflows/change-assessment.md",
  "paths": {
    "request": "activity:work/request.md",
    "assessment": "activity:results/assessment.md"
  },
  "provenance": {"source": "user request", "reason": "Assess the supplied proposal"}
}
```

Preview first. A `needs_input` response returns the missing file paths and their
expectations without creating a run. The apply operation pins the paths in
`bindings.json` and snapshots input bytes. `workflow install` for format 4
requires no `locations` because path selection happens at launch.

`workflow show` adds `files` with the resolved paths, file states and accepted
versions. Assignment output `path` is relative to the run directory. Write to
that staging path. The runtime materializes intermediates at acceptance and
delivers final files for the accepted outcome. When status is `publishing`,
`workflow publish` accepts `activity_id`, `run_id`, `expected_revision`,
and `provenance`. Apply to finish the committed pending plan after inspecting
conflicts. Startup and Activity status list unfinished runs without dispatching
anything. Formats 2 and 3 keep their existing path and run semantics.

## Activity layout and conversation

New `activity create` defaults to layout 2: `README.md` and
`system/state.json`, `system/log.md`, `system/chat.jsonl`. `initial_input` is
preserved exactly as a typed human message; state references its message ID.
Optional `summary` supplies a human objective for README without replacing original
content. Explicit `layout_version: 1` is retained for compatibility; startup/reads
never migrate old records. Environment state format remains 3.

- `activity chat-post` accepts optional `role` (human/assistant/agent/system),
  `message_type` (instruction/reply/coordination/legacy-input), `source_message_id`
  and `delivery_status` (received/prepared/delivered) for layout 2. Agent defaults
  remain coordination. Assistant defaults to prepared, never claimed delivered.
  Stable source-ID replay acknowledges identical content without appending; changed
  content conflicts. Human text is not truncated to the legacy 64KiB limit.
- `activity record` uses explicit `artifacts` names under results/ or evidence/,
  or README.md. Canonical analysis.md/plan.md/etc names resolve under results/.
  Overlapping destinations are rejected before writes. Revisions go to history/.
  `input_append` is legacy-only: post original human messages through typed chat.
- `activity close` retains the existing request fields but layout 2 appends the
  final outcome/recording report to README.md, preserving its predecessor under
  history/readme/. It creates no outcome.md. State/log/usage are under system/.
- `activity migrate-layout` takes selected `activity_id`, provenance and optional
  `summary` and `allow_closed` Boolean (default false). Preview is read-only; apply explicitly converts the current legacy
  Activity, preserving original state/input and context provenance, existing IDs,
  timestamps and accepted evidence. Unknown/mixed/partial destinations block.
  Stop all writers before migration and hand off new invocation paths afterward.
  Closed archives are never automatically changed. Explicit allow_closed: true
  permits only the selected archive while a separate work Activity is active;
  closure identity/timestamps/outcome remain unchanged and exact prior outcome
  content becomes the README final report. Retired agent work is durable history,
  rather than ignored disposable work. Other archives remain untouched.
- `activity work-cleanup` takes current `activity_id`, provenance, exact
  Activity-relative `paths` under work/, and actual `writers_ended: true`,
  `evidence_retained: true` host attestations. Preview lists the scope. Apply removes
  only the selected declared disposable work, refusing links, overlaps and
  invocation manifests. It never cleans results/evidence/history/system/run data.
  Close does not silently discard unexplained work or uncertain failures.

Requests to public APIs can run in memory; CLI --request-stdin avoids disposable
request files. The coordinator consolidates verification under evidence/ and keeps
only meaningful detailed proof. Runtime roles and the shared Activity convention
specify output owners and retention. README navigation derives from existing paths.

Host instructions capture received human messages before dependent work regardless
of chronicles, and record assistant content with truthful delivery status. This is
an explicit host integration protocol, not a claim of an unavailable automatic UI
hook or authentication. Always-enabled reconciliation checks actual saved-source coverage into the same chat.

## Activity and package operations

Requests are JSON objects. All applied Activity and package mutations require valid current core state and readable mandatory instructions. For example, `python -B .hai/tools/hai.py activity discover --workspace .` reads the current Activity; add `--request request.json` where fields are listed below. Every mutation requires the provenance object described above.

- `activity discover` takes `{}`. `activity show` takes `activity_id`.
- `activity create --apply` initializes `usage.json` and attempts to capture published model rates. An optional verified `pricing` snapshot supplied by the host overrides the lookup. Recording bind/synchronization and Activity closure refresh usage automatically.
- `activity usage-update` takes `activity_id`, provenance and optional `sources`, `pricing` and `reported_spend`. It previews by default. `--apply` refreshes assigned ranges into Activity-local `usage.json`. `activity usage-read` reads the retained snapshot by Activity ID, including archives. Unknown data is marked unavailable or stale. See [source attribution, counters and estimates](../../conventions/activity-usage_conv.md).

When a result includes `user_notice`, its `message` explains the outcome and
`action_owner` identifies who acts next (`user`, `host`, or `none`). Apply the
[user communication convention](../../conventions/user-communication_conv.md) to
every result shown to the user, including operations that only return diagnostics.
- `activity invocation-allocate` takes `activity_id`, `role` and provenance. Preview creates nothing (`allocated: false`); `--apply` exclusively creates `work/agents/<role>/<uuid>/invocation.json` in layout 2 (legacy Activities keep files/agent-invocations/<uuid>/invocation.json) below the current Activity and returns its existing folder (`allocated: true`), stable IDs, Activity-relative suffix and metadata. Closed/stale IDs, collisions and unsafe paths are rejected. Partial results retain and name changed paths. See [allocation and actual host handoff](../../conventions/agent-invocation_conv.md); the runtime does not spawn agents.
- `activity chat-read` takes `activity_id`, optional nonnegative integer `after_sequence` (default `0`) and optional integer `limit` (`1..1000`, default `100`). Returns a page with `messages`, `total_messages`, `next_after_sequence` and `has_more`; reads closed Activities too. Omit `--apply` for reads. `activity chat-post` takes `activity_id`, `author`, `text` and provenance. It previews by default; `--apply` appends to the current Activity's `chat.jsonl` under the runtime lock. No edit/delete action exists. See [chat format and participation](../../conventions/activity-chat_conv.md), including attribution and filesystem-access limits.
- `activity create` takes initial_input and provenance. `activity record` takes activity_id, optional steps/implementation_start/artifacts/input_append, log and provenance. `activity close` takes activity_id, outcome, archive_label, outcome_text and provenance. Layout-2 closure always reconciles chat; optional recording_requirement must keep enabled:true and can declare an independent mandatory obligation. Legacy external recording_proof/recording_paths cannot bypass unified verification. Available recognized messages are saved before reporting completeness or unresolved-boundary blockers. Legacy layout-1 external proof remains historical compatibility only. `activity supplement` appends attributed evidence to a closed record without reopening it. Actual partial paths are retained on failures.
- `packages validate` takes `definition`; `packages resolve` takes `definition` and `runtime`, a capability snapshot shaped as `{"models":{"model-id":["high"]}}`. `packages audit` takes `{}`. `packages install` takes workspace-relative `source`, `name`, provenance, and optional Boolean `replace` and `register`. Replacement additionally requires the exact `reviewed_differences` list returned by a preview; the previous package is retained as a backup. Registration may require a separate reconciliation after replacement. `packages register` takes `name` and provenance. Remote acquisition is unsupported. Safe no-overwrite package and Activity moves require an available native atomic rename primitive. Implementations cover Linux, Windows and macOS; only Linux has been tested here.
- `recording status` takes `{}` and reports the configured flag, threshold, and available evidence. `recording schedule` takes `occurrence_ids`, optional `covered_ids`, optional positive integer `threshold`, and optional `last_dispatched_count` for the previously dispatched observed count. It reports gaps and whether dispatch is due; it does not persist a checkpoint or start a background task. `recording assess-closure` accepts the structured request defined by the recording gate helper. The recorder consumes explicit assignments; bounded current-session discovery/binding is documented below.
- `host check` takes `model`, `effort`, and caller-supplied `models` mapping each model ID to an array of supported efforts. It reports whether that evidence contains the pair. The runtime does not discover host capabilities or invoke a host agent.

## Activity chat example

Save a UTF-8 workspace request such as `chat-post.json`:

```json
{
  "activity_id": "<current stable Activity UUID>",
  "author": "software-developer",
  "text": "The implementation is ready for the assigned verification work.",
  "provenance": {"source": "assigned developer", "reason": "handoff"}
}
```

Preview with `python -B .hai/tools/hai.py activity chat-post --workspace . --request chat-post.json`;
append by adding `--apply`. To read, use a separate request containing only
`{"activity_id":"<same UUID>"}` with `activity chat-read`. For later pages, include
the returned `next_after_sequence` as `after_sequence`. These examples do not assign
an agent, authenticate an author or imply the described implementation is complete.

## Invocation allocation example

Save a workspace-contained JSON request, for example `invocation-request.json`:

```json
{
  "activity_id": "<current stable Activity UUID>",
  "role": "software-developer",
  "provenance": {"source": "authorized host assignment", "reason": "allocate before a new spawn"}
}
```

Preview with `python -B .hai/tools/hai.py activity invocation-allocate --workspace . --request invocation-request.json`.
Add `--apply` to allocate. Dispatch only after successful applied readback, passing
the returned `path`, `activity_relative_path`, `activity_id` and `invocation_id` in
the first assignment. Record the actual returned host handle and observed launch
status through `activity record`; the manifest is not launch evidence.

Same-live-instance follow-ups keep the allocation; every new spawn attempt uses a
new one. Failed or uncertain launches retain material. Host closure waits for
verified ended writers; allocation locks do not stop later filesystem writes.
There is no new global registry, cleanup command or security sandbox.

Run `python -B -m unittest discover -s .hai/tools/runtime/tests -p 'test_invocations.py'`
for allocation, CLI, concurrency, unsafe-path, partial-failure and archive fixtures.
Separately observe real host launches receiving usable distinct folders and writing
independent files; fixture success alone does not prove host handoff. Controlled
verification Activities may be used so product work is not closed for a test.

## Chat verification

Run `python -B -m unittest discover -s .hai/tools/runtime/tests -p 'test_chat.py'`
for isolated fixtures covering shared authorship, exact append preservation,
preview/read behavior, CLI requests, pagination, malformed history, unsafe links,
lock contention, partial writes and archive/new-Activity separation. Tests do not
invoke agents or establish OS-level immutability. Report actual platform and skips.

## Activity usage example

Save a workspace-contained JSON request with an explicitly authorized source:

```json
{
  "activity_id": "<current stable Activity UUID>",
  "sources": [
    {"path": "/explicit/saved-session.jsonl", "session_id": "<original source session ID>", "start_position": 42}
  ],
  "provenance": {"source": "host Activity assignment", "reason": "refresh requested usage"}
}
```

Run `python -B .hai/tools/hai.py activity usage-update --workspace . --request usage-request.json`
to preview and add `--apply` to persist. Later requests need only `activity_id` and
provenance to refresh the same bindings. Position 42 is an example, not a default;
the host supplies actual Activity attribution and does not scan unrelated sessions.
`end_position` is optional for a fixed inclusive cutoff; otherwise the source is
read through its latest complete saved record.

Optional pricing is a rate snapshot, not a framework default:

```json
{
  "rates": {
    "example-model": {
      "input_credits_per_million": "10",
      "cached_input_credits_per_million": "1",
      "output_credits_per_million": "20"
    }
  },
  "source": "Explicit example rate card; these are not current prices",
  "captured_at": "2026-11-06T00:00:00Z"
}
```

Pass that object as `pricing` only when actual selected rates and provenance are
available. Reports and configuration cover tokens and credits only.
No API keys, account credentials, billing calls or network access are used.

Run `python -B -m unittest discover -s .hai/tools/runtime/tests -p 'test_usage.py'`
for cumulative/interval accounting, model rates, reported-spend freshness, malformed
sources, idempotent totals, unavailable data, optimistic/partial persistence, CLI,
archive reads and automatic pre-closure refresh. These checks do not authenticate
host billing evidence or prove completeness of all related sessions.

## Always-enabled conversation recording

New layout-2 Activities have one authoritative conversation: system/chat.jsonl. Applied chat-post stores the posted message and checks registered sources for missing saved messages. Every turn must also run recording synchronize --apply; startup is read-only and reports the action needed. There is no recording enable/disable switch or prompt threshold. Bookkeeping lives in system/recording.json without repeated message bodies.

- `recording discover`: read-only current-host session resolution using an explicit canonical source path or exact session filename under the configured host session store. Never searches unrelated conversation text.
- `recording bind`: activity_id, authoritative session_id/source_path/representation, observed start_position and provenance. The Activity range is continuously recorded; enabled_intervals is unnecessary for unified binding. Preview without --apply; applied binding is durable before imports. It never infers the first work prompt.
- `recording synchronize`: activity_id, provenance, optional explicitly assigned sources and optional independently attributable mandatory flag. Preview returns counts/warnings, not reserved message IDs. Apply appends missing messages and preserves existing bytes. Every retained occurrence is rechecked, including earlier gaps.
- `recording verify`: activity_id; read-only missing-message, retained-reference and current-source checks. needs_synchronization requires an applied synchronization. recorded_with_gaps never means complete coverage.
- `recording migrate`: activity_id and provenance. Explicitly previews/applies migration of the current layout-2 legacy transcript ledger. Every proven indexed message is imported even if the native source is unavailable. Exact predecessors, including old repair history and settings, go to history/recording/before-unified-v1/. Existing chat is an exact prefix. Publication/retirement are resumable; no guessed Markdown parsing or unverified deletion.
- `recording status` reports always-enabled policy. `recording adapters` lists reviewed source adapters. Historical layout-1 recording/proof code remains for compatibility, not an optional current recorder.

Visible assistant commentary/progress is included; internal analysis/tool plumbing is excluded. Imports retain source-qualified identities and source timestamps/positions separately from capture time/sequence. Repeated equal text is never deduplicated by text. Source-less older posts remain unchanged; overlapping imported source occurrences may coexist rather than guessing their identity. Prepared assistant messages remain prepared; delivered native replies are captured only after saved source evidence exists. No host delivery hook or background execution is assumed.

Unavailable sources and unsupported valid records produce coverage warnings while recognized messages are stored. Integrity errors retain actual partial paths. Closure flushes messages and seals source assignments; independent mandatory completeness obligations and unresolved registered-source end boundaries can prevent archival after supported messages are retained. See [recording contract](../../conventions/chronicles_conv.md).

Installed skill discovery reads entry-point frontmatter only, returning each
candidate's name, description and definition path. Startup exposes this as
`skill_context` with status/issues separate from core validity. `skills list`
refreshes the same inventory, preserving valid candidates alongside malformed
entry issues. A missing/empty collection is available with no entries. Metadata
is not execution readiness: `skills resolve` still validates the full selected
entry and any required settings. Supporting resources/scripts are never loaded
by discovery. Headers without valid delimiters or exceeding 64 KiB are reported.
Follow the core skill convention for selection and refresh rules.

Core deployment requires only .hai/ and initialized .hai_env/. Package sources
and workflow definitions outside them must be explicitly supplied. Role/skill
installation accepts optional source_mappings, for example
{"selected/peer-role": ".hai_env/roles/peer-role"}; no root library is inferred.
Source role dependencies always use installed skills. Required dependencies must
be installed before installing or validating their dependent role. roles migrate
handles internal legacy paths by default; historical library conversion needs
explicit legacy_source: "hai_agents_library". Legacy capability retirement needs
explicit legacy_source: "hai_roles_library" alongside retire_legacy_source.
Historical markers/recovery evidence retain their recorded interpretation.
