# Always-enabled Activity conversation recording

## One authoritative conversation

`system/chat.jsonl` is the append-only Activity conversation in layout 2. HAI records every received human message verbatim before dependent work, delivered assistant replies when observable, and participant coordination with explicit attribution. Recording has no enable/disable switch or prompt threshold. Visible assistant commentary/progress is included. Native tool calls, internal reasoning and system/developer instructions are not conversation messages. Explicit participant coordination remains typed separately.

The host MUST persist visible clarification questions/answers presented through a host UI tool as typed chat when their actual presentation is observed; tool plumbing is not a substitute for capturing their text. The host MUST attempt `recording synchronize --apply` at every new/resumed turn, after registered-source work and before commits and closure. Applied chat-post also reconciles registered sources. Startup is read-only: it checks missing saved messages and reports synchronization/binding/migration needs without claiming to have performed a write. The host MUST act on those needs. No background worker or delivery hook is assumed. A final reply unavailable until after delivery is collected from its saved source at the next interaction; prepared text MUST NOT be represented as delivered.

## Sources and missing-message checks

Native sources require explicit source identity, Activity start/end boundaries and provenance. Host-identified current-session discovery follows the existing safe source convention; never search unrelated sessions, guess boundaries from timestamps, or import outside the assigned Activity. New bind requests need no enablement intervals; source start/end define the always-recorded range. Historical enablement intervals are preserved in predecessor evidence, but the authorized unified migration reconciles the entire assigned Activity range, including previously omitted occurrences.

Synchronization checks all retained occurrences and all eligible saved source messages, not merely a tail cursor. It appends missing occurrences without replacing or reordering existing chat bytes. Imports retain original source identity, position and timestamp separately from runtime capture timestamp/sequence. IDs are qualified by source session. Equal text alone never establishes identity: repeated equal prompts remain distinct. Old source-less chat posts remain unchanged; possible overlap is not silently deduplicated. Verified stable identities/order can reconcile representation changes without repeating messages. Ambiguous changes remain explicit coverage limits.

A missing/unrecognized source must not suppress recognized messages from another source. Unsupported valid records produce warnings and positional gaps while recognized messages are retained. Native source unavailability never disables direct human-entry capture. Integrity failures, unsafe attribution/paths and uncertain partial writes are reported and preserved, not silently repaired or claimed complete.

## Operational state and recovery

Only `system/recording.json` stores synchronization bookkeeping: version, source bindings, source-prefix fingerprints, references/hashes into chat, warnings and migration progress. It contains no repeated message bodies. Native provenance is stored with imported chat records. Native source content can be verified only while its source is available; no source contains all hidden host interactions. Source identities/order supplement append sequence; a late import is not moved into the old byte prefix. Durable source registration precedes import, so an ordinary retry can resume an interrupted append-before-state publication without caller resupplying the binding.

Applied imports use the shared runtime lock, contained nonlinked paths and exact chat prefix/readback checks. Referenced messages must retain their expected exact content and provenance. Current-source verification is separate from capture and never makes an unavailable source fully verified.

## Legacy migration

`recording migrate` previews or applies conversion for the sole current layout-2 Activity. Legacy transcript/ledger hashes and indexed rendering must validate first. Copy every predecessor byte, including earlier repair history, into `history/recording/before-unified-v1/` before retiring old locations. Import every provable indexed message even if its original native source is unavailable. Do not guess Markdown boundaries when a proven index is absent. Existing chat bytes remain an exact prefix. Publishing/importing/retiring phases are resumable; only originals matching verified backups may be removed. Historical Activities stay readable without automatic rewriting. The layout-1 recorder remains a historical compatibility implementation, not a new Activity recording option.

## Closure and limitations

Closure reconciles sources synchronously and records actual warnings in the outcome. Independent mandatory completeness obligations still require complete source coverage after recognized content is saved. Legacy external proof cannot bypass unified verification. An unavailable registered source with an unresolved end boundary prevents archival: otherwise an open historical range could consume future Activity messages. Resolve that boundary with evidence; do not invent a cutoff or silently lose its tail. Ordinary independent work may continue through availability warnings.

A readable Markdown view may be generated on demand as an export, but is not a second maintained conversation store. Existing historical transcripts remain preserved evidence. Every completion report must distinguish recorded content, verified coverage, gaps and unsaved outcomes.

New chat source metadata and empty-feature defaults are forward changes; older HAI runtimes may reject them. A downgrade must use a reviewed restore from preserved predecessors, never erase fields to make an old reader accept the new state.
