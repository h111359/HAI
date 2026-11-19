# Update workflow

## Description

Revise an identified definition while preserving predecessor evidence and existing executions.

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

1. Read the selected definition and requested change from [input:target] and [input:request]. Retain exact bytes/hash/revision and scoped known run references; do not inspect unrelated run content.

2. Preserve the predecessor at an unused path in [input:activity] history/ before a material edit. Record actual source, reason and affected contracts. Increase the definition revision for material changes.

3. Prepare scoped edits and compare original versus revised meaning, including optional inputs, result conditions, failure paths, limits and handoff completeness. Do not infer approval of newly introduced restrictions.

4. Recheck inspected target identity/hash and permission before writing. Stop dependent edits on input changes or partial failure and retain actual results without automatic cleanup/retry.

5. Run core structural validation and semantic review of affected paths, refreshing dependent examples and actual check evidence within scope. Existing run definition snapshots remain unchanged.

6. Return [output:result] with changed paths, preserved predecessor, revision and actual validation/semantic results. Return any desired run migration to the host as a separate decision; never alter run state yourself.

## Outputs

| Output | Meaning | Completion criteria |
| --- | --- | --- |
| [output:result] | Actual definition work or scoped findings and dependencies | Paths, changes, evidence and limits reflect performed work; no implied execution or approval. |

## References

- [Role rules](../conventions/workflow-authoring_conv.md) ? common authority and preservation ? required.
- [Workflow convention](../conventions/workflow_conv.md) ? format and data contracts ? required.
- [Workflow tools](../tools/workflows/README.md) ? parser/validator and limits ? required before checks.
- [Runtime commands](../tools/runtime/README.md) ? managed validation and existing Activity operations ? required before use.
- [Artifact placement](../conventions/artifact-placement_conv.md) ? predecessor/evidence destinations ? required before writes.

- [Configurable workflow authoring](../conventions/workflow-authoring-format3_conv.md) - required for format-3 definitions, configuration, gates and live or feedback lineage; retain format-2 maintenance compatibility.
