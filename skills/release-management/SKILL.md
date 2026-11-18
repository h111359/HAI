---
name: release-management
description: "Assess an exact release candidate, prepare versioned metadata and packages, verify readiness and reconcile authorized publication evidence."
---

# Release management

Use this capability directly or under a suitable role. Follow actual task authority, workspace boundaries and applicable host instructions. A skill does not launch an agent, change model policy or grant permissions. In HAI-managed work, retain Activity ownership and report missing prerequisites; direct use does not require adopting the former role.

## Method constraints

- **Release contracts:** The operator MUST apply the three local contracts and the owning environment-state declaration to release data and readiness.
- **Independent versions:** The operator MUST keep bundle SemVer and core state-format versions separate.
- **Manifest meaning:** The operator MUST NOT treat a manifest's shipped targets as evidence that a consumer was migrated.
- **Exact source:** The operator MUST tie released assets to one recorded exact source commit and export.
- **Candidate declarations:** The operator MUST NOT substitute installed working-tree metadata for evidence from the candidate source.
- **Consumer information:** The operator MUST disclose relevant state-format differences, required environment migrations and limitations.
- **Result state:** The operator MUST distinguish prepared, draft, published, failed and unverified results.

## Procedures

| Procedure | Trigger | File |
| --- | --- | --- |
| Establish the candidate | A HAI bundle release assessment, version recommendation or candidate is requested. | [Establish the candidate](procedures/establish-candidate.md) |
| Prepare and verify | An assessed candidate has authority for source metadata, package preparation or requested automation. | [Prepare and verify](procedures/prepare-and-verify.md) |
| Publish and reconcile | A ready frozen candidate needs publication handoff or returned publication evidence needs review. | [Publish and reconcile](procedures/publish-and-reconcile.md) |

## References


- [Release policy](conventions/release_conv.md) — bundle versioning and readiness — required for every release.
- [Contract versioning](conventions/contract-versioning_conv.md) — references to owning compatibility rules and release dependencies — required for every release.
- [Publishing policy](conventions/publishing_conv.md) — packaging, authority, GitHub, and recovery — required for every release.
- [Role convention](../../.hai/conventions/role_conv.md) — receiver checks, role boundaries, and references — required for all operations.
- [Git-manager](../../roles/git-manager/ROLE.md) — required registered workspace extension for Git/GitHub execution and its configuration/gates; host coordinator performs routing, do not adopt or invoke that role.
- [State convention](../../.hai/conventions/state_conv.md) — state-format authority and configured context — required for release contract checks; conditional when interpreting environment state.
- [State contract](../../.hai/contracts/state.json) — installed target to snapshot and verify against the candidate's own declaration — required for every release.
- [Tooling convention](../../.hai/conventions/tooling_conv.md) — runtime and helper requirements — conditional when executing, creating, or changing supporting Python tools.
- [term:Bundle] → [Release candidate](concepts/release.md) — required when assessing the corresponding release identity or authority.
- [term:Candidate] → [Release candidate](concepts/release.md) — required when assessing the corresponding release identity or authority.
- [term:Bundle version and release-manifest contract targets] → [Release candidate](concepts/release.md) — required when assessing the corresponding release identity or authority.
- [term:Release authority] → [Release candidate](concepts/release.md) — required when assessing the corresponding release identity or authority.
