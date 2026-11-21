---
name: solution-design
description: "Assess technical feasibility, resolve attributable technical decisions and prepare a coherent implementation and verification plan."
---

# Solution design

Use this capability directly or under a suitable role. Follow actual task authority, workspace boundaries and applicable host instructions. A skill does not launch an agent, change model policy or grant permissions. In HAI-managed work, retain Activity ownership and report missing prerequisites; direct use does not require adopting the former role.

## Method constraints

- **Readable implementation plans.** The operator MUST follow the [implementation plan format](conventions/implementation-plan_conv.md) when creating or revising an implementation plan.
- **Current evidence.** The operator MUST compare readiness and decisions with the current input revision rather than reuse a stale pass.
- **Relevant context.** The operator MUST use the Business analyst [context registry contract](../requirements-analysis/conventions/context-registry.md) for designated supplemental context, inspect supplied relevant readable materials fully and report unreadable or nontext limits.
- **Required conventions.** The operator MUST load the coding, language, framework, interface and documentation conventions applicable to the actual targets before their dependent edits or checks; missing mandatory conventions block only dependent work.
- **Readiness evidence.** The operator MUST require current passed business-readiness evidence or an evidenced exemption under the Business analyst [readiness contract](../requirements-analysis/conventions/requirements-readiness.md) before dependent technical planning or implementation.
- **Dialogue persistence.** The operator MUST follow the Business analyst [dialogue contract](../requirements-analysis/conventions/clarification-dialogue.md), requiring verified host persistence before displaying new questions or applying answers.
- **Plan coherence.** The operator MUST carry every implementation-relevant assumption, decision, acceptance obligation and documentation change directly into the current plan and preserve predecessor evidence through host runtime revisions.

## Procedures

| Procedure | Trigger | File |
| --- | --- | --- |
| Assess solution | A new or changed technical assignment needs assessment. | [Assess solution](procedures/assess-solution.md) |
| Resolve technical decisions | A consequential unresolved or changed technical decision needs clarification. | [Resolve technical decisions](procedures/resolve-technical-decisions.md) |
| Prepare implementation plan | A normal or explicitly accelerated implementation plan is requested. | [Prepare implementation plan](procedures/prepare-implementation-plan.md) |

## References

- [Role convention](../../.hai/conventions/role_conv.md) — selection, independence and handoff requirements; required for execution.
- [Core Activity convention](../../.hai/conventions/activity_conv.md) — stable context, step evidence and original implementation start; required when interpreting Activity context.
- [Reference notation](../../.hai/conventions/reference-notation_conv.md), [procedure convention](../../.hai/conventions/procedure_conv.md) and [instruction writing](../../.hai/conventions/instruction-writing_conv.md) — required for interpreting instructions.
- Authorized task-relevant domain sources — read only what the assignment requires.
- [Implementation plan format](conventions/implementation-plan_conv.md) — required when creating, revising or reviewing an implementation plan.

- [Technical assessment](conventions/technical-assessment.md) — required for assessment and technical readiness.
- [Plan helper](scripts/README.md) — required before validation; pure structural checks do not prove semantic readiness.
- Business analyst conventions linked in Rules — required for the named operations; absent peers block dependent work only.
