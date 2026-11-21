# Read-only Codex source adapter

The native-source adapters here also serve current always-enabled chat reconciliation. Standalone Markdown/checkpoint contracts described below are historical compatibility; current runtime imports text into chat.jsonl. See [recording](../../conventions/chronicles_conv.md).

`read_codex_source.py` requires Python 3.11+ and the standard library. Verify an
absolute interpreter under the core tooling convention before execution. Pass
only the explicitly authorized canonical source; no session discovery occurs.

From the workspace root:

```text
<absolute-python-executable> -B .hai/tools/chronicles/read_codex_source.py /explicit/session.jsonl --representation event_msg --expected-session supplied-session-id
<absolute-python-executable> -B .hai/tools/chronicles/test_read_codex_source.py
```

The [source convention](../../conventions/codex-source_conv.md) documents the supported
conservative JSONL subset and representation choice. Older/future schemas, ambiguous
assistant phases, missing metadata, malformed/truncated records or changed sources
return `ok: false` with explicit issues. Select one representation and retain it;
never merge event/response duplicates. Blank records and duplicate JSON keys fail.
Repeated resume metadata is accepted only for the exact same original session ID
and start timestamp; changing outer resume time or nonidentity metadata does not
renumber occurrences. Conflicting original identity/start still blocks reading.

The API is `read_source(path, representation, expected_session=None, *, allow_partial=False)`.
Runtime recording uses `allow_partial=True`; the CLI exposes `--allow-partial`. JSON output
has `ok`, source identity/start, `representation`, `durable_path`, `source_sha256`,
`messages`, selected `adapters` and `issues`, plus `usable`, `complete` and
`gaps` (physical source position and reason). `ok`/`complete` describe full
interpretation; `usable` distinguishes a safe partial subset from an integrity failure. Each normalized message has exact decoded `text`, `role`,
actual `timestamp`, `source_session_id`, physical `source_position` and an
optional original `message_id`. Physical positions are zero-based JSONL lines,
including excluded records. Repeated identical messages retain different positions.
The adapter has no writes, side effects, downloads or external dependencies. Strict
CLI exit 0 means complete interpretation and exit 1 means unavailable/incomplete
source. With `--allow-partial`, exit 0 also permits a usable partial subset; inspect
`complete` and `gaps` rather than treating that exit code as full coverage. Exit 2
is CLI argument misuse. Returned partial messages never prove complete
coverage. Paths outside the workspace require the caller's supplied source authority;
acceptance of a path by this parser is not permission to read it.

`auto` (the CLI default) selects supported event messages first, then response
messages only if a complete event read contains no eligible messages. A partial
event read with gaps never falls back to hide those gaps. It never merges
representations. The reviewed
registry in `adapters.py` supports legacy events, completed nested items and
response messages. Completed item support excludes known reasoning, tool,
subagent activity and progress records, plus completed `ContextCompaction` lifecycle
markers whose item contains only a type and nonblank ID. These markers carry no
conversation text; they retain physical source positions and never become chat.
Reviewed completed `Extension` items of kind `web.search` with ID, query, action
and results fields are also excluded as tool records, including open-page actions.
Their results are never promoted into user or assistant conversation messages.
Changed or incomplete compaction shapes remain explicit gaps in tolerant mode;
unfamiliar message shapes no longer suppress storage of recognized messages.
Strict extraction still reports incomplete interpretation. Format changes are handled by reviewed code, not executable definitions
supplied in a source file. See [maintain source adapters](../../procedures/maintain-source-adapters.md).

This tool neither scans sources nor creates or advances transcripts/checkpoints.
It does not establish Activity attribution, enabled intervals, retained-source
completeness or coverage; core synchronization performs those checks and compare exact
existing segments. A trailing incomplete source record blocks progress past that
boundary rather than being silently discarded. Tests use disposable textual
fixtures, not a user's actual sessions.

The source convention permits an explicitly assigned immutable exact-byte prefix
snapshot for a live source. The reader treats that canonical file as supplied and
preserves its original physical positions; it does not create the snapshot or
prove its original-source provenance. Core separately verifies the original
prefix and absence of later eligible exchanges before claiming closure freshness.
Excluded tool records appended to the live original do not by themselves change
the immutable prefix fingerprint; changed original text or new eligible exchanges
still invalidate stale closure evidence.

## Partial extraction and storage

In tolerant mode the reader continues across unsupported, validly framed selected
records and returns exact recognized messages before and after them. Gap entries
contain `source_position` and `reason`; opaque unknown payloads are not promoted
into chat or interpreted as instructions. The original source remains unchanged.

Core synchronization retains source-scoped gap evidence and reports
`recorded_with_gaps` with warnings. Positions outside the assigned enabled range
do not affect that Activity. Reader usability is not full coverage, and repeated
synchronization must not duplicate messages or erase gaps. Identity conflicts,
invalid JSON framing, unstable reads, unsafe paths and damaged retained evidence
retain their integrity protections. See the [chronicles contract](../../conventions/chronicles_conv.md).

Inspected outer usage/world/delegation-control metadata is excluded only in the
reviewed shapes documented in the [source convention](../../conventions/codex-source_conv.md#reviewed-outer-metadata-records).
Changed shapes and unknown outer record types remain explicit gaps.
