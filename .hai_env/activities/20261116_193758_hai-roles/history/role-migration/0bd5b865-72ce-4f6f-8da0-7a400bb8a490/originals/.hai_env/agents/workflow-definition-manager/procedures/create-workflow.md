# Create workflow

## Description

Author and check one self-contained process with explicit role assignments, artifact contracts and result-dependent transitions.

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

1. Use [input:request], [input:target] and [input:context] to establish the process purpose, one entry, intended participants and terminal outcomes. Retrieve known facts before asking for missing necessary choices.

2. Prepare all step instructions, initial inputs, output paths/formats/expectations and named results. Each result needs evidence and one next action. Define positive per-step and total-run limits; do not assume success/failure are the only results.

3. Walk each transition, including returns and failure paths. Every required incoming artifact must be supplied by every predecessor result that reaches the consumer. Preserve necessary earlier decisions in the actual handoff, not just references the next step cannot read.

4. Check scope, actor responsibility, mutually understandable result conditions, evidence sufficiency and explicit tool/format checks. Respect unrestricted formats and existing product destinations; do not force product artifacts into a run copy.

5. Recheck target absence and authority, create the single file exclusively, and run core workflow validate. Perform semantic review separately. An invalid result is retained and reported; validation does not execute the target.

6. Return [output:result] with exact authored path, revision, format evidence, semantic findings and execution-readiness limits. Do not register an agent or launch a run.

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
