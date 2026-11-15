# Independent recording compatibility review

Reviewed adapters, reader, source discovery, semantic continuity, predecessor retention and best-effort/required policy. No implementation files changed by reviewer.

## Findings

1. High: different source session was downgraded to optional interruption, allowing best-effort closure. Fixed by author; independent probe now returns blocked with original source identity changed.
2. High: related archived Activity used stale physical boundaries after rewrite, allowing the same logical exchange in a second Activity. Fixed by author; independent probe now rejects unverifiable archived source positions.
3. Medium: unknown event with text field could disappear as excluded metadata. Root fixed guard; independent probe now rejects unsupported message-shaped event.
4. Limitation: foreign-OS saved absolute path raises before missing-path discovery. Root informed; same-OS relocation supported. Broader unknown-event discriminator allowlist recommended, since unknown future schemas cannot safely be classified by a few text field names alone.

## Checks

- Independent fixture probes, all writes confined to invocation/test-work: wrong session identity blocked; unknown text event blocked; shifted archived duplicate coverage blocked.
- Complete runtime suite: 190 tests, 3 failures, 10 platform skips. Remaining failures are expectations/fixture environment issues: default auto discovery now succeeds on response-only source, no-source diagnostic wording changed, real-missing-source policy fixture conflicts with inherited host session ID. Root/authors notified; rerun after correction required.
- Chronicles suite: 17 tests passed, 1 platform symlink skip.

No remaining demonstrated safety blocker after the fixes above. Approval remains conditional on corrected full-suite results and resolving/documenting the foreign-path and unknown-event limits. Actual Activity reconciliation was not performed by this reviewer. No outside-workspace writes or real-session source edits performed.

## Follow-up review

Foreign-OS locator recovery, turn-level identity matching across regenerated item IDs, strict unknown event discriminator handling and strict source identity protection were reviewed. Six targeted tests independently passed on Windows Python 3.14.7 with fixtures inside this invocation: foreign locator rediscovery, retained turn identity, shifted archived overlap rejection, source identity conflict, discovery identity conflict and same-turn regenerated item IDs.

No remaining objection to these deltas. Root is rerunning broad suites after correcting the three prior fixture/expectation failures. Remaining recommendation: apply the same explicit known-exclusions policy to response_item discriminators, since the role/suffix heuristic can silently ignore an unknown response type with a body/text field. Review approval for live reconciliation is conditional on those final checks.

## Final clearance

Reviewed final response-item known-exclusions whitelist and strict unknown-type failure. Independently reran chronicles reader suite: 17 passed, 1 platform skip. Parent reports broad runtime194/startup66/activities16 plus chronicles17 suites passed (platform skips reported separately). Earlier blockers and recommendations are resolved. No remaining review objection to applying the previewed real Activity reconciliation with predecessor preservation and fresh verification. No implementation/live recording writes by reviewer.
