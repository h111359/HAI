# Installing and upgrading HAI

The [0.4.0 release notes](release-notes/0.4.0.md) and earlier release manifests describe their recorded package versions; current workspace changes do not republish those artifacts. Actual publication status is tracked on [GitHub Releases](https://github.com/h111359/HAI/releases). Published [0.1.0](release-notes/0.1.0.md), [0.2.0](release-notes/0.2.0.md), and [0.3.0](release-notes/0.3.0.md) retain their own compatibility targets.

Download the HAI release ZIP from the **Assets** section of the [latest release](https://github.com/h111359/HAI/releases/latest), then extract it. Git and a repository clone are not required for normal installation.

HAI requires Python 3.11 or later and a host that can read workspace instructions and run commands. Optional agent invocation, models and integrations depend on the host; installing HAI does not establish those capabilities. Copy the complete reusable `.hai/` tree into the workspace, retaining the license and avoiding unrelated project files, and direct the host to [.hai/start.md](.hai/start.md). The runtime entry point and operation contracts are documented in [runtime commands](.hai/tools/runtime/README.md). It is not a background service or an automatically installed Python package.

Before replacing an existing framework, preserve the workspace's `.hai_env/`, configured Activity and specification data, and product files. A framework upgrade does not itself migrate state, records or transcripts. Current state format is 3; supported format 2 is read-only migration context. Preserve invalid, unsupported or conflicting state and use only an explicitly authorized migration after reviewing its inputs and backup/partial-result behavior. See the [state convention](.hai/conventions/state_conv.md) and [Activity migration notes](release-notes/activity-migration.md). Preserve Activity IDs, human inputs, revisions and transcript provenance through an upgrade.

Optional workspace extensions are separate complete packages under `.hai_env/roles/`, with explicit entries in its catalogue. Golden source packages in root `roles/` are data; they do not execute from the source library. Installation, replacement, registration and execution are separate actions. Preserve local modifications and external settings at `.hai_env/config/roles/`, review replacement differences, and do not infer enabled capabilities or permission from a package being present. Core startup and administration require no optional extension or model profile. See [role configuration](.hai/conventions/role-configuration_conv.md).

## Upgrading the environment layout in 0.4.0

The canonical fixed files are `.hai_env/config/state.json`,
`.hai_env/config/agent_instructions.md`, and optional
`.hai_env/config/model_profiles.json`. Existing files directly under `.hai_env/`
are migration inputs, never fallback runtime authorities.

After preserving local changes and replacing the reusable core, follow the
[layout migration procedure](.hai/procedures/migrate-environment-layout.md).
Safely read and apply the legacy instructions first, stop other environment
writers, and prepare a workspace-contained JSON request with the actual migration
instruction identified in `provenance.source` and a meaningful `provenance.reason`.
Using a verified absolute Python 3.11+ executable, preview:

```text
<absolute-python> -B .hai/tools/hai.py environment migrate-layout --workspace . --request <workspace-contained-request.json>
```

Only after explicit authorization and review of hashes/moves, repeat with
`--apply`, inspect recovery copies and `config/layout-migration.json`, then run
startup and reload canonical instructions. The migration preserves exact bytes;
it does not convert state format or move Activities/specifications. Mixed layouts,
conflicts, unexplained locks and partial operations require reviewed resolution,
not automatic merging or retry. Format-2 specification extraction remains a
separate explicitly authorized operation after layout migration.

## Work and output boundaries

For Windows and Linux interpreter invocation, path formats, recording setup and
verification, see [runtime portability](.hai/tools/runtime/PORTABILITY.md).

Apply the shared [workspace boundary](.hai/conventions/workspace-boundary_conv.md)
and [artifact placement contract](.hai/conventions/artifact-placement_conv.md).
Outside file writes require explicit user location/purpose permission, including
temporary files and tool effects. Requested outputs retain their canonical
destinations; task scratch, run results and review evidence stay with their owning
Activity/invocation unless a governing contract designates otherwise.

The core ZIP does not install optional roles. To obtain updated optional packages,
download the exact release source archive and use its `roles/`, `skills/` and `workflows/`
collections, then follow runtime preview/apply installation and registration. Preserve
external settings and review existing local differences before replacement.

Existing projects with HAI agent packages require the explicit [role migration](.hai/procedures/migrate-roles.md) after updating the core. HAI roles use ROLE.md; actual skills keep SKILL.md. The migration preserves customized installed packages separately from library sources and keeps historical Activity records unchanged.

## Roles, skills and workflows

Source collections are flat roles/ packages, skills/ packages with SKILL.md and
workflows/ single-file definitions. Download the chosen release source archive
when these optional resources are needed; the core release ZIP does not implicitly
install or activate them. Preserve local installed variants before updates.

Roles define responsibility and select skills; skills can also be used directly.
The installed environment uses .hai_env/roles/, .hai_env/skills/ and
.hai_env/workflows/. Skill methods and templates are not copied into every role.
Settings retain a single actual owner. Follow the runtime installation commands
and inspect previews before apply. Missing dependencies block affected work.

A workflow installation preview lists the output locations to choose, their purpose
and expected contents. Ask the human for those workspace-relative base folders
before apply; do not invent saved choices or launch a run during installation.
Each run uses a separate folder, and step executions receive distinct intermediate
names. Accepted evidence and input lineage remain with the Activity. Historical
records and existing settings are preserved by explicit reviewed migration.
