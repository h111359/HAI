# Workflow design package — review draft 0.1

Date: 2026-11-14. Activity: `1b440d51-819b-4299-862b-0182f0f4fca5`.
Status: **proposed, not approved for implementation**.

This package describes the entire proposed first version. Runtime commands,
directories and manager capabilities below are proposals, not installed features.
All examples and traces are illustrative, not evidence of executed workflows.

## Read in this order

1. [Requirements and acceptance](01-requirements.md): your requirements and proposed scope boundaries.
2. [Solution specification](02-solution-specification.md): exact format, file references, state, transitions, recovery and interfaces.
3. [Worked examples](03-worked-examples.md): full definitions, concrete paths, artifact samples and traces.
4. [Manager design](04-manager-design.md): responsibilities, procedures and validation ownership.
5. [Implementation plan](05-implementation-plan.md): affected resources, verification and staged delivery.

## Proposed solution at a glance

An optional named process lives in `.hai_env/workflows/<name>.md`. A host starts
an execution inside the sole current Activity, snapshots that definition and its
initial inputs, and follows one control path at a time. Each step is an instruction
to a registered agent. Accepted named results choose the next step or a declared
terminal outcome. Results always have file evidence; unknown or invalid results
cannot advance the process. The definition manager owns authoring and review;
core owns validation/persistence; the host owns actual dispatch and coordination.

```mermaid
flowchart LR
    Request[Customer request] --> Clarify[Business analyst]
    Clarify -->|ready| Design[Solution architect]
    Design -->|needs-clarification| Clarify
    Design -->|designed| Build[Software developer]
    Build -->|implemented| Check[Quality assurance]
    Check -->|accepted| Document[Specification manager]
    Document --> Finish[Workflow completed; Activity stays open]
```

The diagram omits other terminal branches; the complete example defines every
result and its evidence. Rework is bounded and retained, not an implicit restart.

## Decisions requested in review

| Proposal | Recommendation and reason | Alternative and cost |
| --- | --- | --- |
| Machine-readable structure | Restricted scalar frontmatter plus fixed Markdown tables; simple review and no external YAML dependency. | JSON blocks allow richer nesting but make simple definitions harder to read. |
| Run storage | `.hai_env/workflow-runs/<activity-id>/<run-id>/` is NOT recommended; place records at `<configured Activity>/files/workflow-runs/<run-id>/` instead. This is under `.hai_env/` by default and archives with the Activity. | A fixed `.hai_env/` run root would satisfy that location literally even with a custom Activity store, but require a second archival/ownership mechanism. |
| Shared registration | Definition filename is its identity; validation precedes selection, with no separate workflow catalogue initially. | An explicit catalogue adds a separate registration step and consistency burden. |
| Artifact contracts | Run evidence files are fixed per attempt; actual product changes are listed in evidence manifests and retain existing owners. | Direct arbitrary product-output paths in the workflow add overwrite and retry semantics. |
| Coordination | Several runs per Activity, but only one executing run at a time; other runs can be paused. | Concurrent runs require enforceable resource ownership and conflict handling. |
| Result logic | Unlimited named results with explicit human-readable selection criteria; the host accepts exactly one. | A Boolean expression language adds another interpreter and security surface. |
| Loops | Explicit back-edges, with per-step and total attempt limits. | Acyclic-only definitions exclude ordinary clarification/rework processes. |
| Agent manager placement | Workspace-authored manager, separately registered through runtime if implementation is approved. | A golden library package is an additional deliverable, not assumed. |

These are recommendations for approval, not additional user requirements. In
particular the single-file location, one entry, unrestricted result names and
single-Activity execution are already your requirements and are preserved.

## Approval boundary

Review the whole package or comment on individual decisions. An approval must
identify this version and any exceptions. The implementation plan does not grant
permission to implement, register a manager, change runtime behavior, run an example,
enable specification management or publish anything. Later material revisions keep
their predecessor and change notes rather than silently changing an approved design.
