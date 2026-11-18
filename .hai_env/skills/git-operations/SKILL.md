---
name: git-operations
description: "Inspect and operate Git repositories and GitHub resources within actual authorization; validate selected integration settings and preserve unrelated work."
metadata:
  hai-settings-owner: "git-manager"
---

# Git operations

Use this capability directly or under a suitable role. Follow actual task authority, workspace boundaries and applicable host instructions. A skill does not launch an agent, change model policy or grant permissions. In HAI-managed work, retain Activity ownership and report missing prerequisites; direct use does not require adopting the former role.

Settings have one owner: `git-manager`. Use `skills resolve` to validate the installed owner contract and read `.hai_env/config/roles/git-manager.json` once; absent values use that contract defaults, invalid values block dependent operations. Selecting this skill does not select the owner role.

## Method constraints

- **Git commands:** The operator MUST require enabled Git integration for every Git repository command, including inspection, export, fetch and push.
- **Service operations:** The operator MUST require enabled GitHub integration for GitHub connector, API and CLI operations.
- **Combined operations:** The operator MUST require both integrations when an operation uses both local Git and GitHub service operations.
- **Remote transport:** The operator MUST NOT require GitHub service integration solely because a Git command targets a GitHub remote.
- **Initialized environment:** The operator MUST require a usable initialized HAI environment before repository operations.
- **Local settings:** The operator MUST use locally validated extension settings rather than expect Git settings from core startup.
- **Unavailable integration:** The operator MUST stop only the operations that need a missing, disabled or invalid integration setting.
- **Independent diagnosis:** The operator MAY diagnose tools and configuration without enabling an unavailable repository capability.
- **No diagnostic bypass:** The operator MUST NOT perform a blocked repository operation under the name of diagnosis.
- **Push settings:** The operator MUST require valid enabled automated-push settings and permission for the requested update before an agent-executed push.
- **Manual push status:** The operator MUST return manual-push or setup status through host coordinator when automated push is off, absent or invalid.
- **No push bypass:** The operator MUST NOT bypass push restrictions through an API, connector, alternate transport or recreated remote ref.
- **Push request limits:** The operator MUST NOT treat a push request alone as permission to change saved settings or publish a release.
- **Repository identity:** The operator MUST verify the remote, default branch, signed-in account and authentication method rather than assume them from names such as `origin` or `main`.
- **Service tool choice:** The operator MAY choose a capable available connector or a sufficient installed CLI/API for the requested service operation; a capable connector is the default.
- **Installed Git:** Before enabling automated push, The operator MUST verify that Git and the chosen transport tools work for the selected repository.
- **Unattended authentication:** Before enabling automated push, The operator MUST verify that the chosen HTTPS or SSH authentication works without interactive prompts.
- **Remote write access:** Before enabling automated push, The operator MUST verify that the authenticated account has write access to the selected remote repository.
- **Push without force:** Before enabling automated push, The operator MUST verify that the requested target refs can be updated without force.
- **Fresh setup checks:** The operator MUST use checks made for the requested setup and actual repository/remote rather than reuse another setup's readiness result.
- **Checks before each push:** The operator MUST recheck current tooling, authentication, write access and branch requirements before each real push.
- **Read-only access:** The operator MUST NOT treat read access alone as proof of permission to update the remote repository.
- **Dry-run side effects:** The operator MUST review the effects of hooks and the dry-run itself before using a dry-run to check push access.
- **Dry-run choice:** The operator MAY use a safe `git push --dry-run` with explicit refs and no interactive prompts to check remote update access after reviewing the hooks.
- **No test push:** The operator MUST NOT send a real push merely to test push access or readiness.
- **Dry-run limits:** The operator MUST NOT claim that a successful dry-run guarantees a later real push will pass server hooks, branch protections or access checks.
- **Chosen settings:** The operator MUST NOT change a supported Boolean under `settings.git` or `settings.github` unless the user chose that change; an explicitly authorized legacy extraction preserves the existing choices without re-enabling them.
- **Other saved data:** The operator MUST preserve all other root and nested configuration values, including unknown properties and the configuration-format version, when changing chosen settings; core state remains untouched except during explicit legacy extraction.
- **Legacy extraction:** The operator MUST preserve complete legacy `integrations.git` and `integrations.github` subtrees, reject conflicting destinations, preserve recoverable prior bytes and verify the destination before removing only those old keys under explicit migration authority.
- **Invalid setting structure:** The operator MUST have explicit permission to repair a setting with an invalid data type or missing required fields before replacing it.
- **No saved readiness:** The operator MUST NOT store live readiness evidence in settings.

## Procedures

| Procedure | Trigger | File |
| --- | --- | --- |
| Configure integrations | Explicit Git/GitHub or automated-push setup, validation or scoped repair is requested. | [Configure integrations](procedures/configure-integrations.md) |
| Inspect repository discovery boundaries | Explicitly bounded repository-aware discovery or targeted ignore evidence is requested. | [Inspect repository discovery boundaries](procedures/inspect-discovery.md) |
| Operation workflow | A Git/GitHub operation or requested automated-push assessment is needed. | [Operation workflow](procedures/operate.md) |
| Commits and local changes | The requested operation stages or commits changes, produces a commit, or exports an exact commit. | [Commits and local changes](procedures/commit-and-export.md) |
| Branches, synchronization, and conflicts | Branch/ref changes, fetch, pull, merge, rebase, conflict resolution, push, or requested push enablement assessment is needed. | [Branches, synchronization, and conflicts](procedures/synchronize.md) |
| GitHub collaboration and checks | Requested GitHub PR, issue, check or workflow work is needed. | [GitHub collaboration and checks](procedures/collaborate.md) |
| Tags, releases, and recovery | Authorized tag/release execution or recovery from partial repository/service failure is needed. | [Tags, releases, and recovery](procedures/release-and-recover.md) |

## References

- [Role configuration](../../../.hai/conventions/role-configuration_conv.md) and [owned contract](../../roles/git-manager/configuration/contract.json) — required for role configuration, validation and dependent work; no workspace file is needed when declared defaults suffice.

- [Role convention](../../../.hai/conventions/role_conv.md) — receiver checks and host coordinator-only routing — required for all tasks.
- [State convention](../../../.hai/conventions/state_conv.md) — shared core assurance and legacy extraction preservation — required for dependent HAI work and state extraction.
- [Startup helper](../../../.hai/tools/startup/README.md) — core environment assurance only; it does not validate extension settings — conditional when interpreting core helper output.
- [Tooling convention](../../../.hai/conventions/tooling_conv.md) — Python runtime and helpers — conditional when executing or changing supporting Python tools.
- Current installed tool help and official Git/GitHub documentation — command behavior and service limits — conditional when needed for the selected operation.
- [term:Git integration] → [Git operations](concepts/git-operations.md) — required when the corresponding gate, candidate or commit context applies.
- [term:GitHub integration] → [Git operations](concepts/git-operations.md) — required when the corresponding gate, candidate or commit context applies.
- [term:Automated push] → [Git operations](concepts/git-operations.md) — required when the corresponding gate, candidate or commit context applies.
- [term:Operation authority] → [Git operations](concepts/git-operations.md) — required when the corresponding gate, candidate or commit context applies.
- [term:Frozen release candidate] → [Git operations](concepts/git-operations.md) — required when the corresponding gate, candidate or commit context applies.
- [term:Pre-commit chronicle verification] → [Git operations](concepts/git-operations.md) — required when the corresponding gate, candidate or commit context applies.
- [Git configuration contract](conventions/git-configuration_conv.md) — independent switches, unavailable states and scoped preservation — required before configured operations or setup.
- [Extension helper](scripts/README.md) — read-only saved-setting validation and limits — required before first local helper use.
