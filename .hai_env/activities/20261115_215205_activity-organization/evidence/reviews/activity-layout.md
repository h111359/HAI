# Independent Activity layout review

The implementation is ready for the coordinator's authorized current-Activity migration. No remaining material finding was identified in the reviewed code and documentation. Live migration has not been performed by this reviewer.

The review covered default layout-2 creation and README closure; separate layout markers; legacy discovery; typed conversation, exact input and delivery attribution; system-owned usage and recording metadata; named invocation work; declared results/evidence destinations; safe disposable-work cleanup; workflow compatibility; and explicit migration with retained originals.

## Findings corrected and checked

- Malformed, Boolean, floating-point, unknown and mixed layout markers now fail with structured errors. Thirteen independent invalid-marker probes passed.
- Canonical artifact aliases and overlapping destinations are rejected before preview/apply writes. The originally reproduced partial-write collision is retained in resolved-artifact-alias-failure.json. Independent corrected probes preserved exact files and directories.
- Closure refreshes README navigation after creating usage and predecessor history, while retaining the exact earlier README.
- Migration handles empty legacy input explicitly, uses exclusive no-overwrite renames, refuses known unresolved workflow writers, retains unknown legacy material in history, preserves old chat bytes and validates both moved and untouched baseline evidence. Legacy container directories move into history instead of remaining loose at the Activity root.
- A reproduced failure after publication of layout-2 records initially allowed further Activity writes. Discovery now blocks prepared/partial migration reports. The original failure is retained in partial-migration-continuation-failure.json. Independent repeated failure injection confirmed subsequent public record rejects without writes; normal public migration and subsequent record succeed.
- Cleanup retains case-varied invocation manifest names. An independent Invocation.JSON probe preserved the entire allocation.

## Verification

Independent combined maintained suites ran 79 tests successfully, with two Windows symlink-creation capability skips in the existing chat/invocation tests. These covered layout lifecycle, migration, services, typed conversation, legacy chat, invocations and workflow runs.

After the final discovery recovery gate, all 22 new layout/conversation/migration/service tests passed with no skips. Independent public-API probes additionally checked alias/ancestor destination rejection, partial-migration continuation refusal, normal migration continuation and case-varied manifest retention. All fixtures and temporary files stayed inside this invocation's workspace-owned test-work directory.

Current Activity, conversation and runtime documentation agrees with the implemented storage and command contracts. Initial original content is retained in typed chat; README provides the human entry and final report; optional chronicles remain a separate source-backed facility. Request stdin avoids unnecessary request artifacts.

## Limits and handoff

The coordinator owns the broad regression report, live current-Activity migration and final preservation/readback checks. Existing closed archives were not edited by the reviewer. Migration must occur after all participants stop writing, followed by explicit new invocation-path handoff; old allocation paths must not be recreated.

The host must explicitly capture observed human and assistant content. Runtime persistence is not automatic UI interception, authentication or proof of delivery. Assistant text saved before transmission remains prepared. Caller-supplied stopped-writer and retained-evidence attestations remain host responsibilities; filesystem checks provide no OS-level isolation.

Only one readable review report and the essential failed reproductions are retained by this reviewer. No maintained source, actual workflow, live migration, commit or Activity closure was performed by the reviewer. Permitted Activity chat posts record review findings and this handoff.


## Explicitly selected closed-archive amendment

The user's authorized scope also includes the specifically discussed existing archive; this is separate from automatic or bulk migration. Reviewed the added allow_closed Boolean (default false), public API selection and durable closed-agent-work mapping. No material finding remains in this amendment.

Independently ran the migration/layout/conversation suites after this change: 22 tests passed, no skips. A separate public-API fixture confirmed that closed migration requires a different active work Activity and explicit allow_closed:true; default requests and absence of an active work Activity reject without writes; preview leaves all bytes unchanged. Applied migration preserves original lifecycle fields, closure/outcome metadata, archive folder, exact prior outcome bytes (including CRLF/trailing spaces) in both history and README, and the historical invocation manifest/evidence under history/legacy-material/agent-work. Closed-record mutations remain rejected, and the separate active work Activity stays byte-for-byte unchanged.

Current Activity/runtime documentation agrees with the explicit selected-archive exception. For a future authorized commit, tracked-source relocation mappings still need Git inclusion review: history avoids new disposable-work patterns, while global extension/cache ignores can still affect renamed files. This reviewer performed no Git mutation or live migration. Writers are ended again; new invocation-path handoff is required after migration.


## Final content-preservation and discovery correction

Reviewed the final layout-2 artifact change: supplied UTF-8 deliverable content is retained exactly, with artifact reasons and names recorded in the system log instead of appending a Markdown footer that would invalidate JSON. Legacy Markdown behavior is retained. The meaningful JSON regression checks both byte equality and successful JSON parsing.

Reviewed migration report ownership validation. Independently found/reproduced an appearance race between the two metadata existence checks, which previously raised UnboundLocalError. Discovery now initializes each Activity's report separately, fingerprints its presence/content before reading, rechecks after state validation and returns a structured failure if it appears, changes or disappears. The failed reproduction is retained in migration-report-appearance-failure.txt. Independent repetition now returns blocked with no runtime writes. All 11 final Activity-layout tests pass without skips, including the new content and discovery regressions.

No remaining material finding in the reviewed final scope. Writers are ended for the coordinator's explicitly authorized migrations; no further work should use the old invocation path after relocation without a new path handoff.
