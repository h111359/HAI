# Execute workflow

## Description

Coordinate a registered workflow within its owning Activity and retain attributable
assignments, artifact evidence, accepted results and unresolved dependencies.

## Inputs

| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
| [input:request] | Actual requested process, scope and authority | Mandatory | Human or authorized context | Retrieve known context, then ask only for necessary missing decisions. |
| [input:definition] | Named workflow file or existing run | Mandatory | Selection, workflow list or show result | List available definitions or runs; do not guess an ambiguous selection. |
| [input:activity] | Sole current active Activity | Mandatory | Validated runtime discovery | Establish continuity through existing Activity operations before starting work. |
| [input:runtime] | Actual host model/effort support evidence | Mandatory | Available host capabilities | Report unavailable execution combinations; do not fabricate support. |

## Prerequisites

Readable fixed instructions, valid core context, authorized meaningful assignment
and compatible Activity continuity. Definition validation and current readiness are
separate; optional missing dependencies block only affected execution.

## Rules

- **Assignment authority.** The coordinator MUST keep workflow effects within
  [input:request] and existing permissions; file presence is not execution authority.
- **Host execution.** The coordinator MUST perform actual execution through available
  host tools; Python run operations do not launch agents or prove writer termination.
- **Evidence.** The coordinator MUST substantiate the selected result's authored
  condition and output expectations with actual artifacts and check evidence.
- **Input lineage.** The coordinator MUST use resolved inputs from the frozen
  assignment and MUST NOT substitute a similarly named artifact from another attempt.
- **Safe continuation.** The coordinator MUST resolve unknown writers and partial
  product effects before retrying and MUST NOT infer rollback from cancellation.
- **Independent checks.** The coordinator MUST preserve the shared policy for
  independent verification instead of treating a role label as proof of independence.

## Steps

1. Resolve [input:request], [input:definition] and [input:activity]. Use `workflow list`
   for explicit discovery and `workflow validate` for structural evidence; ask the
   definition manager for scoped semantic review when needed. Do not change workflow
   files merely to display a menu. A malformed file is not absence of the whole feature.
2. Preview `workflow start` with the Activity ID and selected definition. Inspect
   initial files, task authority and missing prerequisites. Applying start pins the
   definition and initial artifact bytes, not permission for all possible effects.
3. Preview/prepare the next step using the current run revision, actual [input:runtime]
   capability evidence, authority reference and prerequisite assessment. Read the
   selected installed role's instructions/configuration; check required tools and
   operation-specific conditions. Missing configuration never becomes permission to
   enable an integration. Specification updates need the owner's enabled setting.
4. For direct role work, retain the actual executor identity. For a separate spawn,
   obtain an applied Activity invocation allocation, supply its manifest/folder plus
   Activity/run/step/attempt IDs, instruction, exact input paths and output destinations,
   and record the returned host handle. Supply Activity chat operations and boundary
   authority. Record running only after launch is observed; failed launches remain
   attempts. Never describe a direct role switch as a separate agent invocation.
5. Obtain the agent's one proposed result. Inspect its required files/directories,
   unchanged inputs, current product checks and authored result/format expectations.
   Resolve conflicting criteria rather than choosing the first matching row. Submit
   complete-step with actual host assessment; rejection does not dispatch the next
   step. A crash without required failure evidence remains an interruption.
6. After acceptance, show the selected next action and refresh its prerequisites
   before dispatch. An explicit return creates a new attempt. Reaching a limit
   blocks rather than silently extending it. Finishing records the declared outcome
   and does not close the Activity or publish anything.
7. For waits, record actual questions/answers. For pause/cancel, stop scheduling and
   verify the assigned writers ended before releasing ownership. Resume/retry checks
   input/role/config changes and actual earlier effects. Identical accepted completion
   replay returns the saved acceptance; conflicting replay is not another success.
8. Maintain recording/usage through their existing source-backed contracts. Report
   completed, failed, blocked and unrun work accurately as [output:result]. Before
   requested Activity closure resolve unfinished runs and relevant writers; include
   the Activity-local run folders in any requested export or retention review.
   Resolve paths by stable Activity/run IDs after archival; runs move with the owner.

## Outputs

| Output | Meaning | Completion criteria |
| --- | --- | --- |
| [output:result] | Run identity, accepted outcomes, actual artifacts and unresolved work | State agrees with actual host evidence; no invented launch, result, approval, recording coverage or external effect. |

## References

- [Workflow convention](../conventions/workflow_conv.md) — definition and file contracts — required.
- [Run convention](../conventions/workflow-run_conv.md) — ownership, state and recovery — required.
- [Runtime commands](../tools/runtime/README.md) — actual request shapes — required before operations.
- [Role convention](../conventions/role_conv.md) and [invocation convention](../conventions/agent-invocation_conv.md) — execution mode and handoff — required before role work.
- [Artifact placement](../conventions/artifact-placement_conv.md) and [workspace boundary](../conventions/workspace-boundary_conv.md) — ownership/permission — required.
