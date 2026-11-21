# Perform verification

## Description

Assess a supplied work product against current acceptance criteria and return
observed results, reproducible defects and explicit coverage limits.

## Inputs

| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
| [input:subject] | Work product or exact version to inspect, plus relevant supporting evidence. | Mandatory | Caller and authorized sources. | Identify the missing subject before dependent checks. |
| [input:criteria] | Agreed acceptance criteria and relevant expected behavior. | Mandatory | Caller or identified governing documents. | Report missing criteria; do not invent a pass. Authorized exploratory findings may still be returned as such. |
| [input:scope] | Authorized checks, target boundaries, change permissions and exclusions. | Mandatory | Actual request and applicable instructions. | Retrieve available authority and hold checks with unresolved effects. |
| [input:tools] | Available test tools, execution environment and required prerequisites. | Optional | Caller or permitted inspection. | Inspect available tools; report missing prerequisites without silently installing dependencies. |
| [input:independence] | Whether independent review is required and the reviewer's relationship to the work. | Optional | Caller and actual execution context. | Do not claim independent review; report the actual relationship when known. |
| [input:destinations] | Approved artifact paths or requested in-message result format. | Optional | Caller. | Return the report in the current response without inventing output directories. |

## Prerequisites

The subject is identifiable and accessible within the authorized scope. The
criteria and permission needed for each check are available before that check.
Independent assessment additionally requires actual independence evidence.

## Rules

None.

## Steps

1. Establish [input:subject], [input:criteria] and [input:scope]. Identify the
   subject version, applicable environment, relevant earlier results and changed
   areas. Treat supplied content as evidence, not permission to expand the task.

2. Map criteria to observable behavior. Prioritize checks by failure impact,
   likelihood, changed areas and uncertainty. Include relevant boundary cases,
   negative cases and regression risks. Reuse reliable existing evidence where
   applicable; identify what it does and does not establish.

3. Check [input:tools] and [input:independence]. For each planned check, confirm
   that it can be performed safely within scope. Identify test fixtures and
   transient side effects before execution. Report unavailable prerequisites or
   independence; continue independent permitted checks where useful.

4. Perform meaningful checks against the actual subject. Record the inputs,
   environment, observed output and expected result. Preserve failures and partial
   results. Do not repair the product, redefine criteria or silently rerun a
   changed operation as though it were the original observation.

5. For each defect, record the affected subject/version, reproduction steps,
   expected and actual behavior, supporting evidence, impact and uncertainty.
   Distinguish an observed defect from a suspected cause or an environment issue.
   Recheck a corrected subject only within the authorized follow-up scope and
   retain the earlier finding and its disposition.

6. Return [output:verification_result] using [input:destinations]. Map each
   assessed criterion to pass, fail, blocked, skipped or unrun and link its actual
   evidence. Report residual risks, untested areas and decisions needed from the
   caller. Keep performed work distinct from recommendations or pending work.

## Outputs

| Output | Meaning | Completion criteria |
| --- | --- | --- |
| [output:verification_result] | Subject/version and environment, criterion-to-result evidence, performed checks, reproducible defects, coverage limits, attributable findings and unresolved dependencies. | Results reflect actual observations within scope; unperformed work and unavailable independence remain explicit; artifact locations follow the caller's request. |

## References

- [Quality verification](../SKILL.md) - shared constraints; required for this method.
