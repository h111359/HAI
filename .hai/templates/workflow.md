---
workflow_format: 1
name: workflow
revision: 1
entry: assess
max_step_attempts: 2
max_run_attempts: 2
---
# Assess a request

## Purpose

Produce a bounded assessment before implementation. Copy this template to a named
workflow and change its name, instructions and artifact contracts to the actual task.

## Inputs

| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| request | activity:input.md | markdown | Actual supplied request and known constraints. |

## Outcomes

| Name | Meaning |
| --- | --- |
| assessed | Assessment and remaining decisions are available. |

## Steps

### assess

#### Agent

business-analyst

#### Instruction

Assess the request, clarify its intent when possible and document requirements,
unknowns and recommended next decisions. Do not implement or invent approval.

#### Inputs

| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| request | workflow:request | yes | markdown | Original request snapshot. |

#### Outputs

| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| assessment | attempt:assessment.md | markdown | Evidence-based findings, scope and unresolved decisions. |

#### Results

| Name | When | Outputs | Next |
| --- | --- | --- | --- |
| assessed | Assessment covers the requested scope and identifies unresolved decisions without claiming implementation. | assessment | end:assessed |
