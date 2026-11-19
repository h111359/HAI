# Chronicle compatibility repair and recording recovery

## Fix

Inspected only the exact host-identified native session. Three completed ContextCompaction items contained only a type and ID, with no conversation text. The adapter now recognizes that exact lifecycle shape and excludes it without changing source positions or adjacent message text. Unknown, incomplete or message-bearing variants still interrupt explicitly.

Reading farther exposed three completed Extension records of kind web.search, including search and openPage actions. The adapter recognizes their inspected ID/query/action/results shape as tool data. Results never become human messages or assistant outcomes; other extension kinds, unexpected fields and malformed values remain errors. The source convention and reader documentation describe both shapes. No native session files were modified and no workspace-identity checks were relaxed.

## Independent review and regression evidence

The independent reviewer was launched as /root/compaction_review with allocated invocation d6c47fb0-87f3-44e1-9f5c-91b6fa5dcc58. The reviewer found no code correctness blockers, independently passed the 20-test reader suite (one platform-dependent skip), required source-convention documentation, and recommended extra openPage/malformed query/action fixtures. Those documentation and test follow-ups were completed.

Developer checks: reader suite 20 tests, one platform-dependent skip; runtime chronicle suite 23 tests, one platform-dependent skip; no failures. Tests verify exact text, physical positions, unchanged source bytes, non-conversation exclusions and explicit rejection of changed/unknown shapes. Temporary files were confined to the Activity's disposable work/test-work directories. git diff --check passes.

## Recovery

The repaired reader parses the full current native log without extraction errors. Original session metadata retains the former haide workspace name. The earlier human-authorized rename to HAI, exact current host thread ID, canonical exact-ID source and actual first Activity prompt establish association. The existing explicit-source synchronization API was used; strict automatic discovery behavior remains unchanged.

Current Activity begins at the exact saved Create a new activity prompt, source position 6901. Enabled-state provenance uses unchanged configuration/revision 2 from the pre-Activity commit 16dca1a and retained Activity observations; no enablement changes were authorized during this Activity. The enabled interval and source were explicitly assigned.

The first preview detected a stale open-ended recording assignment in archived workflow implementation Activity 1b440d51-819b-4299-862b-0182f0f4fca5. Its retained checkpoint and 55 messages ended at position 1688. Independent review required a narrow metadata repair rather than expanding historical coverage. An isolated candidate passed core load/verify before publication. The live assignment was sealed at 1688, with its conversation body and all retained message tuples unchanged. Exact predecessor ledger/checkpoint/transcript bytes and repair provenance remain in that archive's chronicles/history/. Archived Activity state is byte-identical.

Positions 1689 through 2804 remain an explicitly unverified historical interval. A broader isolated backfill candidate was never published. This fix does not reconstruct that interval or claim it verified. The actual next-Activity prompt at 2805 establishes the later boundary. Unrelated archived Activities were not rewritten.

After sealing, current synchronization preview and apply succeeded, recording 30 saved messages. Fresh recording verify passed and startup now reports verified recording for the registered main-session source. These results do not claim unknown participant-session coverage or future unsaved final responses. The reviewer's available findings are retained in Activity records; no native child-session identity was supplied for separate attribution.

No commit or Activity closure was requested or performed for this fix.
