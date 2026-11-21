# Activity conversation storage review

This is an investigation and proposal, not an implemented storage change.

## Actual current responsibilities

| Location | Purpose and consumer |
| --- | --- |
| chronicles/*.md | Human-readable exact human/assistant exchanges imported from explicitly assigned native AI-session sources. Optional chronicles feature; excludes tools/progress. Used by recording integrity verification and human review. |
| system/chronicles/checkpoint.json | Synchronization progress, source assignments, verified/pending ranges and scheduling state. Machine data, not a second readable transcript. |
| system/chronicles/core.json | Source bindings, prefix/artifact hashes and message index used to check retained transcript integrity, compare source continuity and recover from safe source-format changes. The current index also repeats full message text. |
| system/chronicles/history/<id>/ | Preserved predecessor checkpoint, ledger and transcript plus reconciliation explanation, created for a recording reconciliation rather than every ordinary synchronization. |
| system/chat.jsonl | Mandatory append-only Activity messages, captured by host/participants through chat-post, independent of optional chronicles/native-source availability. Supports human-entry persistence and participant coordination, with typed roles and delivery status. Not source-verified merely because posted. |

The separation of readable transcripts and operational metadata comes from Activity layout 2: activity_layout.artifact routes chronicle Markdown to chronicles/, metadata and recovery copies to system/chronicles/. The same folder label obscures their different purposes.

## Observed evidence before this review's capture/synchronization

- Current transcript: 76,141 bytes. Current ledger: 109,243 bytes. Checkpoint: 2,494 bytes.
- Ledger message_index: 110 messages, with 73,507 UTF-8 bytes of repeated message text.
- Chat: 35 records, all human. 33 match indexed source messages after trimming surrounding whitespace (diagnostic comparison only, not source identity or safe deduplication).
- Recovery folder 9cfa7845-e874-4963-839b-5fb105beef77 contains the old transcript/checkpoint/ledger and reconciliation.json. The recorded event at 2026-11-19T02:04:26Z resolved earlier unsupported-record gaps after reviewed metadata recognition. These are historical versions, not competing current files.

## Assessment

Human-entry capture and optional source-backed recording intentionally overlap: the first survives absent/disabled native recording, while the second retains delivered assistant outcomes and independently checks source attribution. Their different guarantees justify some duplication. Current chat contains no assistant replies, despite its wider schema/contract, so replacing chronicles with a rendering of chat would lose recorded content and source guarantees.

There is unnecessary complexity as well: full message text is duplicated inside a machine ledger, source/range facts overlap across two metadata files, and recovery history is nested separately from the Activity-wide history convention. Disk usage is modest; confusing ownership and extra consistency checks are the larger costs.

## Recommended target

```text
<Activity>/
  chronicles/                  # optional readable source-backed transcript
    <segment>.md
  system/
    chat.jsonl                 # mandatory human entries and participant messages
    recording.json             # one versioned recording state, without full message bodies
  history/
    recording/<revision-id>/   # preserved predecessors only for actual reconciliation
```

1. Keep chat and optional chronicles with explicit purposes. Do not require users to inspect system files. Describe the distinction once in the Activity README/navigation. Enforce existing assistant prepared/delivered rules honestly; no invented delivery hooks or backfilled replies.
2. Combine checkpoint and ledger into one authoritative versioned recording state. Keep bindings, progress, gaps, hashes and occurrence identities with no duplicate source assignment structures. Preserve pending-operation and partial-write detection.
3. Replace full message bodies in that state with occurrence IDs/positions, role, exact-content hashes and explicit byte spans into the retained transcript. This requires a defined byte contract and migration tests: Markdown headings alone are ambiguous when user text contains those headings. Verify source continuity with actual source text and these references; a hash alone is not proof of coverage or attribution.
4. Keep reconciliation backups but place future ones under the common history/recording/ area. Do not create a history snapshot for every ordinary sync or delete old snapshots automatically. Existing history remains until an explicit, preservation-checked migration.
5. Keep source-backed recording independently verifiable. Do not blindly merge posts and source messages or deduplicate by text; identical text can be separate occurrences. Link the two by an observed source message identity when available, retaining separate provenance and delivery status.

Implement in stages: clarify ownership/navigation; introduce a versioned state and byte-span contract with self-contained recovery/continuity tests; provide explicit migration preserving current evidence. No rewrite of all recording functionality or loss of optional-recording independence is needed. This proposal has not been independently reviewed or implemented.

## Inspected implementation/contracts

- .hai/tools/activity_layout.py: artifact routing.
- .hai/tools/runtime/chronicles.py: load/verify/render, full-text snapshot storage and predecessor preservation.
- .hai/tools/runtime/source_continuity.py: exact retained-message continuity checks and source rebasing.
- .hai/conventions/activity-chat_conv.md: mandatory chat and append-only message contract.
- .hai/conventions/chronicles_conv.md and transcript-segment_conv.md: optional exact-source recording and checkpoint contract.
