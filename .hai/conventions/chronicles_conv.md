# Chronicles

Core owns source synchronization, exact transcript segments, checkpoints and fresh coverage verification. The host supplies the stable Activity, authorized source identity, exact assignment ranges, enablement intervals and attributable provenance. The separate read-only current-session resolver can locate an existing source under the standing enabled-recording policy; the recorder itself consumes explicit bindings and never guesses attribution. The host serializes recording and Activity writers and resolves ambiguous or overlapping assignments. No separate manager, agent profile or library package is required.

## Availability policy

`features.chronicles.mode` accepts `best_effort` (default, including existing states without the field) or `required`. The host MUST attempt enabled recording and disclose actual interruptions and coverage gaps. In best-effort mode the host MUST continue independent ordinary work through source-format or source-availability interruptions without silently disabling recording. Explicit recording commands MUST retain their actual blocked/partial results; they MUST NOT report unavailable coverage as verified. Required mode and independently mandatory obligations block operations that depend on complete recording.

Activity closure MUST attempt synchronization. A best-effort source interruption detected during read-only preparation MAY produce an `unavailable` recording outcome with explicit gap details while preserving existing evidence. Retained-artifact tampering, invalid ledgers or attribution, unsafe paths, partial writes and uncertain writers MUST NOT be downgraded by this policy. The host MUST NOT bypass an independently mandatory requirement by selecting best-effort mode. An unavailable original source limits fresh source verification; it does not by itself establish that the retained transcript was changed.

## Early source readiness

Enabling chronicles authorizes bounded read-only discovery of the current host-identified session and assigned participants. Prefer `CODEX_THREAD_ID` as current execution identity, falling back to `CODEX_SESSION_ID`; an inherited parent session ID can differ. An explicitly supplied ID must agree with the selected host identity. Prefer a canonical host-supplied source path. Otherwise search filenames only under `CODEX_HOME/sessions` (default `~/.codex/sessions`) for the exact current session UUID, then read only the unique candidate. Validate canonical regular/nonlinked paths, embedded session identity and workspace, source schema and stable read. Conflicting supplied/current identities, zero/multiple matches, unsafe paths, unsupported/truncated sources or wrong metadata are actionable blockers; never select a newest file, scan unrelated conversation content or reconstruct text. Other hosts can supply an authoritative session ID and canonical path explicitly. Missing current host identity remains unverified; prior registered-source coverage alone does not establish readiness for a new unknown session.

Primary runtime startup remains read-only and core validity stays independent of `recording_context`. Its recording states include `disabled`, `needs_activity`, `needs_binding`, `verified`, `needs_synchronization`, `blocked` and `unverified`. Resolve required readiness before substantive recorded work. An empty Activity created in a prior turn receives its work range at the first actual assigned prompt, not at the earlier creation/closure prompt. A resolver's latest user occurrence is diagnostic information, never an automatic Activity boundary. The host obtains an authoritative saved occurrence from the actual turn/source; an ambiguous mapping blocks assignment rather than using a timestamp or text similarity.

`recording bind` registers a checked source, explicit observed user position and supplied enabled intervals using the existing synchronizer/ledger. Preview creates nothing. Repeated identical binding is safe; existing identity/range/intervals cannot silently move. Resume recorded bindings, respecting verified message continuity and enablement revisions. A changed source prefix triggers supported semantic reconciliation; it is not permission to discard evidence or guess attribution. A new current session in an existing Activity needs its own explicit binding; unknown related sessions remain a coverage limit. `usage_source` in the bind result can be passed by the host to `activity usage-update`; it is attribution data, not a token/credit estimate.

Interactive binding requires the actual work prompt, not an environment-only user
record. If a participant's assignment is saved as native inter-agent metadata,
the coordinator verifies that record and its attribution, and registers the
explicit range through existing `recording synchronize`. Eligible final outcomes
remain exact source text; inter-agent/tool records do not become human prompts.
If the assignment occurrence cannot be verified, keep the boundary unavailable.

## Synchronization and integrity

Apply validated recording settings and mandatory workspace instructions. Disabled recording without an independent obligation performs no discovery and creates no transcript directory, segment or checkpoint. Enabling covers subsequent eligible exchanges; earlier off periods require explicit historical-import authority. Configuration changes preserve existing files, gaps and coverage. Host scheduling synchronizes newly saved outcomes at the next active turn, uses the prompt threshold for ordinary batches, and synchronizes/verifies synchronously before each commit and closure regardless of threshold. A real host turn-completion hook can flush after delivery; without one, no background continuation or unsaved outcome is claimed.

Use only completed, durable saved source for exchange text, except the explicit [mandatory pre-delivery procedure](../procedures/mandatory-pre-delivery-recording.md). Preserve human prompts, clarification exchanges and delivered final outcomes verbatim and in source order. Exclude tool calls, internal instructions, environment metadata and progress. Keep source identities, boundaries and verified coverage separate from exact text. Never reconstruct missing messages, deduplicate equal text, record one occurrence in overlapping Activities or segments, claim a proposed operation was completed, or treat a prepared outcome as already saved. Retain historical bytes and optional labels, and do not reject an older label alone. Closed-record catch-up is permitted only for assigned completed old-source exchanges and does not reopen the Activity or authorize new substantive work.

The ordinary synchronization command updates only the current active Activity.
Read-only verification also accepts archived Activities. Closed-record catch-up,
legacy adoption and prepared-text reconciliation remain explicit core maintenance
procedures; these commands do not implement those mutations. Report that limit
before dependent work rather than claiming catch-up or appending around the ledger.
Pending/prepared or interrupted checkpoint state blocks ordinary synchronization
until explicitly reconciled; it is never erased by a later successful batch.

Before reads and again before writes, validate containment, target types, safe direct-child store consistency and the selected Activity identity; load only relevant assigned records and artifacts rather than recursively reading unrelated history. Use sole mutation ownership, recheck inspected source, assignment, coverage and target contents immediately before writes, exclusively create new directories and segments, and never overwrite another source or segment. Preserve unrelated material. On changed inputs, gaps, divergence, unsafe paths, ambiguous coverage or partial failure stop affected work, preserve and report actual partial results; never silently truncate, repair, retry or roll back. Recheck exact contents and occurrence coverage after writes. Source hashes and scheduling cursors alone do not establish coverage.

The [transcript convention](transcript-segment_conv.md) retains checkpoint format 1. Core maintains a supplemental `chronicles/core.json` binding/hash ledger; existing checkpoint or segments lacking that ledger require explicit adoption, and unsupported, malformed or unknown legacy state blocks rather than being rewritten implicitly. See [Codex source convention](codex-source_conv.md) for supported representations and immutable-prefix safeguards.

An actual enable/disable change through environment configuration increments the
internal `features.chronicles.enablement_revision` (absent means zero). Cadence-only
changes do not increment it. After an enablement transition, synchronization
requires explicit updated enabled intervals for every already registered source,
with attributable boundaries and no removal of previously recorded exchanges.
It never assumes that an intervening disabled period was eligible. Unchanged
identity/path/assignment bounds remain required; only interval reconciliation is
permitted for that transition. Unknown boundaries block dependent recording.

Required-mode or independently mandatory recording must be synchronized and verified afresh through the completed closure-request cutoff before Activity closure. Best-effort closure attempts the same synchronization, with only source interruptions eligible for the explicit unavailable outcome described above. Core close synchronizes registered sources and validates exact evidence; missing, pending, divergent or ambiguous required source, outstanding writes or coverage gaps block close. Closure synchronization finalizes a live source assignment end at the completed eligible closure cutoff so later Activity source ranges do not overlap. The future undelivered acknowledgement is outside that cutoff. Disabled/no-obligation closure requires no recording writes or source. See [recording evidence](recording-evidence_conv.md), [synchronize](../procedures/synchronize-chronicles.md) and [verify](../procedures/verify-chronicles.md).
