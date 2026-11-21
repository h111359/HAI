---
workflow_format: 4
name: workflow
revision: 1
entry: assess
max_step_attempts: 2
max_run_attempts: 2
---
# Assess a request

## Purpose

Produce a bounded assessment before implementation. Copy this template to a
named workflow and replace its file contracts and instructions with the actual
task requirements.

## Inputs

| Name | Required | Mode | Location | Format | Expectation |
| --- | --- | --- | --- | --- | --- |
| request | yes | ask | - | markdown | Requested change, affected area and known constraints. |

## Intermediate Files

| Name | Mode | Location | Format | Expectation |
| --- | --- | --- | --- | --- |

## Final Files

| Name | Action | Mode | Location | Format | Expectation |
| --- | --- | --- | --- | --- | --- |
| assessment | create | default | run:files/assessment.md | markdown | Findings, supporting evidence and remaining decisions. |

## Outcomes

| Name | Meaning | Files |
| --- | --- | --- |
| assessed | Assessment and remaining decisions are available. | assessment |

## Steps

### assess

#### Role

business-analyst

#### Instruction

Read the supplied request and confirm its scope against authorized Activity
context. Assess intent, requirements and open decisions. Write the assessment
to its assigned staging path and include evidence and uncertainty.

#### Inputs

| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| request | workflow:request | yes | markdown | Requested change and constraints. |

#### Outputs

| Name |
| --- |
| assessment |

#### Results

| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| assessed | Assessment covers the authorized scope and identifies remaining decisions. | assessment | end:assessed | none |
