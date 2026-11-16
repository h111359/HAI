# Validate workflow

## Description

Check selected workflow structure and process meaning without changing or executing the definitions.

## Inputs

| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
| [input:request] | Requested operation, scope and authority | Mandatory | Caller or authorized conversation | Retrieve known context; return unresolved necessary decisions. |
| [input:target] | Definition path, bounded collection or new process objective | Mandatory | Caller or inspected workspace | Resolve from authorized context; do not guess another target. |
| [input:activity] | Valid current Activity and evidence destination | Mandatory | Core runtime discovery | Establish continuity before substantive writes; diagnose independently where permitted. |
| [input:context] | Applicable instructions and inspected source evidence | Optional | Caller and authorized workspace | Load relevant contracts; keep unavailable facts explicit. |

## Prerequisites

An explicit requested operation, readable fixed instructions and compatible current
Activity context for substantive work. Authoring additionally needs meaningful
process requirements and authority for the selected definition.

## Rules

None.

## Steps

1. Establish the exact read-only [input:target] and review boundaries from [input:request]. Enumerate a collection only when the requested scope calls for it; partial discovery does not prove absence.

2. Run core workflow validate for each selected definition and retain its actual syntax/reference/graph/file-contract diagnostics. Invalid files remain unchanged.

3. Assess whether the instructions match participant responsibilities, whether each result condition is understandable, and whether every next step receives sufficient actual content, including clarification/rework baselines.

4. Assess coverage and ambiguity of business conditions, finite loop usefulness, author-defined format checks and product/working-artifact ownership. Cite the authored expectation or actual requirement behind each finding.

5. Report participant availability/settings/tool evidence only when checked; do not label an unverified dependency as ready or a structural pass as semantic approval.

6. Return [output:result] with findings, location, significance, check limits and proposed repairs. Leave any repair to separately authorized authoring work and leave all workflow execution to the host.

## Outputs

| Output | Meaning | Completion criteria |
| --- | --- | --- |
| [output:result] | Actual definition work or scoped findings and dependencies | Paths, changes, evidence and limits reflect performed work; no implied execution or approval. |

## References

- [Role rules](../SKILL.md) ? common authority and preservation ? required.
- [Workflow convention](../../../../.hai/conventions/workflow_conv.md) ? format and data contracts ? required.
- [Workflow tools](../../../../.hai/tools/workflows/README.md) ? parser/validator and limits ? required before checks.
- [Runtime commands](../../../../.hai/tools/runtime/README.md) ? managed validation and existing Activity operations ? required before use.
- [Artifact placement](../../../../.hai/conventions/artifact-placement_conv.md) ? predecessor/evidence destinations ? required before writes.
