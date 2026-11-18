---
name: framework-advice
description: "Review HAI framework sources with explicit coverage and return three file-grounded recommendations without modifying the workspace."
---

# Framework advice

Use this capability directly or under a suitable role. Follow actual task authority, workspace boundaries and applicable host instructions. A skill does not launch an agent, change model policy or grant permissions. In HAI-managed work, retain Activity ownership and report missing prerequisites; direct use does not require adopting the former role.

## Method constraints

- **First source:** The operator MUST begin a framework review with `.hai/concepts/hai.md`.
- **Complete coverage:** The operator MUST read every file in `.hai/`, including nested folders, for a complete framework review.

## Procedures

### Review and recommend

Trigger: The human requests repository-specific HAI advice and the top three logical next actions.

#### Description

Review this workspace's HAI framework without modifications and return three evidence-based recommendations for the next logical actions.

#### Inputs

| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
| [input:framework_files] | Readable .hai/concepts/hai.md and every file in .hai/ | Mandatory | Verified workspace .hai/ tree | Retrieve from authorized context; return the specific dependency and pause dependent work. |
| [input:priorities] | Human priorities and constraints | Optional | Caller or authorized context | No additional priorities; rank from framework evidence. |

#### Prerequisites

Readable [input:framework_files], including `.hai/concepts/hai.md` and every file in `.hai/`; supplied [input:priorities] when available.

#### Rules

None.

#### Steps

1. Read `.hai/concepts/hai.md` first, then inventory [input:framework_files] recursively.
2. Read every inventoried file and track coverage. If any required file is unreadable, report its access/coverage limit and pause dependent complete-review recommendations.
3. Identify logical next repository actions from reviewed evidence and supplied [input:priorities].
4. Rank the top three, explaining briefly why each comes next and linking relevant reviewed files where helpful.
5. Return [output:recommendations] in chat with actual coverage/uncertainty under the inherited read-only/independence rules.

#### Outputs

| Output | Meaning | Completion criteria |
| --- | --- | --- |
| [output:recommendations] | Ranked top three logical next actions in chat with concise file-grounded reasons | Complete .hai/ coverage established; missing inputs and review limitations reported; no files changed. |

#### References

- [HAI concept](../../../.hai/concepts/hai.md) — framework overview — required;
  read first when starting the framework review.
- `.hai/`, relative to the workspace root — source material for repository
  recommendations — required; read every file recursively after the HAI concept.
- [Role convention](../../../.hai/conventions/role_conv.md) — shared role
  identity, format, and independence — required when loading this role.

## References


- [HAI concept](../../../.hai/concepts/hai.md) — framework overview — required;
  read first when starting the framework review.
- `.hai/`, relative to the workspace root — source material for repository
  recommendations — required; read every file recursively after the HAI concept.
- [Role convention](../../../.hai/conventions/role_conv.md) — shared role
  identity, format, and independence — required when loading this role.
