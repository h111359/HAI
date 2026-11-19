# Source collection cleanup

The human accepted the proposed skill/role/framework boundaries and authorized tidying the source collections before individual portability refactors.

## Removed from source only

- `roles/release-manager/`: specifically prepares HAI product releases.
- `skills/release-management/`: HAI bundle contracts, packaging and release methods.

Both remain installed. The role remains registered. All nine source resource files had installed counterparts with unchanged content apart from rebased Markdown links. Checks and hashes were retained before removal.

## Renamed reusable administration sources

| Previous source identity | Current source identity |
| --- | --- |
| `roles/role-definition-manager` | `roles/hai-role-definition-manager` |
| `roles/workflow-definition-manager` | `roles/hai-workflow-definition-manager` |
| `skills/role-authoring` | `skills/hai-role-authoring` |
| `skills/workflow-authoring` | `skills/hai-workflow-authoring` |

The human explicitly chose to keep these cross-workspace HAI administration capabilities and accepted `hai-` instead of `hai_` to conform to existing name rules. Canonical names, role skill declarations, links and relevant self-references were updated. Installed identities were not migrated.

All other source packages remain reusable across HAI workspaces. HAI references in their methods remain for future, separately scoped portability refactors. `skills/crete-design-package` is not installed and was preserved unchanged. The workspace-only advisor was already installed-only and required no source removal.

Collection READMEs now state the inclusion/preservation rules and distinguish the renamed source identities from existing installed packages.

## Verification

- All 41 source and installed role/skill definitions validate.
- All 140 installed role/skill resource files retain their original hashes, with no additions/removals.
- All three files in the uninstalled design skill retain their earlier audit hashes.
- All actual local Markdown link targets in the source collections exist. A catalogue example inside a fenced code block is illustrative and excluded.
- `git diff --check` passes. No runtime, workflow, configuration or installed package was changed.
- No new tests were added or broad test suite run: this is package organization and metadata/link maintenance, checked through the existing validators and preservation audit.
- Best-effort chronicles synchronization was attempted; its actual result is retained in the verification evidence. No complete native transcript coverage is claimed.

See [preservation evidence](../evidence/collection-cleanup-preservation.json) and [verification](../evidence/collection-cleanup-verification.json).
