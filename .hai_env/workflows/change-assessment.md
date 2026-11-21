---
workflow_format: 4
name: change-assessment
revision: 4
entry: assess
max_step_attempts: 2
max_run_attempts: 2
---
# Change assessment

## Purpose

Assess a proposed change without implementation. Use this process for a bounded architecture assessment. Its three domain-specific
results preserve unknowns and scope limits without starting implementation.

## Inputs

| Name | Required | Mode | Location | Format | Expectation |
| --- | --- | --- | --- | --- | --- |
| request | yes | ask | - | markdown | Requested change, affected area, known constraints and the decision the assessment should inform. |

## Intermediate Files

| Name | Mode | Location | Format | Expectation |
| --- | --- | --- | --- | --- |

## Final Files

| Name | Action | Mode | Location | Format | Expectation |
| --- | --- | --- | --- | --- | --- |
| assessment | create | default | run:files/assessment.md | markdown | Feasible approach, evidence, risks, constraints and recommended next decision. |
| discovery | create | default | run:files/discovery-questions.md | markdown | Unknown facts, why each matters, bounded checks and blocked conclusions. |
| boundary | create | default | run:files/scope-boundary.md | markdown | Exact scope conflict, evidence and decision needed to proceed. |

## Outcomes

| Name | Meaning | Files |
| --- | --- | --- |
| feasible | An evidence-based feasible direction has been identified. | assessment |
| discovery-needed | Necessary technical facts remain unknown. | discovery |
| outside-scope | The proposal exceeds the authorized assignment. | boundary |

## Steps

### assess

#### Role

solution-architect

#### Instruction

Read the supplied proposal file. Confirm the requested change, affected area,
constraints and decision against authorized Activity context. Ask for missing scope
where necessary. The supplied file does not itself authorize implementation.

Inspect the proposed change and authorized relevant product material without editing
the product. Separate feasible options, unknown facts and authority limits. Write
the artifact matching the selected result. Do not start implementation, create a
release or infer permission to broaden the assignment.

#### Inputs

| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| request | workflow:request | yes | markdown | Original supplied scope and constraints. |

#### Outputs

| Name |
| --- |
| assessment |
| discovery |
| boundary |

#### Results

| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| feasible | Scope is authorized and enough evidence supports a feasible approach. | assessment | end:feasible | none |
| needs-discovery | Scope is authorized but necessary technical facts are unknown. | discovery | end:discovery-needed | none |
| outside-scope | The requested assessment itself exceeds the authorized assignment. | boundary | end:outside-scope | none |
