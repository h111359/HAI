---
workflow_format: 1
name: change-assessment
revision: 1
entry: assess
max_step_attempts: 2
max_run_attempts: 2
---
# Change assessment

## Purpose

Assess a proposed change without implementation. Use this process for a bounded architecture assessment. Its three domain-specific
results preserve unknowns and scope limits without starting implementation.

## Inputs

| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| request | activity:input.md | markdown | Proposed change and its actual constraints. |

## Outcomes

| Name | Meaning |
| --- | --- |
| feasible | An evidence-based feasible direction has been identified. |
| discovery-needed | Necessary technical facts remain unknown. |
| outside-scope | The proposal exceeds the authorized assignment. |

## Steps

### assess

#### Agent

solution-architect

#### Instruction

Inspect the proposed change and authorized relevant product material without editing
the product. Separate feasible options, unknown facts and authority limits. Write
the artifact matching the selected result. Do not start implementation, create a
release or infer permission to broaden the assignment.

#### Inputs

| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| request | workflow:request | yes | markdown | Original supplied scope and constraints. |

#### Outputs

| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| assessment | attempt:assessment.md | markdown | Feasible approach, evidence, risks, constraints and recommended next decision. |
| discovery | attempt:discovery-questions.md | markdown | Unknown facts, why each is necessary, bounded ways to establish them and blocked conclusions. |
| boundary | attempt:scope-boundary.md | markdown | Exact scope conflict, evidence and decision needed to proceed. |

#### Results

| Name | When | Outputs | Next |
| --- | --- | --- | --- |
| feasible | Scope is authorized and enough evidence supports a feasible approach. | assessment | end:feasible |
| needs-discovery | Scope is authorized but necessary technical facts are unknown. | discovery | end:discovery-needed |
| outside-scope | The requested assessment itself exceeds the authorized assignment. | boundary | end:outside-scope |
