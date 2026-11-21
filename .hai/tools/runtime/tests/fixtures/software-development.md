---
workflow_format: 3
name: software-development
revision: 1
entry: prepare
max_step_attempts: 5
max_run_attempts: 32
---
# Software development

## Purpose
Carry authorized backlog work through clarified requirements, solution design,
human approval, implementation, independent QA, human acceptance and a final
Backlog-manager completion handoff. Roles select suitable installed skills.
Selection grants no permission and starts no agent. All outputs are retained run
evidence; product changes and backlog updates keep their canonical owners. Stable
product names are declared in implementation/completion reports and require the
owner's actual authority; this process never automatically publishes or closes an Activity.

## Locations
| Name | Purpose | Contents |
| --- | --- | --- |
| handoffs | Retain reviewable step evidence and exact downstream handoffs. | Per-run folders containing every step execution report, requirements, design, approval, QA and defects. |
| completion | Retain the final completion receipt for review. | Per-run completion evidence referencing canonical backlog/product changes and actual human acceptance. |

## Inputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| activity-context | activity:README.md | markdown | Activity summary; host supplies actual human request and selected backlog item under current authority. |

## Outcomes
| Name | Meaning |
| --- | --- |
| delivered | QA passed, human accepted and authorized Backlog-manager completion was recorded; Activity remains open. |
| blocked | Required decision, capability or evidence is unavailable; preserve effects and obtain a new authorized continuation. |
| declined | Human declined the proposed implementation or completed result. |

## Steps
### prepare

#### Role
backlog-manager

#### Instruction
Identify the selected backlog item, actual request, constraints, current owner authority and completion evidence needed. Do not invent scope or mark completion. Report unavailable dependencies.

#### Inputs
| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| context | workflow:activity-context | yes | markdown | Exact applicable accepted evidence. |

#### Outputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| work-item | configured:handoffs/prepare-{execution}-work-item.md | markdown | Selected canonical backlog path, scope, constraints and authority references. |

#### Results
| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| prepared | Selected work and constraints are established. | work-item | step:clarify | none |
| blocked | Selected item or authority is unavailable. | work-item | end:blocked | none |


### clarify

#### Role
business-analyst

#### Instruction
Clarify actual authorized scope and acceptance criteria; preserve human decisions and record material changes. Evaluate readiness before design. Use returned questions where present.

#### Inputs
| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| work-item | accepted:prepare/prepared/work-item | yes | markdown | Exact applicable accepted evidence. |
| questions | feedback:questions | no | markdown | Exact applicable accepted evidence. |

#### Outputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| requirements | configured:handoffs/clarify-{execution}-requirements.md | markdown | Current requirements, acceptance criteria, actual decisions and readiness evidence. |

#### Results
| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| refined | Requirements are ready for design. | requirements | step:design | none |
| blocked | Human input or readiness is unresolved. | requirements | end:blocked | none |


### design

#### Role
solution-architect

#### Instruction
Design the approved scope with implementation and verification guidance. Identify material changes requiring fresh clarification/approval. Return explicit questions rather than invent decisions.

#### Inputs
| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| work-item | accepted:prepare/prepared/work-item | yes | markdown | Exact applicable accepted evidence. |
| requirements | accepted:clarify/refined/requirements | yes | markdown | Exact applicable accepted evidence. |

#### Outputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| design | configured:handoffs/design-{execution}-solution-design.md | markdown | Solution, changed paths, tradeoffs, test guidance and scope/requirements identities. |
| questions | configured:handoffs/design-{execution}-questions.md | markdown | Specific unresolved scope or design questions. |

#### Results
| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| designed | Design is complete and traceable to requirements. | design | step:approve-design | none |
| questions | Requirements need clarification. | questions | step:clarify | none |
| blocked | Safe design cannot proceed. | questions | end:blocked | none |


### approve-design

#### Role
solution-architect

#### Instruction
Present the current requirements and design to the human. Wait for actual approval before implementation. Record the actual received instruction and host semantic attestation bound to this checkpoint; agent assertions are insufficient. Material changes return for clarification and fresh approval.

#### Inputs
| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| requirements | accepted:clarify/refined/requirements | yes | markdown | Exact applicable accepted evidence. |
| design | accepted:design/designed/design | yes | markdown | Exact applicable accepted evidence. |

#### Outputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| approval | configured:handoffs/approve-design-{execution}-design-approval.md | markdown | Current requirement/design identities, actual human message reference and approval or requested changes. |
| questions | configured:handoffs/approve-design-{execution}-questions.md | markdown | Actual requested scope/design changes. |

#### Results
| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| approved | Human explicitly approved current requirements/design and host verified the recorded instruction. | approval | step:implement | human |
| changes | Human requested material changes. | questions | step:clarify | none |
| declined | Human declined implementation. | approval | end:declined | none |
| blocked | Human instruction or necessary evidence is absent. | approval | end:blocked | none |


### implement

#### Role
software-developer

#### Instruction
Implement the current approved design within actual authority; select suitable skills and perform developer checks. On QA return consume the exact new defects plus still-applicable earlier requirements, design and approval. Report canonical product outputs/changes and stable final names with owner authorization; do not publish automatically.

#### Inputs
| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| work-item | accepted:prepare/prepared/work-item | yes | markdown | Exact applicable accepted evidence. |
| requirements | accepted:clarify/refined/requirements | yes | markdown | Exact applicable accepted evidence. |
| design | accepted:design/designed/design | yes | markdown | Exact applicable accepted evidence. |
| design-approval | accepted:approve-design/approved/approval | yes | markdown | Exact applicable accepted evidence. |
| defects | feedback:defects | no | markdown | Current QA defects on a partial return; absent on the first implementation. |

#### Outputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| implementation | configured:handoffs/implement-{execution}-implementation-report.md | markdown | Canonical changes, checks, result/limitations, approved input identities and addressed defects. |
| questions | configured:handoffs/implement-{execution}-questions.md | markdown | Material scope/design issues requiring renewed clarification and approval. |

#### Results
| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| implemented | Approved changes and developer checks are complete. | implementation | step:verify | none |
| scope-change | Material scope or design change is required. | questions | step:clarify | none |
| blocked | Implementation dependency or checks prevent completion. | implementation | end:blocked | none |


### verify

#### Role
quality-assurance

#### Instruction
Independently verify the implementation against current requirements and approved design. Record actual checks and meaningful defects. Failed QA never becomes a passing result or human acceptance. Preserve partial-return defect lineage; material scope changes require renewed clarification and approval.

#### Inputs
| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| requirements | accepted:clarify/refined/requirements | yes | markdown | Exact applicable accepted evidence. |
| design | accepted:design/designed/design | yes | markdown | Exact applicable accepted evidence. |
| design-approval | accepted:approve-design/approved/approval | yes | markdown | Exact applicable accepted evidence. |
| implementation | accepted:implement/implemented/implementation | yes | markdown | Exact applicable accepted evidence. |

#### Outputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| verification | configured:handoffs/verify-{execution}-verification-report.md | markdown | Actual acceptance checks, outcomes and limitations tied to current implementation. |
| defects | configured:handoffs/verify-{execution}-defects.md | markdown | Reproducible defects against the exact implementation; input identities retained. |
| questions | configured:handoffs/verify-{execution}-questions.md | markdown | Material requirement or design changes identified by QA. |

#### Results
| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| passed | All required acceptance checks pass with evidence. | verification | step:accept-result | none |
| defects | Implementation defects require bounded rework. | verification, defects | step:implement | none |
| scope-change | QA identifies a material scope/design issue. | questions | step:clarify | none |
| blocked | Required verification is unavailable or inconclusive. | verification | end:blocked | none |


### accept-result

#### Role
quality-assurance

#### Instruction
Present the current passing QA result and implementation to the human. Wait for actual acceptance; QA success alone is insufficient. Bind the recorded received human instruction and host semantic attestation to this checkpoint. Changes requiring scope/design revision return to clarification.

#### Inputs
| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| requirements | accepted:clarify/refined/requirements | yes | markdown | Exact applicable accepted evidence. |
| design | accepted:design/designed/design | yes | markdown | Exact applicable accepted evidence. |
| design-approval | accepted:approve-design/approved/approval | yes | markdown | Exact applicable accepted evidence. |
| implementation | accepted:implement/implemented/implementation | yes | markdown | Exact applicable accepted evidence. |
| qa-pass | accepted:verify/passed/verification | yes | markdown | Exact applicable accepted evidence. |

#### Outputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| acceptance | configured:handoffs/accept-result-{execution}-human-acceptance.md | markdown | Current QA/implementation identities and actual human acceptance/decline reference. |
| questions | configured:handoffs/accept-result-{execution}-questions.md | markdown | Actual requested material changes. |

#### Results
| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| accepted | Human accepted the current verified result. | acceptance | step:complete | human |
| changes | Human requests changed scope/design. | questions | step:clarify | none |
| declined | Human declined the result. | acceptance | end:declined | none |
| blocked | Human acceptance is missing or ambiguous. | acceptance | end:blocked | none |


### complete

#### Role
backlog-manager

#### Instruction
After QA pass and actual human acceptance, verify the canonical backlog owner authorization before updating its completion status. Record supporting QA, accepted product changes and human acceptance. If update authority is missing report blocked; workflow selection alone grants none. Never close the Activity automatically.

#### Inputs
| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| work-item | accepted:prepare/prepared/work-item | yes | markdown | Exact applicable accepted evidence. |
| requirements | accepted:clarify/refined/requirements | yes | markdown | Exact applicable accepted evidence. |
| design | accepted:design/designed/design | yes | markdown | Exact applicable accepted evidence. |
| design-approval | accepted:approve-design/approved/approval | yes | markdown | Exact applicable accepted evidence. |
| implementation | accepted:implement/implemented/implementation | yes | markdown | Exact applicable accepted evidence. |
| qa-pass | accepted:verify/passed/verification | yes | markdown | Exact applicable accepted evidence. |
| human-acceptance | accepted:accept-result/accepted/acceptance | yes | markdown | Exact applicable accepted evidence. |

#### Outputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| completion | configured:completion/complete-{execution}-completion-record.md | markdown | Final per-run receipt: canonical backlog update, product outputs, QA and actual human acceptance; Activity stays open. |

#### Results
| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| completed | Authorized backlog completion and supporting evidence are recorded. | completion | end:delivered | none |
| blocked | Owner authority or completion evidence is unavailable. | completion | end:blocked | none |
