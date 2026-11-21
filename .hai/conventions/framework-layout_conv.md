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

Optional workspace role packages live at `.hai_env/roles/<name>/` and their explicit registration catalogue at `.hai_env/roles/catalogue.md`. Reusable sources are optional caller-selected packages, not a runtime execution origin. A package's settings are stored separately in `.hai_env/config/roles/`; source changes do not automatically replace installed packages. See [role convention](role_conv.md) and [role configuration](role-configuration_conv.md).

Activity records use the configured store and the shared [Activity convention](activity_conv.md). Core source-backed recording lives in `tools/chronicles/` and runtime; see [chronicles](chronicles_conv.md) and [recording evidence](recording-evidence_conv.md). Explicit source assignment remains the host’s responsibility.

New Activities use layout 2: README.md at root; operational records under system/;
review outputs in results/, retained proof in evidence/, prior versions in history/,
and disposable material in work/. Human instructions persist in typed chat even
when native sources are unavailable. Existing archives retain layout 1 until explicit
compatible migration. See the Activity convention for exact generation/cleanup rules.

Only `.hai/` and `.hai_env/` are fixed workspace roots. A new workspace needs
only the complete `.hai/` tree; initialization creates `.hai_env/`. No other
workspace directory, library or file is required, created or probed by default.

Installed roles, skills and workflow definitions live below `.hai_env/`. Source
packages and definitions are optional task inputs at explicitly selected locations;
there is no universal source-library layout. Configured Activity stores, product
stores and workflow outputs may use other authorized workspace locations. Core
may inspect those particular locations only because configuration or the current
assignment identifies them. Configuration remains in `.hai_env/config/`; no
additional configuration file is mandatory for an ordinary installation.

Source inspection resolves required skills only from installed `.hai_env/skills/`.
Installation rebases own-package links and preserves core/environment links. Peer
source links require explicit `source_mappings` in the installation request, with
workspace source paths mapped to specific installed role/skill package paths.
Missing mappings fail before checking unrelated reference targets. No catalogue,
automatic source search, fallback or implicit installation is introduced.

## Core definition authoring

Core role/workflow authoring methods live in procedures/, conventions/ and concepts/ under .hai/. They ship with the core and require no optional authoring packages. Start with [role management](../procedures/manage-role-definitions.md) or [workflow management](../procedures/manage-workflow-definitions.md).

## Complete role packages and independent skills

Roles may contain job-specific procedures, conventions, scripts and templates, and may omit skill dependencies. ROLE.md remains a concise entry point to those resources. Skills package independently usable capabilities and receive explicit caller context; resource file type does not decide ownership. See [authoring ownership](role-authoring_conv.md#ownership-and-extraction-checks). Existing installed/source packages and settings remain unchanged until separately authorized refactoring.

## Explicit external package references

A workspace-specific package may link to project policies or other resources
outside the fixed roots only when their paths are explicitly declared in optional
.hai_env/config/workspace-paths.json. Its schema is
{"workspace_paths_format":1,"references":["project/policies"]}.
Paths are contained workspace-relative files/directories. No referenced path is
inspected until the selected package actually needs it. Without this configuration
there is no external reference allowlist and no file is created automatically.
This declares structural references, not execution permissions or permission to
read secrets. Existing workflow/product/store location settings retain their own
owners and need no duplicate entry merely to operate on those configured stores.

Current recording text lives only in system/chat.jsonl; system/recording.json holds references and progress. Explicit legacy recording migration retains original transcript/metadata trees under history/recording/. No new root chronicles folder is generated for layout-2 recording.
