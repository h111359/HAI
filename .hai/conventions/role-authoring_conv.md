# HAI role authoring

The host follows this core method directly. Apply actual task authority, workspace boundaries, Activity ownership and host execution policy. No authoring package or specialist model profile is required. Report missing prerequisites without claiming success.

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
| Establish scope and inspect | Before creating, updating, validating, auditing, a definition. | [Establish scope and inspect](../procedures/author-role-establish-scope-and-inspect.md) |
| Create a definition | A new definition is explicitly requested. | [Create a definition](../procedures/author-role-create-definition.md) |
| Update a definition | An identified existing definition or authorized migration requires changes. | [Update a definition](../procedures/author-role-update-definition.md) |
| Validate or audit | A definition, registered collection, or changed definition needs read-only verification. | [Validate or audit](../procedures/author-role-validate-or-audit.md) |

## References


- [Role convention](role_conv.md) — definition format, identity,
  selection, and ownership — required for all operations.
- [Role concept](../concepts/role.md) — role boundaries — required when creating
  or changing responsibilities.
- [State convention](state_conv.md) — catalogue encoding and workspace
  prerequisites — required for interpreting catalogue identity and HAI context; independent format
  checks and prerequisite diagnosis remain available without initialized state.
- [Workspace catalogue](../../.hai_env/roles/catalogue.md) when present —
  registration and identity checks — required before mutations; conditional on audit scope.
- [Model profiles](model-profiles_conv.md) — model metadata and
  runtime evidence boundaries — conditional when choosing execution declarations.
- [Framework layout](framework-layout_conv.md) — canonical resource
  placement — required for creation or explicitly authorized relocation.
- [Role tools](../tools/roles/README.md) — validation commands and limits —
  required before first helper use.
- [Tooling convention](tooling_conv.md) — implementation and testing —
  conditional when creating, changing, or executing supporting helpers.
- Caller-supplied sources — target-role knowledge and authority — read only what
  the selected operation needs.
- [Reference notation](reference-notation_conv.md) and [procedure convention](procedure_conv.md) — namespaced references and current procedure/definition format — required for authoring and verification.
- [term:Caller] → [Definition management](../concepts/definition-management.md) — required when interpreting local caller.
- [term:Target] → [Definition management](../concepts/definition-management.md) — required when interpreting local target.
- [term:Origin] → [Definition management](../concepts/definition-management.md) — required when interpreting local origin.
- [term:Registration] → [Definition management](../concepts/definition-management.md) — required when interpreting local registration.
- [Instruction writing](instruction-writing_conv.md) — plain rule wording and the three modal meanings — required when authoring or reviewing instructions.

## Role and skill authoring split

Keep the role a job description: responsibilities, scope, quality, decisions, authority limits and handoffs. Reference reusable methods with quoted metadata `hai-skills: "capability-one, capability-two"` and matching Skills links. Several roles may select the same capability. A role may own job-specific conventions, procedures, scripts and templates even when it uses no skills; no empty procedure tree or artificial skill dependency is required. Preserve hai-model-class and hai-reasoning-effort as host execution declarations; skills cannot override them.

Author reusable capabilities under root `skills/<name>/SKILL.md` with native name/description frontmatter and free-form task instructions plus only necessary resources. No ROLE headings, empty configuration contract or model metadata is imposed on a skill. Native optional license, compatibility, metadata and allowed-tools remain descriptive under actual host authority. Source roles live directly in `roles/<name>/ROLE.md`; installed counterparts live in `.hai_env/roles/`. Recompute relative paths from actual package depth.

For existing integration packages pending separately authorized refactoring, a skill may declare `metadata.hai-settings-owner` and use `skills resolve` to validate that one owner contract and read existing saved settings. This does not adopt the role. Never duplicate saved settings in a skill package. Installed skill lookup must not fall back to root sources.

Apply the authoring scope and boundaries in [definition management](../procedures/manage-role-definitions.md).

## Ownership and extraction checks

- **Complete role.** The author MUST retain job-specific operating knowledge with the role when independent skill packaging adds no useful capability. A role MAY use no skills.
- **Independent capability.** Before extracting a skill, the author MUST identify a useful direct invocation, sufficient explicit inputs, clear outputs and its independent maintenance purpose. The author MUST NOT extract solely because a resource is a convention, procedure, script or template.
- **Single owner.** The author MUST keep related invariants under one owner and MUST NOT duplicate implementations between role and skill. A method reused across deployments of one role MAY remain in that role package.
- **Shared policy.** The author MUST reference shared core/project policies from their owner. Cross-role sequencing belongs in workflows; HAI lifecycle and recording remain core responsibilities.
- **Portable skill.** The author MUST keep newly authored or refactored skills usable without HAI or a selected role. Domain specialization MAY remain where it provides useful expertise.
- **Explicit refactoring.** The author MUST preserve current capabilities and configuration during any approved transfer and verify all resources before retirement. New principles alone do not migrate or remove existing source/installed packages.
