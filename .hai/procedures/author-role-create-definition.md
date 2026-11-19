# Create a definition

## Description

Create and verify a scoped role definition and necessary resources, keeping creation separate from registration and reporting the actual resulting status.

## Inputs

| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
| [input:inspection] | Verified scope, identity and prerequisite findings | Mandatory | Result of Establish scope and inspect | Retrieve from authorized context; return the specific dependency and pause dependent work. |
| [input:role_requirements] | Meaningful purpose, boundaries, knowledge, inputs, defaults, failures and outcomes | Mandatory | Caller or authorized context | Retrieve from authorized context; return the specific dependency and pause dependent work. |
| [input:origin] | Runtime origin for a new installed definition | Optional | Caller or authorized context | Default installed definitions to workspace origin; an explicitly requested source-package kind comes from inspection and is not a runtime origin. |
| [input:name] | Proposed descriptive name | Optional | Caller or authorized context | Resolve a descriptive name with the caller before creating a definition. |
| [input:execution_metadata] | Proposed specialist class and effort | Optional | Caller or authorized context | Choose justified specialist class/effort and explain; preserve host coordinator exceptions. |

## Prerequisites

Verified `inspection` output from [Establish scope and inspect](author-role-establish-scope-and-inspect.md), supplied as [input:inspection]. Meaningful role requirements and settled ownership before creation.

## Rules

- **Workspace default:** The operator MUST use workspace origin for a new role unless golden source-package creation is explicitly requested.
- **Missing name:** The operator MUST resolve an absent descriptive name with the caller before creation.
- **Unspecified execution settings:** The operator MUST choose and explain justified specialist class and effort values when none are supplied.
- **Model mapping boundary:** The operator MUST NOT put concrete model mappings in the new definition.
- **Exclusive creation:** The operator MUST create new definition files and directories exclusively without replacing existing parents or targets.

## Steps

1. Resolve purpose, trigger, boundaries, knowledge, inputs/defaults, failure behavior, procedures and observable outcomes from [input:role_requirements] and [input:inspection]. Resolve conflicting ownership and a missing [input:name]; establish [input:origin] for an installed target or the source-package kind from inspection, and [input:execution_metadata] under the creation defaults.
2. Define the role-owned settings, types, defaults, missing/error behavior and ownership boundaries; when no settings are owned, omit the contract and its metadata. Prepare `configuration/contract.json` and quoted `hai-configuration-contract` metadata only for actual settings ownership under the shared configuration convention, without creating workspace overrides or enabling capabilities. Author the canonical description first. Prepare unchanged-format YAML identity/optional fields and the ordered Purpose, Scope, Out of Scope, Rules and References headings; add Skills for explicit capability references and Procedures only for genuinely role-local methods; set folder/name agreement and quoted string specialist metadata, without declaring a built-in coordinator role.
3. Classify each proposed statement by meaning and scope. Put reusable method constraints in SKILL.md; responsibility, authority and handoff conduct stays in ROLE Rules, unique operation-specific constraints in local Rules, actions/decisions in Steps, required starting conditions in Prerequisites and short purpose/result prose in Description. Keep concepts explanatory and conventions about representation/contracts.
4. Write each genuine rule with an explicit actor, action, object and applicable condition. Use uppercase `MUST` for an obligation, `MUST NOT` for a prohibition and `MAY` for a choice within existing permission. Split independent requirements into separate short bold titles without IDs; use exactly `None.` for no local rules. Reference inherited rules rather than repeat or override them.
5. Compare the drafted wording with [input:role_requirements] and settled decisions. Check that defaults, preferences, permitted alternatives, obligations, prohibitions and exceptions retain their meaning; a modal word alone proves neither clarity nor correct placement.
6. Extract reusable methods to a coherent skill and declare quoted comma-separated `metadata.hai-skills` plus Skills links in the role. For any genuinely role-local procedure needed across its skills, prepare its Description, Inputs, Prerequisites, Rules, Steps, Outputs and References, including local namespaced tables and absence behavior. Use canonical index triggers and local file links, or the permitted single inline form. Map domain terms to purposeful concept Markdown; place schemas/contracts in conventions and actual execution behavior in the owning procedure. Add conditional references and only demonstrated supporting resources.
7. Recheck authority, collision facts, context, target absence and containment, then create the prepared resources exclusively. If inputs changed or creation partially fails, return actual partial results under the inherited failure rule.
8. Run [Validate or audit](author-role-validate-or-audit.md), passing the selected target as `target`, [input:inspection] as `inspection` and requested scope as `audit_scope` where relevant. If validation fails, return actual partial results and findings without registration.
9. Return any combined installation/registration request through host coordinator to runtime, with the validated source or installed canonical target, exact decoded description, definition/contract evidence and the user's covering scope. Never copy an installation, mutate a catalogue or invoke another role. A source-only target remains uninstalled; an authored runtime definition remains unregistered unless runtime separately completes explicit registration.
10. Return [output:definition] with verified authoring results, actual registration observation and required installer/catalogue handoffs. Creation alone does not install a package, add membership or activate capabilities; do not claim a pending runtime step completed.

## Outputs

| Output | Meaning | Completion criteria |
| --- | --- | --- |
| [output:definition] | Verified authored definition/source package and installer/catalogue handoff evidence | Structural/semantic evidence and exact metadata reported; source remains non-executable/unregistered and pending installation/registration is identified without catalogue writes. |

## References

- [Capability instructions](../conventions/role-authoring_conv.md) — shared core authoring method and boundaries.
- [Role convention](../conventions/role_conv.md) — definition format, identity,
  selection, and ownership — required for all operations.
- [Role concept](../concepts/role.md) — role boundaries — required when creating
  or changing responsibilities.
- [State convention](../conventions/state_conv.md) — catalogue encoding and workspace
  prerequisites — required for interpreting catalogue identity and HAI context; independent format
  checks and prerequisite diagnosis remain available without initialized state.
- [Workspace catalogue](../../.hai_env/roles/catalogue.md) when present —
  registration and identity checks — required before mutations; conditional on audit scope.
- [Model profiles](../conventions/model-profiles_conv.md) — model metadata and
  runtime evidence boundaries — conditional when choosing execution declarations.
- [Framework layout](../conventions/framework-layout_conv.md) — canonical resource
  placement — required for creation or explicitly authorized relocation.
- [Role tools](../tools/roles/README.md) — validation commands and limits —
  required before first helper use.
- [Tooling convention](../conventions/tooling_conv.md) — implementation and testing —
  conditional when creating, changing, or executing supporting helpers.
- Caller-supplied sources — target-role knowledge and authority — read only what
  the selected operation needs.
