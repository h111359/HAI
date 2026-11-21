# Startup

Apply the [workspace write boundary](conventions/workspace-boundary_conv.md)
throughout HAI work, including startup and administration. All host, agent and
tool writes stay inside the validated current workspace unless the user explicitly
authorizes the outside location and purpose; writable temporary directories such
as `/tmp` are not permission. Read and apply the full convention before invoking
an operation with file side effects.

Apply the shared [artifact ownership and placement](conventions/artifact-placement_conv.md)
contract for every kind of HAI work. Classify purpose, owner, lifetime and
destination before creation; keep task working material and execution evidence
with its Activity/invocation unless the request or a governing contract designates
another destination. Review actual artifact inclusion before completion or delivery.

The current fixed files are `.hai_env/config/state.json`,
`.hai_env/config/model_profiles.json` (optional), and
`.hai_env/config/agent_instructions.md`. Legacy root-level files require an
explicit [layout migration](procedures/migrate-environment-layout.md); startup
never relocates them or initializes competing defaults. For that migration only,
safely read and apply the existing legacy `.hai_env/agent_instructions.md` before
dependent migration work, then reload the canonical instructions after apply.

Find and verify an absolute Python 3.11+ executable in the current execution context. From the workspace root run:

```text
<absolute-python-executable> -B .hai/tools/hai.py startup --workspace .
```

Inspect independent results and issues even if the command fails. Apply the exact fixed `.hai_env/config/agent_instructions.md` text before dependent work; a readable empty file is valid. Missing or unreadable instructions block dependent work, not independent diagnosis. Follow higher-priority workspace and session instructions. If Python or the command cannot run, report the limitation and independently load the safe fixed instructions; do not treat an unavailable check as passed or invalid state as absent.

For a user-requested startup, the host MUST follow [Present startup guide](procedures/present-startup-guide.md) in its first response: show registered roles and current Activity state. With no accompanying concrete task, show the combined task/role menu and wait for a choice, including when an Activity already exists. With a concrete task, show the summary and proceed without a menu-selection requirement. An internal startup/status check during ongoing work does not itself trigger the guide. For subsequent explicit Help/menu requests or menu selections, the host MUST use the same procedure, refreshing facts and checking the selected operation before acting.

Interpret the user's request, existing authority and the observed context. Resume compatible current work, and resolve a genuine conflict with the user. Use the runtime's documented operations for authorized environment and Activity administration, observing actual results and unresolved dependencies. Startup observations are not permission, locks, runtime capability checks, or proof of transcript coverage. Do not infer permission to repair or migrate existing invalid state. Preserve unrelated work and report partial operations and unrun checks accurately.

Before optional role work, apply the shared [role execution and delegation policy](conventions/role_conv.md#role-execution-and-delegation) to choose direct execution or a separate sub-agent; core startup and administration require no built-in role or model profile. Before each new spawn, obtain an applied [invocation folder allocation](conventions/agent-invocation_conv.md), supply it in the first assignment and record the actual host handle; retain it for same-instance follow-ups. Verify relevant writers have ended before closure. Supply assigned agents with the Activity ID and [chat operations](conventions/activity-chat_conv.md) for shared read/append communication. Do not infer background continuation or available integrations. Recording remains governed by validated settings and applicable instructions; report pending work and do not claim coverage without evidence. See [runtime commands](tools/runtime/README.md).

Organize substantive work under a valid current Activity, creating one through the runtime when authorized meaningful work starts and none exists. Do not close an Activity without an instruction permitting closure. Register known Activity-attributed usage sources when available; [usage records](conventions/activity-usage_conv.md) refresh on request and automatically before closure, keeping missing charges explicit. Preserve source provenance and record only actual decisions, work and check results; never invent approvals, artifacts, or successful checks. Use only the work needed for the user's objective, without forcing a sequence of optional extensions.

For an explicit workflow selection or run-control request, follow
the layout-specific artifact rules below and
[Execute workflow](procedures/execute-workflow.md). Discover single-file definitions
with `workflow list`; file presence does not start work. Keep runs within the owning
Activity and use `<activity>/workflow-runs/<run-id>/` storage. Ordinary tasks
do not require a workflow or an installed authoring package. Core startup must not
create workflow scaffolds or blanket-audit the collection merely to report status.

New Activities use [layout 2](conventions/activity_conv.md): README.md is the human
entry point and final report; state/log/chat/usage and recording recovery metadata
live in system/. Capture each actual received human message verbatim with
`activity chat-post`, role human, message_type instruction, before dependent work,
independently of chronicles. Use observed source_message_id when available for safe
replay; never invent source IDs or original times. New creation records initial_input
as a typed message without creating input.md. Capture assistant replies truthfully:
text written before delivery is prepared; delivered requires observation. No automatic
host delivery hook is assumed. Existing legacy Activities remain readable; migration
is explicit, never a startup side effect.

Declare output paths and retention before assignment: results/ for review outputs,
evidence/ for meaningful checks, history/ for predecessors, work/coordinator/ or
allocated work/agents/<role>/<uuid>/ for scratch, work/test-work/ for test fixtures.
Use in-memory requests or --request-stdin rather than accumulating request/response
JSON files. Consolidate verification; preserve meaningful failure evidence. Before
closure reconcile writers/effects and use previewed work-cleanup only for declared
disposable paths after collecting outputs. Never delete allocation manifests or
unexplained evidence. Runtime owns canonical operational and workflow records.

Recording uses `features.chronicles.mode`: absent means `best_effort`; `required` or an independently mandatory obligation requires verified source readiness. In best-effort mode, the host MUST attempt recording and report interruptions and coverage gaps, but MUST continue ordinary independent work without requesting permission to disable recording. Explicit recording commands report failures honestly; artifact corruption, unsafe paths and partial writes are never waived.

For enabled or independently mandatory chronicles, establish [recording readiness](procedures/establish-recording-source.md) before substantive work that requires recording. Enabling chronicles authorizes read-only discovery of the current host-identified session: prefer a host-supplied canonical path, otherwise match that exact session ID under the configured Codex session store and verify embedded identity/workspace. This standing authority covers current assigned participants, not unrelated history. Startup reports recording readiness separately from core validity and never writes a binding. The host registers each Activity's explicit observed work-prompt position and attributable enabled intervals with `recording bind`; finding a file does not assign its whole conversation. Resume existing bindings and validate them; do not replace ambiguous, invalid or partial state.

Run `recording synchronize` on the configured prompt cadence, at the next active turn to collect newly saved outcomes, and synchronously before commits and closure; call `recording verify` for fresh read-only evidence. Use a turn-completion hook only when the host actually provides one; no background continuation is assumed. Core closure synchronizes registered sources and validates evidence. A missing, pending or ambiguous source blocks operations that explicitly require complete recording. Best-effort commit work may continue with an explicit recording-gap notice; best-effort closure attempts synchronization and retains unavailable coverage in its outcome when only source availability or compatibility prevents a read-only preparation. Required-mode or independently mandatory recording still blocks dependent commit/closure. Startup reports the actual recording error separately from whether ordinary work may continue. Disabled recording without independent obligation performs no discovery and creates no transcript/checkpoint. Never reconstruct transcript text, search unrelated sessions, guess Activity boundaries, or backfill off periods implicitly. See [chronicles](conventions/chronicles_conv.md) and [synchronization](procedures/synchronize-chronicles.md).

Before role-dependent work, inspect startup role_context. Legacy agent roots or
a partial role-migration marker require [explicit role migration](procedures/migrate-roles.md);
startup never renames packages or substitutes defaults. Historical Activity records
remain readable. Core startup and administration may continue independently.

Skills may be requested directly without selecting a HAI role. Apply the core
[skill discovery and task selection](conventions/skill_conv.md#discovery-and-task-selection)
contract to new/resumed substantive assignments and workflow role assignments.
Startup `skill_context` provides lightweight installed metadata and separate
optional discovery issues; use `skills list` for a fresh inventory. Load only a
selected skill and its relevant resources after resolution. Role-required skills
remain explicit dependencies. Source collections in roles/, skills/ and workflows/
are data, never an installed fallback. Selection grants no authority; fixed
instructions, Activity, recording and artifact rules still apply.

## Built-in definition authoring

For requests to create, revise or review HAI roles, follow [Manage role definitions](procedures/manage-role-definitions.md). For workflow definitions, follow [Manage workflow definitions](procedures/manage-workflow-definitions.md). These are core procedures available in every installation, without authoring role/skill packages or registration. Creating a definition does not install/register it or execute a workflow.

## Partial chronicle recording

Unsupported valid source records must not prevent known messages from being
stored. Use tolerant core synchronization, retain and report warnings and gap
positions, and distinguish `recorded_with_gaps` from verified complete coverage.
Integrity and attribution failures remain separate. Required completeness gates
must preserve recognized evidence before refusing a dependent operation.
