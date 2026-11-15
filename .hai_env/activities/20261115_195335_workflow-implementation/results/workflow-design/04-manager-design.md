# Workflow-definition-manager design — draft 0.3

Storage revision: the user now requires runs inside their owning Activity at
`<activity>/workflow-runs/<run-id>/`, without another Activity-ID level. Runs
move with the Activity on archival. Earlier drafts are preserved in the Activity
revision files; this storage decision supersedes their external-root proposal.

## Purpose and ownership

Create, maintain, verify and validate meaningful single-file workflow definitions.
The manager knows the format, reviews the process and diagnoses invalid contracts.
It does not execute the workflow, dispatch agents or maintain run progress.

The shared workflow format belongs in a future `.hai/conventions/workflow_conv.md`;
the manager references that single authority and owns its authoring/review procedures.
Core Python owns deterministic parsing and run-state validation. This avoids a
definition being “valid” to the manager but interpreted differently by the runtime.

## Proposed package

```text
hai_agents_library/agents/workflow-definition-manager/  # Canonical golden source
  SKILL.md
  configuration/contract.json
  procedures/establish-scope.md
  procedures/create-workflow.md
  procedures/update-workflow.md
  procedures/validate-workflow.md
```

These are proposed source resource names, not files created by this design phase.
The user explicitly requested golden-library inclusion. Shared manager behavior is
therefore maintained in `hai_agents_library/agents/workflow-definition-manager/`.
The corresponding installed package is `.hai_env/agents/workflow-definition-manager/`
with the same reviewed resource structure. Source authoring, runtime installation,
registration and execution remain separate operations; a source package is not an
execution origin. When implementation is authorized, validate the golden package,
install the reviewed snapshot through runtime and separately verify its registration.
Later golden-source changes do not silently replace installed copies or settings.

The manager declares an empty settings contract, fixed workflow root and no feature
toggle. A missing workflow folder is valid before authoring; create it only for an
authorized first definition. A configurable root would expand this agreed location
and is not part of version 1. Core workflow reading and run inspection remain usable
without the optional authoring manager, subject to actual runtime support.

## Proposed SKILL entry

This code block is the proposed role entry structure. Indexed procedure names and
contracts below complete its behavior; implementation will materialize them using
HAI's existing definition/procedure conventions and validate the resulting package.

```markdown
---
name: workflow-definition-manager
description: "Call to create, maintain, validate or audit single-file workspace workflows. Returns definition changes, structural and semantic findings, verification evidence and unresolved decisions; does not execute workflows."
metadata:
  hai-configuration-contract: "configuration/contract.json"
  hai-model-class: "standard"
  hai-reasoning-effort: "high"
---

## Purpose
Maintain clear, valid workflows that coordinate registered agent roles.

## Scope
Author and update explicitly requested definitions in .hai_env/workflows/.
Validate structure, file contracts, graph consistency and business meaning.
Audit an explicitly selected collection without implicit repair.

## Out of Scope
Workflow execution, agent invocation, run-state writes, Activity lifecycle,
agent catalogue mutation, product changes and unauthorized migration.

## Rules
- **Format authority:** The manager MUST follow the shared workflow convention.
- **Task scope:** The manager MUST limit changes to the authorized definitions.
- **Read-only checks:** The manager MUST NOT repair files while validating or auditing.
- **No execution:** The manager MUST NOT invoke participants or execute a target workflow.
- **Role boundaries:** The manager MUST preserve the selected agents' responsibilities and prerequisites.
- **Evidence:** The manager MUST separate structural validity, semantic findings and execution readiness.
- **History:** The manager MUST preserve prior definition bytes and explain changes affecting existing runs.
- **Authority:** The manager MUST NOT invent permission, accepted requirements or successful execution evidence.

## Procedures
| Procedure | Trigger | File |
| --- | --- | --- |
| Establish scope | Before authoring, updating or checking definitions. | [Establish scope](procedures/establish-scope.md) |
| Create workflow | A new workflow is requested. | [Create workflow](procedures/create-workflow.md) |
| Update workflow | Changes to an identified definition are requested. | [Update workflow](procedures/update-workflow.md) |
| Validate workflow | A selected definition or bounded collection needs validation/audit. | [Validate workflow](procedures/validate-workflow.md) |

## References
- Shared workflow convention — format and file contracts, required.
- Shared agent/procedure/configuration conventions — package and ownership, required.
- Workflow validator README — commands and limits, required before helper use.
```

The final package must use real relative links in References, not these explanatory
resource labels. Those exact link destinations are listed in the implementation plan.
Model class/effort follows current profiles and host capability checks, not a concrete
provider model hardcoded into the package. Direct execution does not waive prerequisites.

Configuration contract:

```json
{
  "contract_format_version": 1,
  "agent": "workflow-definition-manager",
  "current_config_format_version": 1,
  "supported_config_format_versions": [1],
  "settings": {}
}
```

## Procedure contracts and behavior

All four procedures will use the existing exact Description/Inputs/Prerequisites/
Rules/Steps/Outputs/References structure. Rules shared across operations stay in
SKILL; procedure-specific rules stay local. No new procedure notation or authority
hierarchy is introduced.

| Procedure | Required inputs | Optional inputs | Observable outputs |
| --- | --- | --- | --- |
| Establish scope | Operation, workspace, target definition or new-process objective, authority, Activity context | Existing findings | Verified target/absence/collision facts, applicable contracts, intended operation and blockers. |
| Create workflow | Scope evidence, agreed process requirements and file ownership | Preferred names, supplied example | One authored definition, actual structural check result, semantic assessment and unresolved decisions. |
| Update workflow | Scope evidence, selected existing definition, requested change | Run-reference evidence | Preserved predecessor, revised single file with incremented revision, change impact, check findings. |
| Validate workflow | Scope evidence, selected definition(s) and audit boundaries | Requirements/acceptance evidence | Read-only structured and semantic findings, readiness limits and repair recommendations. |

Missing required inputs are retrieved from authorized context first; unresolved
meaning is returned to the host/user without invented defaults. Optional inputs
may remain absent. Existing role configuration is checked through the shared loader.

Establish scope:

1. Resolve target and operation; verify workspace, current Activity and user authority.
2. Check fixed instructions and manager configuration; identify affected definitions.
3. Check canonical lowercase filename, case-insensitive collisions and safe ancestry.
4. For an existing file, retain hash/revision and inspect only relevant registered
   role guides/procedures needed to assess responsibility or a concrete dependency.
5. Return facts and blockers without modifying the target.

Create:

1. Translate agreed intent into actors, one entry, input/output contracts, result
   criteria, exact edges, terminal outcomes and finite attempt limits.
2. Walk every edge, especially failure and return paths; ensure mandatory incoming
   files are supplied by each result that can reach the consumer.
3. Check role responsibilities, evidence sufficiency, product destinations and
   distinguish business failure from execution interruption.
4. Prepare the complete Markdown file; resolve consequential missing decisions.
5. Recheck target absence and authority; create exclusively, without overwriting.
6. Run core structural validation, then semantic review; report actual findings.
   File creation is not registration, execution, approval or proof of readiness.

Update:

1. Inspect original bytes, hash, revision and requested changes; report active-run
   implications from authorized same-Activity run metadata where available.
2. Preserve predecessor bytes under the current Activity's files/revisions area
   before changing the reusable file. Increment revision for material changes.
3. Prepare scoped changes and compare before/after meaning, including result paths.
4. Recheck unchanged target/authority before write; preserve partial results if
   interrupted; do not auto-retry or clean up another writer's work.
5. Validate and review. Existing runs retain their snapshots; no automatic rebasing,
   run repair, status change or amendment of accepted evidence.

Validate/audit:

1. Parse with core validator and retain diagnostics; do not fix files implicitly.
2. Inspect all reachable paths and the actual role responsibilities.
3. Assess criterion coverage/overlap, loop usefulness, file semantics and owner
   destinations; produce evidence-based findings rather than universal guarantees.
4. Report readiness separately: role registration, capability, tools and settings
   can change after review. Diagnose only requested dependent configuration.
5. Return severity, location, reasoning and recommended action for each finding.

## Validation layers

| Layer | Checks | Cannot prove |
| --- | --- | --- |
| Syntax | Definition encoding, draft YAML fields, section order, table shape, identifiers and proposed positive limits. Artifact formats are author-defined. | Meaningful instructions or artifact format correctness. |
| Graph/contracts | One entry, valid targets, reachability, terminal paths, output references, mandatory incoming data on every edge, path safety/format compatibility. | A business criterion will actually occur. |
| Semantic review | Scope, appropriate roles, sufficient handoff content, result coverage, ambiguity, authority, testable Expectations, purposeful loops. | Product correctness before execution. |
| Execution readiness | Current Activity, participant/model/tool/config availability, actual inputs and permitted destinations. | Future readiness or successful effects. |
| Result acceptance | Actual output bytes, hashes, criterion/evidence assessment and transition. | External exactly-once execution or absence of all defects. |

Structural validation returns precise section/row diagnostics. A manager assessment
records which semantic checks were performed and unresolved findings. A passing
format check must never be presented as full semantic acceptance or readiness.
