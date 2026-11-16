# Independent review: HAI roles and explicit migration

The reviewed solution is ready. I found no remaining blocking defect in the role rename, migration safeguards, or historical-record compatibility after the fixes described below.

This review was performed by the separate reviewer invocation `25cb7baf-796c-4ae5-a618-0ab6ec90db75`, independently of the implementation authors. The reviewer made no maintained-source, installed-package, live-configuration, workflow-definition, or canonical Activity changes. Test fixtures were confined to this invocation's `test-work/` folder.

## Reviewed behavior

- HAI role packages use `ROLE.md`, `.hai_env/roles`, `.hai_env/config/roles`, `hai_roles_library/roles`, and the role-definition-manager identity. Genuine skills retain `SKILL.md`; actual AI agents, native agent-tool folders, chat speaker values, and execution work folders retain their meanings.
- Live role operations require the new conventions. Explicit migration has a preview snapshot, actual ended-writer attestation, exclusive publication, exact original backups, retained partial evidence, and no automatic retry or replacement of local customizations.
- Configuration contracts use format 3 with `role`; saved-setting format versions and values remain independent. New workflow definitions use format 2 and Role sections; historical pinned format-1 definitions remain inspectable without changing their raw hashes.
- Startup remains usable without optional roles. Core administration can diagnose a legacy or incomplete role migration; role-dependent operations do not silently accept mixed naming.

## Important findings resolved during review

1. The old Activity-layout invocation location `files/agent-invocations` remains readable. Legacy workflow completion cannot fall through into new-role validation and append an accidental rejection.
2. Contracts consistently require format 3. Retired state keys and legacy role roots are rejected or reserved appropriately. Old runtime imports were repaired.
3. Migration preserves installed and library packages independently, arbitrary saved settings, installed-only packages, genuine nested skills, and exact original bytes. Package self-links, peer links, fragment links, and source-library paths now follow the new entry filenames.
4. Migration distinguishes direct execution metadata from arbitrary artifacts named `state.json`, and refuses unresolved or orphan workflow runs.
5. Validated candidate bytes, unchanged dependencies, retained originals, recreated legacy roots, and the migration marker receive drift checks through publication. Incomplete publication leaves a blocking partial marker and recovery evidence.
6. Direct migration calls validate supported core state and mandatory instructions. The tested legacy core-2 and Activity-layout-1 upgrade order remains possible before specification-settings extraction.
7. A custom role named `leader` now follows the ordinary role metadata and model-resolution contract; it does not inherit the obsolete built-in host-package exception.

## Independent verification

| Check | Result |
| --- | --- |
| Role definition broad suite | 80 tests, 6 skipped, no failures or errors |
| Configuration suite | 15 tests, 3 skipped, no failures or errors |
| Startup suite after repairs | 67 tests, 8 skipped, no failures or errors |
| Workflow and invocation suites | 56 tests, 3 skipped, no failures or errors |
| Final migration broad suite plus later fragment regression | 15 tests plus 1 focused test, all passed |
| Final custom-leader contract checks | 2 focused tests, all passed |
| Complete copied-package migration | Preview and apply succeeded in an isolated copy; 11 installed roles and the workspace-only advisor survived |
| Live local Markdown references | 1,336 links checked across core, installed roles, and library; no missing local targets |

The final implementation authors' complete regression counts are recorded separately by the coordinator; the table above records tests actually run by this reviewer. Skips concerned filesystem-link capabilities unavailable in this Windows environment. Linux and macOS were not executed by this reviewer.

## Actual migration preservation

The live migration completed with ID `0bd5b865-72ce-4f6f-8da0-7a400bb8a490`. Independent SHA-256 comparisons against the pre-migration reviewer baseline found no differences in:

- 992 closed-Activity files;
- 3 genuine-skill files;
- mandatory global AI-agent instructions and model-profile settings;
- both saved role-configuration files, at their new locations;
- all 136 original installed-package files, 134 library files, and 2 reusable workflow files retained in the migration backup.

The installed collection contains 11 role packages; the library contains 10. The workspace-only hai-framework-advisor remains installed-only. Installed and library definition-manager packages still differ in the same five relative files, with the entry renamed from `SKILL.md` to `ROLE.md`. All 21 package metadata mappings exactly match their original mappings, including model and effort declarations.

The retained real workflow pilot `e1e8a718-d108-49ea-bec5-24572793827b` was inspected through the current runtime after migration. Inspection succeeded with status finished, pinned workflow format 1, no issues, and no changed files.

The supporting `preservation-baseline.json` is a reviewer-generated hash inventory, not runtime state or a new framework registry.

## Limits and handoff

The review establishes repository behavior and preservation on this Windows workspace. It does not claim execution on other operating systems, unavailable symlink privileges, or a new real AI-provider workflow run. No external publication, commit, release, or Activity closure was performed by the reviewer.

All reviewer fixture processes have ended. The reviewer has no live package, configuration, workflow, or source writers. After this report is written, no reviewer filesystem writes remain pending.
