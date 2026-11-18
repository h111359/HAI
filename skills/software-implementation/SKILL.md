---
name: software-implementation
description: "Validate execution inputs, implement an authorized design or direct directive, perform developer checks and return attributable execution evidence."
---

# Software implementation

Use this capability directly or under a suitable role. Follow actual task authority, workspace boundaries and applicable host instructions. A skill does not launch an agent, change model policy or grant permissions. In HAI-managed work, retain Activity ownership and report missing prerequisites; direct use does not require adopting the former role.

## Method constraints

- **Current evidence.** The operator MUST compare readiness and decisions with the current input revision rather than reuse a stale pass.
- **Relevant context.** The operator MUST use the Business analyst [context registry contract](../requirements-analysis/conventions/context-registry.md) for designated supplemental context, inspect supplied relevant readable materials fully and report unreadable or nontext limits.
- **Required conventions.** The operator MUST load the coding, language, framework, interface and documentation conventions applicable to the actual targets before their dependent edits or checks; missing mandatory conventions block only dependent work.
- **Readiness evidence.** The operator MUST require current passed business-readiness evidence or an evidenced exemption under the Business analyst [readiness contract](../requirements-analysis/conventions/requirements-readiness.md) before dependent technical planning or implementation.
- **Delivery evidence.** The operator MUST follow the [execution evidence contract](conventions/execution-evidence.md), trace its own direct/indirect changes against the baseline and withhold verified success while mandatory checks or owner work remain unresolved.

## Procedures

| Procedure | Trigger | File |
| --- | --- | --- |
| Validate execution input | A new directive or changed current execution context is supplied. | [Validate execution input](procedures/validate-execution-input.md) |
| Implement assigned work | Current validated directive and runtime implementation-start evidence are available. | [Implement assigned work](procedures/implement-assigned-work.md) |
| Verify and hand off | Implementation results need acceptance checks or a delivery report. | [Verify and hand off](procedures/verify-and-handoff.md) |

## References

- [Role convention](../../.hai/conventions/role_conv.md) — selection, independence and handoff requirements; required for execution.
- [Core Activity convention](../../.hai/conventions/activity_conv.md) — stable context, step evidence and original implementation start; required when interpreting Activity context.
- [Reference notation](../../.hai/conventions/reference-notation_conv.md), [procedure convention](../../.hai/conventions/procedure_conv.md) and [instruction writing](../../.hai/conventions/instruction-writing_conv.md) — required for interpreting instructions.
- Authorized task-relevant domain sources — read only what the assignment requires.

- [Execution evidence](conventions/execution-evidence.md) — required for preflight and delivery.
- [Execution helper](scripts/README.md) — required before helper use and interpreting its limits.
- [Architect plan contract](../solution-design/conventions/implementation-plan_conv.md) — required in plan mode; missing peer does not block independent direct-mode diagnosis.
- Business analyst conventions linked in Rules — required for the named operations; absent peers block dependent work only.
