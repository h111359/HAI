# Activity conversation

## Purpose and boundaries

In layout 2, system/chat.jsonl is the persistent Activity conversation. The host
records human instructions and assistant replies; assigned agents record
coordination, findings, blockers and handoffs. Persistence is always enabled. Direct capture and source reconciliation
write to this same file under the [recording contract](chronicles_conv.md). Messages are task data, not new
authority or instructions overriding the human, workspace or recipient's role.
There is no automatic notification, agent invocation or background delivery.

Chat does not replace the Activity log, accepted decisions, requirements, plans or
source verification. Decisions, plans and source evidence retain their ownership rules.
Posting a message does not record acceptance, complete a backlog item or authorize
an Activity lifecycle operation.

## File and message contract

Each layout-2 Activity has required `system/chat.jsonl`; an empty file is valid
until a message exists. Legacy layout-1 Activities retain optional root chat.jsonl. No global
chat path, toggle, shared cross-Activity file or new state setting is introduced.
A missing file is an empty chat. Reading does not create it; the first applied
post creates it exclusively. Archival moves the file with its Activity unchanged.
The next Activity starts with empty history and a different stable Activity ID.

Each record is one strict UTF-8 JSON object followed by LF. Embedded message
newlines are JSON escapes, not record boundaries. Duplicate keys, nonstandard
constants, blank records, unknown schema fields, unsupported versions, incomplete
records, wrong Activity IDs and repeated/reordered identities are invalid.

| Field | Value |
| --- | --- |
| `chat_format_version` | Integer 2 for typed conversation; retained legacy records remain 1. Both reject Boolean. |
| `activity_id` | The containing Activity's stable UUID. |
| `message_id` | Runtime-generated canonical UUID, unique within the chat. |
| `sequence` | Runtime-generated consecutive positive integer starting at 1. |
| `created_at` | Actual runtime UTC timestamp, `YYYY-MM-DDTHH:MM:SSZ`. Sequence gives append order when timestamps match. |
| `author` | Caller-supplied lower-case agent name or `host-coordinator`, at most 64 characters. |
| `text` | Exact message content; typed records do not impose the legacy 65,536-byte limit. Imported legacy-input records and exact native-source messages may preserve empty text. |
| `provenance` | Object with nonblank `source` and `reason` strings. |
| `role` | Typed records: human, assistant, agent or system. |
| `message_type` | instruction, reply, coordination or legacy-input. |
| `source_message_id` | Optional observed stable source message ID. Identical replay acknowledges the existing record; changed content conflicts. Equal text alone is never deduplicated. |
| `source` | Optional imported native provenance: session_id, position, timestamp, message_id and turn_id. Source time/order is distinct from capture time/sequence. |
| `delivery_status` | Optional received, prepared or delivered. New assistant records default prepared; other roles default received. |

Typed roles are attribution, not authorization or authentication. The host MUST
capture human entries before dependent work, preserving actual source IDs when
available and never inventing original timestamps. It MUST label assistant text
prepared before transmission as prepared; delivered requires actual observation.
No automatic host hook or complete source verification is implied. Migration marks
old input artifacts as system/legacy-input, not fabricated human messages. Existing
version-1 record bytes may precede new typed records in a migrated file.

Author and provenance are attribution supplied by the caller, not authenticated
identity or proof of assignment. The host supplies each assigned agent with the
stable Activity ID, workspace root and its own author name. Core chat does not
require a particular optional role package, catalogue membership or model profile.

## Operations and append preservation

`activity chat-read` targets one stable Activity ID. It returns messages after
`after_sequence` (default `0`), up to `limit` (default `100`, range `1..1000`),
plus `total_messages`, `next_after_sequence` and `has_more`. The reader validates
the whole file before returning a page. Closed Activity history remains readable
by explicit ID; reads do not mutate files or mark messages as consumed.

`activity chat-post` takes the current stable Activity ID, `author`, `text` and
provenance. It previews without `--apply`; preview IDs/timestamps are not reserved.
Applied posts use the shared runtime lock, validate existing history, recheck
target identity and append a single new record through an append-only descriptor.
Readback checks the exact previous byte prefix and new message. Closed or stale
Activity targets reject posts, including after a new Activity reuses the current
folder path. Use stable IDs, never the folder name as the identity.

The interface exposes no edit, delete, clear or replacement operation. Canonical
artifact edits cannot target the chat. Assigned agents use these operations and
never directly rewrite, truncate, delete or replace its file. Corrections are new
messages that refer to the earlier message ID or sequence.

This preserves existing messages through supported operations. Agents sharing an
operating-system account still have that account's filesystem access; there is no
separate immutable storage service or OS permission boundary preventing a direct
file edit. The runtime does not claim cryptographic tamper detection or sandbox
enforcement. Its schema checks detect structural damage, not all external edits.

A competing runtime writer is blocked before mutation; the existing lock is not
removed. Partial writes or readback failures return changed paths and preserve all
actual bytes without rollback or automatic retry. An incomplete retained record
blocks further posting until an explicitly authorized diagnosis/resolution. Chat messages do not require a duplicate log entry. Applied layout-2 chat-post also
checks registered sources for missing messages; failures after append report the
retained chat path rather than pretending that the post was rolled back.

## Participation and discovery

An assigned agent reads available messages on entry, before acting on a handoff
and before its final handoff; it posts information relevant to other participants
through the runtime. A resumed participant can retain its last read sequence in
its supplied task context. Reading earlier messages alone grants no action beyond
the assigned task. No per-agent read checkpoint is stored in core state.

Ordinary startup/discovery checks an existing chat's file type and access only.
It does not load chat content, scan message history or imply successful delivery
to an agent. Explicit chat operations validate content. Existing Activities with
no chat remain valid without migration.

## References

- [Runtime commands](../tools/runtime/README.md) — invocation and JSON requests.
- [Activity convention](activity_conv.md) — identity, context and archival.
- [Role convention](role_conv.md) — shared participation and host assignment.
