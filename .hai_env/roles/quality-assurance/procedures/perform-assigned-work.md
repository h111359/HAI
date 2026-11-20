# Perform assigned work

## Description

Perform the assigned quality assurance work and return attributable results, evidence and unresolved dependencies within the authorized scope.

## Inputs

| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
| [input:workspace_root] | Explicit canonical workspace root. | Mandatory | host coordinator or authorized caller | Retrieve authorized context; return unresolved root before dependent work. |
| [input:instructions] | Applicable fixed mandatory and workspace/session instructions. | Mandatory | Caller and safe readable fixed instructions | An empty readable file is valid; missing/unreadable instructions block dependent work. |
| [input:authority] | Requested work, scope, constraints and existing permissions. | Mandatory | Human request relayed by host coordinator | Retrieve existing authority; do not invent approval. |
| [input:activity_context] | Validated environment plus stable active Activity ID/path and relevant record context. | Mandatory | host coordinator and runtime evidence | Retrieve context or return the dependency; no substantive standalone bypass. |
| [input:work_context] | Intent, domain sources, available acceptance criteria, settled decisions, selected steps and relevant prior results. | Mandatory | host coordinator and authorized task sources | Retrieve available context; pause dependent work and continue independent diagnosis. |

## Prerequisites

Compatible environment, safe mandatory instructions, active stable Activity and a meaningful scoped assignment. Required task decisions and operation-specific permission are available before dependent work.

## Rules

None.

## Steps

1. Establish [input:workspace_root], load [input:instructions], compare
   [input:authority], [input:activity_context] and [input:work_context] with the
   procedure requirements, and retrieve missing authorized context before affected work.

2. Identify the product/version, current acceptance criteria, scope, relevant
   implementation evidence and actual reviewer independence. Return missing or
   contradictory criteria and unavailable independence through host coordinator;
   do not invent expected behavior or claim independent assessment without evidence.

3. Select meaningful checks by failure impact, changed areas and uncertainty.
   Include relevant boundary, negative and regression cases. Confirm tools,
   test-side effects and assigned artifact destinations before execution. Report
   missing prerequisites and continue independent permitted checks where useful.
   Do not make product repairs under verification authority; route defects to the
   responsible owner through host coordinator.

4. Perform authorized checks against the identified product/version. Record the
   environment, test inputs, expected result and actual observation. Preserve
   failures and partial results; identify any changed input that invalidates an
   earlier conclusion rather than silently reusing stale evidence.

5. Report each defect with its affected version, reproduction steps, expected and
   actual behavior, evidence, impact and uncertainty. Distinguish an observed
   defect from a suspected cause or environment issue. For authorized follow-up,
   retain earlier findings and identify the version checked again.

6. Map relevant criteria to actual pass, fail, blocked, skipped or unrun results.
   Report regressions, untested areas, coverage limits and unresolved decisions.
   Verification does not establish transcript coverage or authorize Activity closure.

7. Return [output:work_result] with performed work, attributable decisions, exact
   artifact paths or prepared record content and actual verification evidence.
   Keep external work pending until host coordinator returns its owner's evidence;
   do not mark Activity steps or close records yourself.

## Outputs

| Output | Meaning | Completion criteria |
| --- | --- | --- |
| [output:work_result] | Performed assigned work, decisions, artifacts, verification evidence, provenance and unresolved dependencies. | Results match the authorized scope; performed and unperformed work remain distinct; record changes are returned to host coordinator for runtime. |

## References

- [Role instructions](../ROLE.md) — inherited scope, safeguards and required references.
