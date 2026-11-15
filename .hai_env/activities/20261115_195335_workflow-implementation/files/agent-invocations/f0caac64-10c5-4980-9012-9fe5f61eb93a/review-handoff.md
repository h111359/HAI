# Independent workflow implementation review

No remaining material findings in the reviewed parser, run-state, artifact, manager and host-contract scope after corrections.

Found and verified fixes:
- Legitimate artifact descendants named result.json, assignment.json or rejection-1.json no longer masquerade as uncommitted attempt control metadata.
- Accepted predecessor executors are retired from current ownership, allowing the ready next step to pause/cancel independently.
- Attempt-limit records identify the reached limits explicitly.

Verification:
- Independently ran 44 maintained parser/runtime tests: passed, with one Windows symlink-creation capability skip.
- Independently checked exact file and directory snapshots for zero-write prepare, execution report, completion, pause, cancel, resume and retry previews; start preview is covered by maintained tests.
- Independently exercised the corrected nested-artifact acceptance and ready pause/cancel paths.
- Installed agent catalogue audit/profile checks and manager validation passed.
- Golden and installed manager file sets and exact bytes match.
- Inspected latest requirements, detailed specification, core conventions, host execution procedure and manager contract/procedures.

Limits:
- Tests use isolated real filesystem fixtures and simulated host execution identities. No actual product workflow or external agent/model/service execution was performed.
- No claim of OS isolation, proof of host semantic assessments, external exactly-once execution or prevention of arbitrary unauthorized direct file edits.
- The root coordinator owns broad existing-suite compatibility and final CLI/readme integration checks.
- Full event/state snapshots and re-hashing retained artifacts favour simple integrity over large-run performance; no large-scale benchmark was undertaken.

Evidence is retained in this invocation folder. No maintained implementation edits, agent installations, actual workflow runs, commits or Activity closure were performed by the reviewer.


## Final integration review

Reviewed root README workflow introduction, runtime README command/request contracts, CLI group registration, Activity closure hook and configured-root protection changes. Documentation agrees with implemented command fields, pinned storage/lineage, readiness, executor evidence, preview/apply behavior and replay/recovery limits. No material integration finding.

Independently ran `test_workflow*.py` after final root integration changes: 33 tests passed with one Windows symlink privilege skip. This includes 22 run tests, five root integration tests and six existing workflow/package tests. Root integration checks cover template validation versus registration-only start, zero-write closure gate, optional feature absence, reserved roots and stable run paths after actual fixture archival with closed-owner mutation rejection.

No live workflow run or external host execution was performed by the reviewer. The coordinator retains responsibility for the live pilot and broad suite report.


## Final recovery guard amendment

Reviewed the final small runtime delta: a proposed run UUID or new attempt directory that already exists is rejected before writes, including previews. Existing prepared-assignment replay remains a separate retained-evidence path. Empty/partial orphan attempt directories are preserved with unchanged files, directory sets and attempt counters; UUID collisions preserve prior contents. The declined-content assessment fixture confirms rejection records the host's assessment without interpreting arbitrary bytes, and correction can complete the same unaccepted attempt.

Independent final `test_workflow_runs.py`: 25 tests passed, zero failures/errors/skips. No remaining material finding from this amendment. Evidence: final-recovery-tests.json.


## User-authorized Activity-local storage refactor

This amendment supersedes earlier review descriptions of externally stored, path-stable runs. Current runs belong at `<activity>/workflow-runs/<run-id>/`, without repeating the owner UUID in a directory. Owner UUID metadata stays stable; runtime resolves the unique current/archived Activity path. Archival moves contained runs, retaining exact bytes and run-relative artifact contracts. Legacy external evidence requires explicit relocation, with no fallback or implicit migration.

Reviewed current runtime, integration changes and current core/design documentation. Discovered and reproduced an accepted-output lineage race: a predecessor could change after source verification and be copied as new evidence. Root corrected `_source` to return verified evidence and start to bind that observation through snapshot copy. Independently exercised a later mutation immediately after `_source` returns: the operation reports partial changed paths and preserves the snapshot, without committing a run transition. Current guarded lineage, canonical path checks and archive ownership agree with the revised design.

One new cross-Activity fixture initially failed before reaching its intended guard because the other Activity lacked valid state. Root corrected it to a valid closed Activity. Final independent `test_workflow*.py` run: 42 tests passed, one existing Windows symlink privilege skip, no failures/errors. Coverage includes custom Activity store, accepted/unaccepted local run inputs through both prefixes, ancestor snapshot refusal, cross-owner rejection, byte-preserving archive movement/inspection, and legacy refusal.

No remaining material finding in the reviewed refactor. Actual pilot relocation and its byte manifest remain coordinator-owned; reviewer did not move or mutate live runs.


### Independent live-pilot relocation verification

After the coordinator performed relocation, independently rebuilt the complete relative file/directory manifest with direct hashlib SHA-256 reads and compared it with both saved before/after manifests. All seven files and four directories match exactly; aggregate manifest hash is `8117978eddf0313fa8829912725f2d84170db4a52f90f732aa9112090757f02a`. Old source and external root are absent. Read-only workflow show resolves the new Activity-local path and returns the exact saved projection: owner/run IDs unchanged, finished/feasible revision 4, projection not stale. Recomputed run manifest after show is unchanged. Evidence: independent-pilot-relocation-check.json. Reviewer performed no run mutation.
