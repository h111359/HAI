# Establish scope

## Description

Establish the target, authority, ownership, relevant role contracts and prerequisites for workflow definition work.

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

1. Resolve [input:request] and [input:target] as creation, update or read-only validation/audit. Keep explicit process decisions separate from proposals.

2. Check fixed instructions, the installed manager contract and effective settings. Verify [input:activity] through core discovery; do not create another Activity while compatible work is current.

3. Resolve the exact .hai_env/workflows/<name>.md destination and existing ancestor containment. Check case-insensitive names, regular file types and unrelated definitions without scanning their content unnecessarily.

4. Read the selected existing definition and relevant registered participant guides/procedures only to establish actual responsibilities and handoff requirements. An unavailable participant is a readiness issue, not permission to install it.

5. Return inspected source hashes/revisions, canonical target or absence, authority and missing decisions as [output:result]. Do not modify files during inspection.

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
