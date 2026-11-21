# Portable skills and HAI roles: investigation and recommendation

Status: recommendation for human review; no change to skills, roles or runtime is approved or implemented by this investigation.

## My opinion

HAI should support skills that work without HAI, and roles should provide their HAI-specific usage context. This would give the role/skill distinction a practical purpose, improve reuse and make external skills easier to adopt. I recommend the direction, with two qualifications:

1. **Independent of HAI does not mean independent of everything.** A skill may legitimately require Git, Python, a service, a particular document format or another explicitly declared resource. Its requirements must be visible.
2. **A role can provide context, but instructions alone cannot replace runtime integration.** Helpers that import HAI code must be separated or refactored. Common Activity and workflow operations should remain framework services rather than be copied into every role.

The earlier extraction established direct use without selecting a role. It did not establish portability into a workspace without HAI. Those are different properties, and the current implementation falls short of the second.

## What I examined

The audit covers every package under `skills/` and `.hai_env/skills/`: 11 source packages and 11 installed packages, representing 12 distinct skills. Ten identities occur in both collections. `crete-design-package` is source-only; `framework-advice` is installed-only.

The static inventory covers 252 non-cache files: 127 source and 125 installed. It hashes every file and scans every Markdown, Python and JSON resource for HAI paths, runtime imports, Activity requirements, settings ownership and HAI formats. I reviewed each skill entry point, relevant procedures/contracts, representative dependent helpers, and the framework's skill parser/resolver. The inventory is [retained as evidence](../evidence/skill-portability-audit.json). A lexical match is a lead, not proof that every operation is unusable independently.

All 124 files in the ten shared packages were compared. Their differences are confined to Markdown link targets. Installed copies therefore retain the same substantive HAI dependencies. This was a static assessment; I did not execute every skill, run its operational procedures, or demonstrate clean-workspace portability. No independent second-agent review was performed.

I used Exa to review five primary documentation sources across three workstreams: the skill standard, skill authoring, and host integration/customization boundaries. Research findings and recommendations are distinguished below.

## Findings for every skill

| Skill | Current situation | Recommended treatment |
| --- | --- | --- |
| `crete-design-package` | No HAI dependency was identified in its three resources. Inputs, reviewer needs and output placement come from the assignment/project. | Preserve as the existing example of the desired approach; verify portability through representative use rather than assume universal compatibility. |
| `quality-verification` | Its procedure requires a validated HAI environment and active Activity, with no substantive standalone bypass. The verification method itself is generic. | Keep acceptance checking, reproducible defects and coverage reporting in the skill. Supply HAI assignment/evidence destinations through the role and host. |
| `requirements-analysis` | Generic clarification and readiness methods are tied to Activity-scoped dialogue, HAI persistence before displaying questions, protected HAI paths and host handoffs. Some helpers are pure functions, so not every component requires runtime imports. | Keep context assessment, useful questions, decision tracking and readiness assessment generic. Let HAI provide ledger persistence, protected paths and downstream gate enforcement. |
| `solution-design` | Requires Activity context, HAI-shaped plan identity and business-readiness evidence from a sibling skill; technical dialogue inherits its persistence contract. | Accept explicit requirements, decisions, constraints and output expectations. Put HAI plan fields, saved dialogue and approval gates in the role/framework integration. Remove hidden dependence on the requirements skill's internal paths. |
| `software-implementation` | Requires Activity identity and original runtime implementation-start evidence. Its execution contract and sibling readiness/context conventions encode HAI coordination. | Keep implementation, developer verification and attributable change evidence generic. Have HAI supply the approved assignment, applicable conventions and required handoff format. |
| `backlog-management` | Declares `hai-settings-owner`, reads the backlog-manager role configuration, and includes Activity handoff/audit rules. Its auditor discovers `.hai/tools` and loads the installed role contract. | Accept an explicit backlog root and documented backlog format. Move saved-setting lookup and Activity handoff to HAI. Separate the auditor's content checks from HAI configuration loading. A portable skill may remain opinionated about its backlog format. |
| `git-operations` | Explicitly requires initialized HAI and enabled role-owned integrations even for Git inspection. Settings validation/migration helpers depend on HAI. Commit procedures include HAI recording policy. | Keep Git/GitHub operations, real authorization checks and preservation of unrelated work in the skill. HAI supplies enabled capabilities, repository settings and recording obligations. Git/authentication remain genuine external prerequisites. |
| `specification-management` | A mixed package: the tree auditor already supports explicit-root standalone work without HAI; settings ownership, configuration helper and HAI procedures remain coupled. Its helper documentation still refers to the former `specification-manager/` package name. | Preserve the independent specification format and auditor. Extract HAI enablement/location setup and Activity context from the generic package; correct stale examples during a future authorized change. Do not rewrite the existing independent core unnecessarily. |
| `release-management` | The release subject is specifically a HAI bundle: core state-format contracts, candidate declarations, migration information and Git-manager routing are mandatory. | Separate generic candidate/package/publication methods from HAI release policy. Simply deleting HAI paths would lose necessary release behavior. |
| `role-authoring` | Creates HAI ROLE.md definitions, owner contracts and model declarations using HAI conventions, catalogue and validators. | Separate reusable role-design/authoring methods from HAI serialization and validation. The role-definition manager must supply the actual HAI contract and invoke its validator. |
| `workflow-authoring` | Creates HAI workflow formats, environment location bindings, result transitions and run contracts using framework validators. | Separate process/workflow design methods from HAI format generation and checks. The workflow-definition manager provides HAI conventions and integration. |
| `framework-advice` | Its subject and mandatory sources are specifically `.hai/`; it requires reading that framework tree and recommending three actions. | Generalize the skill to framework/repository assessment with an explicit subject, coverage and recommendation count. The HAI advisor role supplies `.hai/` as the subject and HAI-specific review expectations. |

Ten of the eleven source packages contain HAI coupling; this does not mean all their code is coupled or that every operation fails outside HAI. Three authoring/advisory skills and HAI release management also have an intentionally HAI-specific subject, which requires a deliberate redesign rather than a mechanical rename.

Concrete examples: `skills/quality-verification/procedures/perform-assigned-work.md` requires Activity context; `skills/backlog-management/scripts/audit_backlog.py` discovers HAI core at import time; `skills/specification-management/scripts/specification_configuration.py` imports HAI configuration/startup helpers. Conversely, `skills/specification-management/scripts/audit_specification.py` and its documented standalone invocation demonstrate that the separation is feasible.

## What best practices support

**The shared format supports portable folders, not unconditional execution.** The Agent Skills specification defines SKILL.md, optional scripts/references/assets, progressive loading and a compatibility field for environmental requirements. Scripts should be self-contained or document their dependencies. It explicitly allows an intended product in compatibility information. Therefore the standard supports HAI-independent skills but does not require every skill to be universally generic. [Agent Skills specification](https://agentskills.io/specification)

**Use small task instructions and parameterize genuine variation.** Anthropic recommends concise skills, progressive disclosure, appropriate degrees of freedom, parameterized scripts where configuration varies, and evaluations based on real tasks before accumulating instructions. This supports moving environment values out of methods while retaining useful domain detail. It does not support abstracting every skill into an elaborate configuration framework. [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

**Distinguish methods, specialist roles, shared instructions and actual tools.** GitHub describes skills as task-specific instructions/resources, custom agents as specialist roles with instructions/toolsets, and custom instructions as persistent project guidance. External access is supplied by tools/MCP. HAI roles are not identical to GitHub custom agents, but this separation supports the proposed responsibility boundary. [GitHub customization comparison](https://docs.github.com/en/copilot/concepts/customizations/comparing-customizations)

**Discovery and execution belong to the host.** GitHub documents particular discovery directories; an arbitrary root `skills/` directory is not its documented project discovery path. Microsoft exposes configurable skill sources and explicitly requires a script runner for file-backed script execution. Copying a skill is therefore separate from making a host discover it and satisfying its execution requirements. [GitHub skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills), [Microsoft Agent Framework skills](https://learn.microsoft.com/en-us/agent-framework/agents/skills)

## What should live where

| Component | Responsibility | Example |
| --- | --- | --- |
| Skill | Reusable method, intrinsic prerequisites, input/output expectations, necessary templates, scripts and reference material. | Explain how to clarify requirements and produce a decision record from supplied information. |
| Role | Job responsibility, authority limits, skill choice and HAI-specific usage instructions: relevant conventions, configured inputs, output destinations and required handoff. | Business analyst uses requirements analysis, supplies current request/context and returns the required assessment to the Activity owner. |
| Workflow | Ordered assignments, responsible roles, required artifacts, output names/locations, result choices, transitions, loops and human decision points. | Request clarification precedes design; an approved design permits implementation; QA can return work for correction. |
| HAI core/host integration | Activity lifecycle, recording, persistence, shared policy enforcement, configuration validation, tool access and workflow run state. | Save a returned clarification record using the Activity API and make its verified location available to the next step. |

A role should describe its use of a skill and provide the HAI bindings; it should not copy or rewrite the skill's method. A small HAI integration helper can live with the relevant owner where appropriate; common helpers belong to the framework. A role document cannot make a script's missing imports disappear.

For example, a generic requirements skill receives a request, supporting sources, existing decisions and an output location. It produces clarified requirements, unresolved questions and a readiness assessment. The Business analyst role supplies HAI-specific conventions and the assignment context. The host saves records through HAI APIs. The workflow decides whether the result advances to design or returns for clarification. Outside HAI, the same skill can receive those inputs from a person or another system without Activity UUIDs or HAI recording APIs.

Direct skill use must remain possible. A person can supply the needed context without adopting a role. In an HAI workspace, shared workspace rules still apply, and optional HAI integration can be supplied by the host. We should not secretly select a role merely to make a generic skill run.

## External skills: the honest compatibility promise

I recommend: **HAI accepts standards-compatible skill packages without requiring HAI metadata or editing their contents, and roles provide environment-specific usage context.** This is stronger and more useful than claiming that every external folder will work unchanged in every host.

Current barriers extend beyond the authored text:

- `.hai/tools/skills/skill_tools.py` reuses HAI's restricted YAML reader and role-name regex. The regex requires an initial letter; the skill standard permits names beginning with a digit. Some valid YAML constructs are explicitly unsupported. These are interoperability limitations even after removing HAI prose from packages.
- The resolver requires a ready HAI environment and installed `.hai_env/skills/` snapshots. That is a HAI integration requirement, not a requirement a generic skill should impose when used elsewhere.
- `metadata.hai-settings-owner` causes lookup of an installed role contract and saved configuration. That binding belongs outside a generic skill.
- Installation currently rebases cross-package/framework Markdown links. For externally maintained skills, prefer preserving package bytes and keeping HAI bindings separately, making upstream updates predictable.
- Host discovery, tool identifiers, Python/system packages, operating-system assumptions and service access can still differ. Roles can supply supported parameters and tools; they cannot manufacture unavailable capabilities. External packages may also contain project-specific policies that need an explicit compatibility assessment.

Microsoft's implementation ignores unknown top-level fields for forward compatibility, whereas HAI currently rejects them. This is a useful interoperability comparison, not proof that every vendor extension must be accepted or treated as executable authority. HAI should distinguish format validity, host-supported features and unmet dependencies. [Microsoft skill loading](https://learn.microsoft.com/en-us/agent-framework/agents/skills)

## Benefits, costs and integrity

| Perspective | Benefit | Cost or risk to manage |
| --- | --- | --- |
| User | Reuse skills inside/outside HAI and adopt external packages with less editing. | Copying alone cannot guarantee host discovery or prerequisites. Missing inputs should be explained plainly. |
| HAI integrity | Roles become the explicit link between a method and HAI responsibilities; core remains the owner of operational state. | Removing skill prerequisites without replacing their HAI enforcement would weaken readiness, recording and workflow guarantees. |
| Scalability | Several roles/environments can share one method; third-party updates need fewer local patches. | Every imported skill can have a different input vocabulary. Start with explicit role instructions; add structured bindings only where repeated use demonstrates a need. |
| Maintainability | Fewer duplicated policies and fewer skill dependencies on HAI directory layout. | Separating methods, HAI-specific output contracts and helpers is real work. Avoid both repeated HAI boilerplate in roles and overly generic skills that provide little expertise. |

The principal risk is moving coupling rather than removing it: a skill that accepts one opaque mandatory ?HAI context? parameter is still coupled. The opposite risk is stripping detailed methods until the skill says little more than ?do a good job.? Preserve expertise and required domain formats; extract environment ownership and policy.

## Recommended next step, before broad implementation

Agree this boundary, then prepare a bounded design and demonstrate three representative cases: a simple method such as quality verification, a helper-bearing skill such as backlog management, and one externally sourced standard skill. Do not start by changing all packages simultaneously.

The demonstration should show that an exported skill performs a representative task in a workspace without `.hai/` or `.hai_env/`; an external skill can be adopted without changes to its package; two roles can supply different destinations/conventions to one skill; missing prerequisites produce accurate limitations; and HAI still records work and enforces its existing gates. HAI role/workflow authoring and release management then require their own domain-specific extraction decisions.

This report recommends the direction. It does not approve a new architecture, migrate installed packages, change configuration or authorize implementation.
