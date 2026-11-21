# Workflow

## Definition

A workflow is a reusable single-file process that assigns steps to HAI roles,
declares input/output artifacts and follows explicit result-dependent transitions.
One execution is a run; one performance of a step is an attempt. Each run belongs
to exactly one Activity. A workflow cannot transition to another Activity.

## Purpose

Let users select an organizational process without reconstructing every role
handoff. Workflows remain optional; ordinary tasks and role procedures still work.

## Explanation

An explicitly supplied reusable source definition can be installed into
`.hai_env/workflows/<name>.md`. An installed definition is discoverable by its presence;
there is no separate workflow catalogue. Discovery is not execution authority.
The host checks the definition and current prerequisites, then coordinates actual
work. Core tools persist assignments and accept supported result evidence; they
do not invoke models or independently assess business quality.

A step names a role and its expected result. The assigned role chooses suitable
available skills; no workflow skill binding prescribes that choice. Missing suitable
skills block the affected assignment. A step contains its process assignment. The selected role's procedures,
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

Workflow format 3 separates authored filename patterns from human-chosen
workspace-relative destination bases in `.hai_env/config/workflows/<name>.json`.
Installation explains each location and waits for actual choices; missing/unsafe
configuration blocks that workflow without blocking core startup. Each run uses a
UUID subfolder below its configured bases. Every intermediate name contains the
step and runtime-assigned per-step execution number. Accepted copies, immutable
initial snapshots and input lineage remain authoritative inside the Activity.
Canonical product files keep their existing ownership and publication authority.

Format 4 declares input, intermediate and final files in three tables. A run
resolves fixed, default or caller-supplied paths and pins the bindings. A bare
path is workspace-relative. An `activity:` path follows the run's owning
Activity into its archive. Steps stage files, and accepted results determine
which intermediate files become available and which final files are delivered.
Activity status and startup show unfinished runs and known pending actions.

An authored `accepted:step/result/output` source binds a named accepted result,
including earlier approved requirements/design on a partial QA return. Superseded
required ancestors and changed/missing handoff files block acceptance. A human
checkpoint references an actual received typed human instruction and checkpoint-bound
host semantic attestation. Runtime validates recorded attribution and identities;
it does not independently authenticate the human. QA pass and human acceptance
remain distinct.

The host authors and reviews processes through [built-in workflow authoring](../procedures/manage-workflow-definitions.md), without an installed authoring role or skill. The shared workflow convention
is the format authority, core tools check structure, and the host assesses actual
output meaning and current execution readiness. A valid file alone proves neither
participant availability nor successful product changes.

## References

- [Workflow convention](../conventions/workflow_conv.md) — definition and file contracts.
- [Run convention](../conventions/workflow-run_conv.md) — ownership, states and recovery.
- [Execute workflow](../procedures/execute-workflow.md) — host coordination.
- [Activity](activity.md) and [Procedure](procedure.md) — existing lifecycle and role-local work.
