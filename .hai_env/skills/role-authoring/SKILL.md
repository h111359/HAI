---
name: role-authoring
description: "Create, revise and inspect lightweight HAI role job descriptions and skill references, preserving responsibilities, metadata and installation boundaries."
---

# Role authoring

Use this capability directly or under a suitable role. Follow actual task authority, workspace boundaries and applicable host instructions. A skill does not launch an agent, change model policy or grant permissions. In HAI-managed work, retain Activity ownership and report missing prerequisites; direct use does not require adopting the former role.

## Method constraints

- **Shared format:** The operator MUST follow the shared definition, procedure and reference formats.
- **Purpose wording:** The operator MUST limit each Description to the procedure's purpose and intended result.
- **Prerequisite placement:** The operator MUST place required starting conditions in Prerequisites.
- **Workflow placement:** The operator MUST place ordered actions and explicit decisions in Steps.
- **Concept placement:** The operator MUST use concept files to explain meaning.
- **Contract placement:** The operator MUST use conventions to define data formats and contracts.
- **Rule wording:** The operator MUST write each rule in plain language with an explicit actor, action, object and any applicable condition.
- **Rule strength:** The operator MUST express each rule using uppercase MUST, MUST NOT or MAY with their defined obligation, prohibition or permitted-choice meaning.
- **Single requirement:** The operator MUST give each independent requirement its own short, unique, readable bold title without an ID; The operator MAY keep a related exception or default beside it when separating them would obscure the meaning.
- **Shared constraints:** The operator MUST place constraints used by several procedures in ROLE Rules.
- **Local constraints:** The operator MUST limit local Rules to that procedure's specific constraints.
- **Inherited rules:** The operator MUST NOT repeat or override inherited skill instructions and applicable selected-role conduct in a procedure's Rules.
- **Empty local rules:** The operator MUST write exactly `None.` when a procedure has no local rules.
- **Meaning preservation:** The operator MUST preserve existing obligations, prohibitions, defaults, permitted choices, conditions and exceptions when rewriting rules.
- **Clarity evidence:** The operator MUST NOT treat a modal word, numbering or an imperative label as proof that a rule is clear or belongs in Rules.
- **Optional owner contracts.** The operator MUST declare and validate a configuration contract only when the role owns actual settings, and MUST preserve existing saved settings and their owner.
- **Compatibility review:** The operator MUST assess supported versions, defaults, owner boundaries and existing saved-setting compatibility when changing a configuration contract.
- **Distinct role names:** Before changing definition files, The operator MUST check the workspace catalogue and immediate role-folder collection for another role using the same name, ignoring letter case and including unregistered folders.
- **Limited name checking:** The operator MUST NOT use a name check as permission to load unrelated definitions or overwrite another role.

## Procedures

| Procedure | Trigger | File |
| --- | --- | --- |
| Establish scope and inspect | Before creating, updating, validating, auditing, a definition. | [Establish scope and inspect](procedures/establish-scope-and-inspect.md) |
| Create a definition | A new definition is explicitly requested. | [Create a definition](procedures/create-definition.md) |
| Update a definition | An identified existing definition or authorized migration requires changes. | [Update a definition](procedures/update-definition.md) |
| Validate or audit | A definition, registered collection, or changed definition needs read-only verification. | [Validate or audit](procedures/validate-or-audit.md) |

## References


- [Role convention](../../../.hai/conventions/role_conv.md) — definition format, identity,
  selection, and ownership — required for all operations.
- [Role concept](../../../.hai/concepts/role.md) — role boundaries — required when creating
  or changing responsibilities.
- [State convention](../../../.hai/conventions/state_conv.md) — catalogue encoding and workspace
  prerequisites — required for interpreting catalogue identity and HAI context; independent format
  checks and prerequisite diagnosis remain available without initialized state.
- [Workspace catalogue](../../roles/catalogue.md) when present —
  registration and identity checks — required before mutations; conditional on audit scope.
- [Model profiles](../../../.hai/conventions/model-profiles_conv.md) — model metadata and
  runtime evidence boundaries — conditional when choosing execution declarations.
- [Framework layout](../../../.hai/conventions/framework-layout_conv.md) — canonical resource
  placement — required for creation or explicitly authorized relocation.
- [Role tools](../../../.hai/tools/roles/README.md) — validation commands and limits —
  required before first helper use.
- [Tooling convention](../../../.hai/conventions/tooling_conv.md) — implementation and testing —
  conditional when creating, changing, or executing supporting helpers.
- Caller-supplied sources — target-role knowledge and authority — read only what
  the selected operation needs.
- [Reference notation](../../../.hai/conventions/reference-notation_conv.md) and [procedure convention](../../../.hai/conventions/procedure_conv.md) — namespaced references and current procedure/definition format — required for authoring and verification.
- [term:Caller] → [Definition management](concepts/definition-management.md) — required when interpreting local caller.
- [term:Target] → [Definition management](concepts/definition-management.md) — required when interpreting local target.
- [term:Origin] → [Definition management](concepts/definition-management.md) — required when interpreting local origin.
- [term:Registration] → [Definition management](concepts/definition-management.md) — required when interpreting local registration.
- [Instruction writing](../../../.hai/conventions/instruction-writing_conv.md) — plain rule wording and the three modal meanings — required when authoring or reviewing instructions.

## Role and skill authoring split

Keep the role a job description: responsibilities, scope, quality, decisions, authority limits and handoffs. Reference reusable methods with quoted metadata `hai-skills: "capability-one, capability-two"` and matching Skills links. Several roles may select the same capability. A role may retain genuinely local procedures when needed; no empty procedure tree is required. Preserve hai-model-class and hai-reasoning-effort as host execution declarations; skills cannot override them.

Author reusable capabilities under root `skills/<name>/SKILL.md` with native name/description frontmatter and free-form task instructions plus only necessary resources. No ROLE headings, empty configuration contract or model metadata is imposed on a skill. Native optional license, compatibility, metadata and allowed-tools remain descriptive under actual host authority. Source roles live directly in `roles/<name>/ROLE.md`; installed counterparts live in `.hai_env/roles/`. Recompute relative paths from actual package depth.

For settings owned by an installed service role, a skill may declare `metadata.hai-settings-owner` and use `skills resolve` to validate that one owner contract and read existing saved settings. This does not adopt the role. Never duplicate saved settings in a skill package. Installed skill lookup must not fall back to root sources.
