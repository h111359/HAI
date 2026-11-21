# Portable HAI core ? completed fix

HAI can initialize and operate in a workspace containing only `.hai/`. Initialization creates `.hai_env/`; no development collection or other project-root file is required. Default operations do not discover, create, reserve or check unrelated workspace folders.

## What changed

- Startup and role readiness inspect internal legacy/installed locations only. Ordinary root names such as `roles`, `skills` and `workflows` no longer become implicit HAI resources or prevent a caller from selecting custom stores. Security protections and contained-path checks remain in force.
- Core concepts, conventions, authoring instructions and tool documentation use installed definitions or explicitly selected sources. Required skills resolve from `.hai_env/skills/`; there is no source-library fallback.
- Role/skill installation accepts explicit `source_mappings` for peer references. Missing external mappings fail before probing undeclared targets. Own-package, core and environment references retain their supported behavior. Existing source packages are preserved.
- Optional `.hai_env/config/workspace-paths.json` can declare workspace-specific package reference paths: `{"workspace_paths_format":1,"references":["project/policies"]}`. This file is not created or required by default. Declaring paths does not inspect them during startup, grant execution authority, or replace settings owned by stores/workflows.
- Legacy source-library migration requires explicit `legacy_source`; internal naming conversion remains available without any external collection. Historical markers, backups and records retain their interpretation.
- Distributed tests use bundled fixtures. Actual development-library integration requires explicit `HAI_DEVELOPMENT_SOURCES`; default tests do not check for development folders before skipping. The documented runner supplies its contained temporary root to children.
- The complete core now includes `.hai/LICENSE`, identical to the existing repository license. Installation instructions require only the complete `.hai/` folder, including that attribution file.

## Verification

| Check | Result |
| --- | --- |
| Fresh copied-core initialization | Passed; only `.hai/` and `.hai_env/` at workspace root |
| Instrumented default filesystem boundary | Passed; default initialize/startup/readiness/skills/Activity operations reject unintended sibling stat/lstat probes |
| Unrelated root names, explicit custom store, source mapping and configured reference contracts | Passed in 4 boundary regressions |
| Copied-core regression suite | 31 modules, 579 tests including 38 skips; every executed test passes after the focused runner rerun described below |
| Explicit development integration | Skills 28 tests/1 skip, source staging 6/0, workflow installation 6/1; passed |
| Documented runner in isolated installation | Skills suite passed: 28 tests/5 skips |
| Current workspace startup | Valid, no issues |
| Attribution and whitespace | Bundled license matches; git diff --check passes |
| Independent review | Passed; no blocking findings or outstanding reviewer writers |

The first full copied-core run encountered Windows `WinError 267` in the runner regression because its nested fixture working directory was too long. The same four-test module passed from a shorter Activity-owned copied-core fixture. This is not proof of unrestricted deep-path portability. Initial failures and subsequent passing results are retained; skips cover optional development integrations and platform-dependent cases. Development checks initially exposed missing explicit test mappings; those were corrected and rerun successfully.

Review used invocation `fa07ac57-89a6-450b-a789-28425d0b4189` (`/root/deployment_boundary_review`), allocated before delegation. The reviewer performed no writes/background work and provided no attributable usage-source identity. No usage was invented.

## Evidence

- [Clean initialization](../evidence/core-boundary-fix/clean-initialize.json)
- [Full copied-core results, including original runner failure](../evidence/core-boundary-fix/deployed-tests.json)
- [Focused boundary, skills and legacy checks](../evidence/core-boundary-fix/focused-tests.json)
- [Runner rerun and corrected role integrations](../evidence/core-boundary-fix/final-follow-up.json)
- [Final development workflow integration](../evidence/core-boundary-fix/final-development-workflow.json)
- [Documented runner](../evidence/core-boundary-fix/documented-runner.json)
- [Current startup](../evidence/core-boundary-fix/current-startup.json)
- [Original review and reproductions](core-boundary-review.md)

The root development collections, installed packages, user settings and historical migration records were not replaced or deleted. External locations remain possible only as explicit task/configuration choices. The Activity remains open; no commit was requested.
