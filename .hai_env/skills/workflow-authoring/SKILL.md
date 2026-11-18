---
name: workflow-authoring
description: "Create, update and inspect reusable HAI workflows with responsible roles, accepted input contracts, authored results and bounded transitions; do not execute the workflow."
---

# Workflow authoring

Use this capability directly or under a suitable role. Follow actual task authority, workspace boundaries and applicable host instructions. A skill does not launch an agent, change model policy or grant permissions. In HAI-managed work, retain Activity ownership and report missing prerequisites; direct use does not require adopting the former role.

## Method constraints

- **Format authority:** The operator MUST follow the shared workflow
  convention rather than maintain a second incompatible interpretation.
- **Explicit contracts:** The operator MUST specify each step's role,
  instruction, required inputs, output locations, authored expectations and result paths.

## Procedures

| Procedure | Trigger | File |
| --- | --- | --- |
| Establish scope | Before authoring, updating or checking workflow definitions. | [Establish scope](procedures/establish-scope.md) |
| Create workflow | A new workflow definition is requested. | [Create workflow](procedures/create-workflow.md) |
| Update workflow | Changes to an identified workflow definition are requested. | [Update workflow](procedures/update-workflow.md) |
| Validate workflow | A selected definition or bounded collection needs validation or audit. | [Validate workflow](procedures/validate-workflow.md) |

## References

- [Workflow convention](../../../.hai/conventions/workflow_conv.md) — canonical file format — required.
- [Workflow concept](../../../.hai/concepts/workflow.md) — roles, steps and runs — required.
- [Workflow tools](../../../.hai/tools/workflows/README.md) and [runtime](../../../.hai/tools/runtime/README.md) — actual validation operations — required before tool use.
- [Role convention](../../../.hai/conventions/role_conv.md) and [procedure convention](../../../.hai/conventions/procedure_conv.md) — role boundaries and file conventions — required.
- [Artifact placement](../../../.hai/conventions/artifact-placement_conv.md) and [workspace boundary](../../../.hai/conventions/workspace-boundary_conv.md) — destinations and authority — required before writes.
- [Instruction writing](../../../.hai/conventions/instruction-writing_conv.md) — explicit readable rules — required when authoring.

- [Configurable workflow authoring](conventions/authoring-format3.md) - required for format-3 location declarations, per-step execution names, human gates and accepted or historical feedback input bindings. Source definitions live in root `workflows/`; installation creates the distinct `.hai_env/workflows/` snapshot and saves chosen environment locations. Workflows assign roles and results; roles select available skills.
