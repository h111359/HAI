# HAI workflow authoring

The host follows this core method directly. Apply actual task authority, workspace boundaries, Activity ownership and host execution policy. No authoring package or specialist model profile is required. Report missing prerequisites without claiming success.

## Method constraints

- **Format authority:** The operator MUST follow the shared workflow
  convention rather than maintain a second incompatible interpretation.
- **Explicit contracts:** The operator MUST specify each step's role,
  instruction, required inputs, output locations, authored expectations and result paths.

## Procedures

| Procedure | Trigger | File |
| --- | --- | --- |
| Establish scope | Before authoring, updating or checking workflow definitions. | [Establish scope](../procedures/author-workflow-establish-scope.md) |
| Create workflow | A new workflow definition is requested. | [Create workflow](../procedures/author-workflow-create-workflow.md) |
| Update workflow | Changes to an identified workflow definition are requested. | [Update workflow](../procedures/author-workflow-update-workflow.md) |
| Validate workflow | A selected definition or bounded collection needs validation or audit. | [Validate workflow](../procedures/author-workflow-validate-workflow.md) |

## References

- [Workflow convention](workflow_conv.md) — canonical file format — required.
- [Workflow concept](../concepts/workflow.md) — roles, steps and runs — required.
- [Workflow tools](../tools/workflows/README.md) and [runtime](../tools/runtime/README.md) — actual validation operations — required before tool use.
- [Role convention](role_conv.md) and [procedure convention](procedure_conv.md) — role boundaries and file conventions — required.
- [Artifact placement](artifact-placement_conv.md) and [workspace boundary](workspace-boundary_conv.md) — destinations and authority — required before writes.
- [Instruction writing](instruction-writing_conv.md) — explicit readable rules — required when authoring.

- [Configurable workflow authoring](workflow-authoring-format3_conv.md) - required for format-3 location declarations, per-step execution names, human gates and accepted or historical feedback input bindings. Source definitions are explicit caller-selected files; installation creates the distinct `.hai_env/workflows/` snapshot and saves chosen environment locations. Workflows assign roles and results; roles select available skills.

Apply the authoring scope and boundaries in [definition management](../procedures/manage-workflow-definitions.md).
