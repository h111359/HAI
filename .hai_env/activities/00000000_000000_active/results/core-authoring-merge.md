# Core role and workflow authoring

Role and workflow definition maintenance now ships entirely in `.hai/`. The host follows these procedures directly; authoring requires no separately installed role, skill, registration or specialist model profile.

Start here:

- [Manage role definitions](../../../../.hai/procedures/manage-role-definitions.md)
- [Manage workflow definitions](../../../../.hai/procedures/manage-workflow-definitions.md)

The entry procedures preserve authoring responsibility and authority boundaries. Core conventions retain the methods and their indices; eight operation-specific procedures cover inspection, creation, revision and review. The definition-management concept and configurable-workflow authoring convention are also in core. Startup, concepts, affected conventions, execution guidance, tool documentation, collection READMEs and the introductory README point to built-in authoring.

## Preservation and retirement

All 14 source resources and their 14 installed counterparts were compared before removal. Their contents agreed apart from rebased links. Exact original bytes and the destination for each resource are retained in [the transfer record](../evidence/core-authoring-transfer.json). All 57 checked authoring rules remain in core after replacing specialist actors with the host. Authoring package selection metadata and standard/high specialist execution declarations are retired; core administration retains normal host policy. Optional settings ownership is stated consistently; settings-free roles need no contract.

Removed all four packages from both root collections and `.hai_env`: the role/workflow definition managers and role/workflow authoring skills. Removed the two installed catalogue rows. Historical migration transformations, manifests, Activity records and preserved snapshots retain their original identities. Unrelated installed resources are unchanged.

## Verification

- All 33 remaining source/installed definitions validate; startup and the registered-role audit pass.
- All 14 transferred document destinations exist and their actual local Markdown links resolve.
- All 57 checked role/skill authoring rules are accounted for in core.
- An isolated workspace containing only `.hai/` initialized and started with no registered roles. A newly authored role and the core workflow template passed structural validation without authoring packages. This proves mechanical availability and validation, not semantic quality or workflow execution.
- `git diff --check` passes. No runtime code was changed and no broad runtime test suite was needed or run.
- [Verification details and core hashes](../evidence/core-authoring-verification.json) include the actual best-effort recording result. No complete native transcript coverage is claimed.

The fixture is task-owned disposable verification material under work/test-work/core-authoring-only, retained for inspection. The original bytes, mapping, verification and this result are retained evidence. No commit or Activity closure was requested or performed.
