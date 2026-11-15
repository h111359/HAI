# Workflow

## Definition

A workflow is a reusable single-file process that assigns steps to agent roles,
declares input/output artifacts and follows explicit result-dependent transitions.
One execution is a run; one performance of a step is an attempt. Each run belongs
to exactly one Activity. A workflow cannot transition to another Activity.

## Purpose

Let users select an organizational process without reconstructing every agent
handoff. Workflows remain optional; ordinary tasks and agent procedures still work.

## Explanation

A definition in `.hai_env/workflows/<name>.md` is discoverable by its presence;
there is no separate workflow catalogue. Discovery is not execution authority.
The host checks the definition and current prerequisites, then coordinates actual
work. Core tools persist assignments and accept supported result evidence; they
do not invoke models or independently assess business quality.

A step names a role and contains its assignment. The selected role's procedures,
configuration and authority still apply. The host decides direct execution or
separate invocation under the shared agent policy; a step is not inherently a spawn.

Authors choose result names and conditions. Each completed attempt reports one
result with its required artifacts. Acceptance selects one next step or one ending.
Missing tools, unknown writer status and absent evidence are interruptions, not
fabricated failure results. An explicit return to an earlier step creates another
attempt and retains earlier work. Finite per-step and run limits prevent endless loops.

Multiple runs can belong to one Activity, but only one holds its execution slot.
Dedicated `<activity>/workflow-runs/<run-id>/` directories keep records and
artifacts separate. The containing Activity provides ownership without another
Activity-ID folder. A finished run never automatically closes the Activity.
Runs archive and export with their Activity. Durable references use the stable
Activity and run IDs, resolving the current or archived Activity path.

The definition manager authors and reviews processes. The shared workflow convention
is the format authority, core tools check structure, and the host assesses actual
output meaning and current execution readiness. A valid file alone proves neither
participant availability nor successful product changes.

## References

- [Workflow convention](../conventions/workflow_conv.md) — definition and file contracts.
- [Run convention](../conventions/workflow-run_conv.md) — ownership, states and recovery.
- [Execute workflow](../procedures/execute-workflow.md) — host coordination.
- [Activity](activity.md) and [Procedure](procedure.md) — existing lifecycle and role-local work.
