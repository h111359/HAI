# Framework layout

The [artifact placement contract](artifact-placement_conv.md) governs all HAI work,
not just framework packages. Product/project/operational outputs retain their
established locations; task working material and run evidence stay with their
owning Activity/invocation unless explicitly designated otherwise. A layout
convention does not itself authorize relocating existing material.

Environment configuration is grouped under `.hai_env/config/`: mandatory
`state.json` and `agent_instructions.md`, optional `model_profiles.json`, and
role-owned files below `agents/`. Explicit layout migration retains recovery
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

Optional workspace role packages live at `.hai_env/roles/<name>/` and their explicit registration catalogue at `.hai_env/roles/catalogue.md`. Their reusable source packages under `hai_roles_library/roles/` are data, not a runtime execution origin. A package's settings are stored separately in `.hai_env/config/roles/`; source changes do not automatically replace installed packages. See [role convention](role_conv.md) and [role configuration](role-configuration_conv.md).

Activity records use the configured store and the shared [Activity convention](activity_conv.md). Core source-backed recording lives in `tools/chronicles/` and runtime; see [chronicles](chronicles_conv.md) and [recording evidence](recording-evidence_conv.md). Explicit source assignment remains the host’s responsibility.

New Activities use layout 2: README.md at root; operational records under system/;
review outputs in results/, retained proof in evidence/, prior versions in history/,
and disposable material in work/. Human instructions persist in typed chat even
when chronicles are disabled. Existing archives retain layout 1 until explicit
compatible migration. See the Activity convention for exact generation/cleanup rules.
