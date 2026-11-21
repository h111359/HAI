# Activity log

- 2026-11-21T07:40:47Z Created Activity (source: user request; reason: Implement the agreed workflow file and run discovery changes).

- 2026-11-21T08:04:44Z — Implemented format-4 file inventories, per-run bindings and Activity workflow discovery. Preserved exact format-2 predecessor definitions under history/workflow-definitions. Validated both registered definitions and the template. Main suite ran 85 tests with one Windows symlink skip. Eight integration and migration tests passed. Focused parser and runtime checks on the latest edits ran 28 tests with the same skip. A separate CLI process discovered the same ready run after launch. Reproduced the pre-existing no-source archival failure on HEAD and confirmed that matching the synchronization and verification warnings resolves it. (source: local verification; reason: Record workflow implementation and checks).

- 2026-11-21T08:22:38Z — Enabled default JSON-only Activity usage. Verified the official Standard-speed price lookup and captured rates for the configured models in this Activity. Usage remains unavailable without an assigned source. Ran 76 tests with 74 passes and two platform skips. (source: local runtime verification; reason: Record the JSON-only usage implementation and validation).

- 2026-11-21T08:54:23Z — Added per-turn retry for unbound host session discovery. Verified unavailable, later discovery, explicit binding and no discovery after binding. Ran 41 recording and usage tests with two platform skips. (source: local verification; reason: Verify per-turn session discovery and refresh usage).

- 2026-11-21T09:27:44Z — Added the HAI-wide user communication convention and plain-language notices for usage, recording, and missing workflow file locations. Verification ran 45 focused tests with two platform skips. Two additional startup and retry checks passed. (source: local verification; reason: Record and verify plain-language user notices).
