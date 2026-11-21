---
name: backlog-management
description: "Capture, import, maintain and prepare backlog items; preserve item identities, history, catalogue consistency and attributable completion evidence."
metadata:
  hai-settings-owner: "backlog-manager"
---

# Backlog management

Use this capability directly or under a suitable role. Follow actual task authority, workspace boundaries and applicable host instructions. A skill does not launch an agent, change model policy or grant permissions. In HAI-managed work, retain Activity ownership and report missing prerequisites; direct use does not require adopting the former role.

Settings have one owner: `backlog-manager`. Use `skills resolve` to validate the installed owner contract and read `.hai_env/config/roles/backlog-manager.json` once; absent values use that contract defaults, invalid values block dependent operations. Selecting this skill does not select the owner role.

## Method constraints

- **Workspace location.** The operator MUST keep the backlog at the configured workspace-relative directory; the directory MAY be outside `.hai_env/`.
- **Safe boundaries.** The operator MUST validate containment, directory types and protected-path overlaps before access and immediately before writes; it MUST reject linked backlog roots, item folders and item files, including links that remain inside the workspace.
- **Single authority.** The operator MUST use one selected backlog root per operation and MUST NOT merge discovered folders or silently change the configured root.
- **Individual items.** The operator MUST follow the backlog format, keeping each pending item in `new/` and each completed, cancelled or rejected item in `closed/`.
- **Catalogue consistency.** The operator MUST update the root catalogue after every authorized item creation, edit or status change and verify that it agrees with the item files.
- **Stable identities.** The operator MUST preserve item IDs across edits, moves and reopening and MUST NOT reuse an ID from either status folder.
- **Independent records.** The operator MUST keep imported items and the catalogue self-contained, without links, paths or dependencies on original draft files or their audit copies.
- **Preserved history.** The operator MUST append dated change history and preserve earlier decisions; preserved import copies MUST be placed only in the caller-assigned Activity audit directory, while material requirement revisions MUST retain their predecessor in `history/`.

## Procedures

| Procedure | Trigger | File |
| --- | --- | --- |
| Configure backlog | A backlog root needs initial setup or an explicit location change. | [Configure backlog](procedures/configure-backlog.md) |
| Maintain items | Items need capture, clarification, editing, closure, reopening or catalogue inspection. | [Maintain items](procedures/maintain-items.md) |
| Import drafts | The caller identifies draft material to convert into individual backlog records. | [Import drafts](procedures/import-drafts.md) |
| Prepare Activity input | A selected pending item is to become input for Activity work. | [Prepare Activity input](procedures/prepare-activity-input.md) |

## References

- [Backlog format](conventions/backlog_conv.md) — item, folder, catalogue and history contracts; required for all backlog operations.
- [Role configuration](../../.hai/conventions/role-configuration_conv.md) and [owned contract](../../roles/backlog-manager/configuration/contract.json) — required for settings and dependent work.
- [Role convention](../../.hai/conventions/role_conv.md) — host coordination and package boundaries; required for all work.
- [State convention](../../.hai/conventions/state_conv.md) — mandatory instructions and protected paths; required before workspace access.
- [Activity convention](../../.hai/conventions/activity_conv.md) and [runtime commands](../../.hai/tools/runtime/README.md) — required for Activity context and handoff; runtime owns Activity writes.
- [Configuration tools](../../.hai/tools/configuration/README.md) — required before loading settings.
- [Audit helper](scripts/README.md) — required before running the read-only backlog auditor or its tests.
