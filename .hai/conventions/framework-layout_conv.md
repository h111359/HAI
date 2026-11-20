# Framework layout

The [artifact placement contract](artifact-placement_conv.md) governs all HAI work,
not just framework packages. Product/project/operational outputs retain their
established locations; task working material and run evidence stay with their
owning Activity/invocation unless explicitly designated otherwise. A layout
convention does not itself authorize relocating existing material.

Environment configuration is grouped under `.hai_env/config/`: mandatory
`state.json` and `agent_instructions.md`, optional `model_profiles.json`, and
owner settings below `roles/` and workflow location settings below `workflows/`. Explicit layout migration retains recovery
copies below `config/migration-backups/` and `config/layout-migration.json`.

Optional single-file workflow definitions live directly in `.hai_env/workflows/`.
Their dedicated run records/artifacts live in `<activity>/workflow-runs/<run-id>/`.
The runtime resolves the containing Activity through its immutable ID; no extra
Activity-ID directory or separate environment run root is used. Activity archival
moves its runs with it and makes them read-only through the closed owner; exports
and retention include the contained run directories. The definitions root and
legacy external run root remain protected from conflicting store configuration.
The [workflow convention](workflow_conv.md) and [run convention](workflow-run_conv.md)
define their ownership and formats; no workflow catalogue or global current pointer exists.

`.hai/` contains the reusable Python runtime in `tools/`, shared concepts in `concepts/`, conventions in `conventions/`, state contract in `contracts/state.json`, and initialization defaults in `templates/state.json`. `.hai/start.md` is the host entry instruction. `.hai_env/` contains workspace-specific state, fixed instructions, Activity records, optional installed extensions and their settings. Upgrades must preserve workspace data and follow the [state convention](state_conv.md).

Optional workspace role packages live at `.hai_env/roles/<name>/` and their explicit registration catalogue at `.hai_env/roles/catalogue.md`. Their reusable source packages under root `roles/` are data, not a runtime execution origin. A package's settings are stored separately in `.hai_env/config/roles/`; source changes do not automatically replace installed packages. See [role convention](role_conv.md) and [role configuration](role-configuration_conv.md).

Activity records use the configured store and the shared [Activity convention](activity_conv.md). Core source-backed recording lives in `tools/chronicles/` and runtime; see [chronicles](chronicles_conv.md) and [recording evidence](recording-evidence_conv.md). Explicit source assignment remains the host’s responsibility.

New Activities use layout 2: README.md at root; operational records under system/;
review outputs in results/, retained proof in evidence/, prior versions in history/,
and disposable material in work/. Human instructions persist in typed chat even
when chronicles are disabled. Existing archives retain layout 1 until explicit
compatible migration. See the Activity convention for exact generation/cleanup rules.

Reusable source collections are root roles/, skills/ and workflows/. Role folders
live directly under roles/; there is no second roles/ level. Installed capabilities
are copied separately into .hai_env/roles/ and .hai_env/skills/, and workflow
definitions into .hai_env/workflows/. Skills use SKILL.md; roles use ROLE.md.
Presence of source data grants no runtime fallback, execution or installation
authority. Workflow installation collects the actual human-selected output bases;
configuration is environment-specific and generated run material belongs to the
owning Activity or explicitly configured run destinations under the workflow contract.

## Core definition authoring

Core role/workflow authoring methods live in procedures/, conventions/ and concepts/ under .hai/. They ship with the core and require no optional authoring packages. Start with [role management](../procedures/manage-role-definitions.md) or [workflow management](../procedures/manage-workflow-definitions.md).

## Complete role packages and independent skills

Roles may contain job-specific procedures, conventions, scripts and templates, and may omit skill dependencies. ROLE.md remains a concise entry point to those resources. Skills package independently usable capabilities and receive explicit caller context; resource file type does not decide ownership. See [authoring ownership](role-authoring_conv.md#ownership-and-extraction-checks). Existing installed/source packages and settings remain unchanged until separately authorized refactoring.
