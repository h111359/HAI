# Activity log

- 2026-11-21T07:40:47Z Created Activity (source: user request; reason: Implement the agreed workflow file and run discovery changes).

- 2026-11-21T08:04:44Z — Implemented format-4 file inventories, per-run bindings and Activity workflow discovery. Preserved exact format-2 predecessor definitions under history/workflow-definitions. Validated both registered definitions and the template. Main suite ran 85 tests with one Windows symlink skip. Eight integration and migration tests passed. Focused parser and runtime checks on the latest edits ran 28 tests with the same skip. A separate CLI process discovered the same ready run after launch. Reproduced the pre-existing no-source archival failure on HEAD and confirmed that matching the synchronization and verification warnings resolves it. (source: local verification; reason: Record workflow implementation and checks).
