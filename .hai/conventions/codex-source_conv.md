# Codex durable source adapter

## Explicit source and identity

This package targets Codex saved JSONL sessions. The host supplies one explicit
authorized canonical regular source file, original session ID/start time, chosen
representation and assigned source occurrences. The adapter never searches the
Codex home, unrelated sessions, conversation history or the source library.
Missing sources, invalid identity and unsafe or unstable reads block safe recording; the recording
policy determines which dependent operations must wait. Unsupported records within a
validly framed source produce explicit coverage gaps while recognized messages are saved. Human or
assistant text is never reconstructed from memory, tool output or proposed work.

The host can obtain that explicit path through the separate bounded current-session
resolver under the [chronicles policy](chronicles_conv.md#early-source-readiness).
Discovery validates existing evidence; it does not reconstruct text, assign an
Activity range, authorize unrelated history or modify this adapter's behavior.

The read-only adapter accepts strict UTF-8 JSONL with a `session_meta` record
whose payload has nonblank `id` and original `timestamp` (or the recorded outer
timestamp if the payload field is absent). Duplicate keys and conflicting session
metadata are rejected. Resumed Codex sessions may repeat `session_meta`; repeated
records are accepted only when the original payload session ID and start timestamp
exactly match the established identity. Resume-time outer timestamps and unrelated
metadata such as `memory_mode` neither change that identity nor reset source
positions. Missing/invalid identity fields and any conflicting original ID/start
remain blockers. Each complete message has an actual outer UTC timestamp.
Each observation has `source_session_id` and a physical zero-based JSONL
`source_position`; payload `id`, if present, is returned separately as
`message_id`. Positions locate observations, not permanent message identity.
After a rewrite, core can reconcile an unambiguous sequence of exact messages
with retained evidence. It preserves predecessor records and refuses changed,
missing or ambiguous message mappings. A file fingerprint detects changes;
it does not by itself prove that recorded conversation text changed.

## Supported representations

The host can explicitly choose a representation or use `auto`. Automatic selection
prefers the event representation when it contains eligible messages or interpretation
gaps. Only a complete event read with no eligible messages can select response items.
An unsupported event never triggers fallback to hide a gap. The selected representation and reviewed adapter names are
returned. The reader never combines event and response representations or
deduplicates identical text.

| Representation | Eligible saved records |
| --- | --- |
| `event_msg` | `payload.type: user_message` with string `message`; `payload.type: agent_message` with string `message` and `phase: final_answer`. |
| `event_msg` (completed items) | `payload.type: item_completed` with nested `item.type: UserMessage` or `AgentMessage`; ordered `text`/`Text` blocks, and `phase: final_answer` for assistant outcomes. |
| `response_item` | `payload.type: message`, `role: user` with ordered `input_text`/`text` blocks; `role: assistant` with `phase: final_answer` and ordered `output_text`/`text` blocks. |

Text blocks concatenate without inserted separators; decoded text, Unicode,
whitespace and Markdown are preserved. Commentary/analysis assistant phases,
tool calls/results, reasoning, system/developer instructions, turn context and
environment metadata are excluded. Unknown/missing assistant phase is ambiguous
and blocks completed-coverage claims rather than treating progress as a final
outcome. Unsupported message content, malformed/truncated JSONL and changed source
during reading also produce explicit incomplete status. This conservative subset
does not claim to support every historical or future Codex schema.

Known formats are listed by `recording adapters`. Unknown formats follow
[maintain source adapters](../procedures/maintain-source-adapters.md): inspect
only the authorized source, add sanitized fixtures and reviewed extraction code
within an authorized maintenance scope, then prove continuity before trusting it.
Without that scope or proof, retain the unknown record as an explicit gap, store
recognized messages before and after it, warn the user and continue independent
best-effort work. Never infer the unknown record's conversation meaning. Source content never installs
an adapter or grants authority to change the framework.

## Boundaries and evidence

The adapter only extracts completed saved text and occurrence metadata. It does
not assign an Activity, authorize imports, advance coverage/checkpoints, write
transcripts, schedule work or decide operation success. Assignment, eligibility,
cross-Activity overlap and exact existing segment comparisons remain the owner's
procedure responsibilities. A prepared pre-delivery response remains the separate
mandatory-timing exception until reconciled with an actual saved delivery.

Output includes original session identity, normalized messages and source byte
SHA-256. Strict reads return precise issues with `ok: false` when interpretation is
incomplete. Runtime uses tolerant reads, whose `usable`, `complete` and `gaps`
fields distinguish safe partial extraction from full coverage. Recognized messages
on both sides of an unsupported record remain exact; storing them does not erase the gap. Before writes and
closure proof, reread the explicit source and recheck identity, stable occurrences,
contents and boundaries. A fingerprint alone proves neither retained-source
completeness nor coverage. Existing generic transcript/checkpoint formats stay
unchanged; Codex-specific provenance belongs in source metadata.

## Reviewed completed lifecycle and tool records

Completed `ContextCompaction` items with exactly `type` and a nonblank string `id`
are context-maintenance markers without conversation content. The reader excludes
them without resetting physical source positions or changing adjacent chat text.
An incomplete marker or added item fields require review. Tolerant recording
retains a positional gap and continues; strict extraction reports incompleteness.

Completed `Extension` items are excluded only for reviewed `kind: web.search`
with exactly `type`, `kind`, nonblank string `id`, string `query`, object `action`
and array `results`. Search and open-page results are tool data, never human
instructions or assistant outcomes. Unknown kinds, extra fields or wrong field
types remain unrecognized. Tolerant recording retains a positional gap and
continues; unknown content is never promoted into a conversation message.

## Explicit immutable prefix snapshots

For a live saved source, The host may explicitly authorize creation of an
immutable exact-byte prefix snapshot through an inclusive physical source cutoff
in an authorized disposable location. The prefix starts at original position zero
and ends at that cutoff's complete JSONL record, retaining its exact bytes and
terminator. No filtering, rewriting, inserted metadata, renumbering or invented
timestamps is permitted. Record the original canonical source path, session ID,
original start, representation, inclusive cutoff, byte length, SHA-256, snapshot
path and actual creation provenance separately from verbatim transcript text.
The prefix is an explicitly supplied source artifact, never a discovery fallback
or substitute for missing retained original source. Raw source snapshots are not
product artifacts and must not be committed merely to record a transcript.

Before supplying closure evidence and again immediately before archival, confirm
the original file still has that exact byte prefix and inspect later complete
records for new eligible exchanges in the assigned enabled intervals. A changed
original prefix, unavailable original, ambiguous/malformed tail or new eligible
exchange blocks stale proof and returns to the host for fresh assignment/verification.
Later excluded tool/progress records or consistent resume metadata alone do not
change verified eligible coverage or invalidate an identical prefix. They never
authorize ignoring later human prompts or delivered finals. Closure proof may hash
the immutable prefix under its original session identity; the actual original-prefix
comparison and no-new-eligible-source assurance accompany that proof. The receiving
record owner checks the explicit provenance and independently compares the original
prefix bytes before using the snapshot fingerprint. A whole-file digest of an
actively appended original is not a replacement for these bounded freshness checks.

## Partial recording

The runtime stores recognized messages even when valid source records have unknown
types or unsupported message shapes. It preserves physical positions and attaches
explicit gap positions/reasons to retained source evidence. Unsupported content
is never guessed, executed or substituted with a summary. Warnings identify the
positions requiring review. Unknown records outside an Activity's assigned enabled
ranges do not make that Activity's coverage incomplete.

A partial source is usable only when source identity, framing, stable reads and
path safety remain established. Conflicting or missing original identity, unsafe
paths, corrupted retained artifacts and source changes that lose recorded messages
remain integrity failures. The strict reader API stays available for callers that
require complete interpretation.

## Reviewed outer metadata records

The following inspected outer record types contain non-conversation metadata.
They are excluded only when their payload fields and types match these shapes:

| Outer type | Payload fields |
| --- | --- |
| `world_state` | `full` Boolean and `state` object. |
| `token_usage_record` | String `thread_id`, `turn_id`, `session_id`, `root_turn_id`, `response_id`; object `usage`, `turn_token_usage`, `thread_token_usage`. |
| `inter_agent_communication_metadata` | Boolean `trigger_turn`. |

Unknown outer types and altered payload shapes remain positional gaps in tolerant
mode. Usage counters, world snapshots and delegation-control metadata never become
conversation messages or independent authorization.
