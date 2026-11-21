---
workflow_format: 4
name: customer-request
revision: 4
entry: clarify
max_step_attempts: 3
max_run_attempts: 12
---
# Customer request

## Purpose

Clarify a customer request, design and implement the agreed change, verify it,
and update the maintained product specification. File presence makes this process discoverable; execution still requires an
authorized assignment and current participant readiness.

## Inputs

| Name | Required | Mode | Location | Format | Expectation |
| --- | --- | --- | --- | --- | --- |
| request | yes | ask | - | markdown | Requested change, affected product or users, desired behavior or problem, plus known constraints and open decisions. |

## Intermediate Files

| Name | Mode | Location | Format | Expectation |
| --- | --- | --- | --- | --- |
| requirements | default | run:files/requirements.md | markdown | Attributable scope, exclusions, requirements, acceptance criteria and resolved questions. |
| questions | default | run:files/clarification-questions.md | markdown | Complete prior requirements and answers verbatim, producer reference/hash, new questions and affected decisions. |
| design | default | run:files/solution-design.md | markdown | Agreed scope, justified design, affected resources, implementation plan and verification approach. |
| implementation | default | run:files/implementation-evidence.md | markdown | Actual behavior, exact created or modified paths, agreed design and criteria, source references, checks, partial effects and limits. |
| checks | default | run:files/developer-checks.json | json | Nonempty object listing actual checks, pass/fail/unrun status and supporting evidence. |
| verification | default | run:files/verified-handoff.md | markdown | Independently verified scope and behavior, exact paths/hashes, test evidence and limits. |

## Final Files

| Name | Action | Mode | Location | Format | Expectation |
| --- | --- | --- | --- | --- | --- |
| missing-decisions | create | default | run:files/questions.md | markdown | Exact unresolved decisions, why each is necessary and the work blocked. |
| rejection | create | default | run:files/design-rejection.md | markdown | Reason design cannot proceed within scope, evidence and alternatives. |
| implementation-failure | create | default | run:files/implementation-failure.md | markdown | Actual failure, completed changes, unresolved effects and safe continuation requirements. |
| findings | create | default | run:files/verification-findings.md | markdown | Defects, failed criteria, affected paths, evidence and required corrections. |
| documentation | create | default | run:files/documentation-receipt.md | markdown | Configured specification root, exact modified files/hashes, verification mapping and limits. |
| documentation-failure | create | default | run:files/documentation-failure.md | markdown | Actual update failure, retained partial edits and next necessary action. |

## Outcomes

| Name | Meaning | Files |
| --- | --- | --- |
| delivered | Implementation independently verified and specification reconciled. | documentation |
| needs-input | Necessary customer decisions remain unresolved; no delivery claimed. | missing-decisions |
| declined | Request is outside the agreed assignment or cannot be responsibly designed. | rejection |
| implementation-failed | Attempted implementation failed with retained evidence and known partial effects. | implementation-failure |
| documentation-failed | Attempted specification update failed with retained evidence and known partial effects. | documentation-failure |
| changes-requested | Verification found defects; findings available for a separately authorized continuation. | findings |

## Steps

### clarify

#### Role

business-analyst

#### Instruction

Read request and, when supplied, architect-questions. Check scope against
authorized Activity context and record attributable decisions in typed Activity
chat. Produce scope, exclusions, requirements
and acceptance criteria without inventing agreement. The initial request snapshot
stays unchanged. On a return from design, address the exact questions and issue a
new complete requirements artifact for this attempt. Do not implement the product.
The architect-questions handoff includes the full previously clarified requirements
and attributable answers. Preserve those settled decisions while addressing the new
questions; do not reconstruct them from the initial request or conversation memory.

#### Inputs

| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| request | workflow:request | yes | markdown | Original request snapshot. |
| architect-questions | feedback:questions | no | markdown | Full previous clarified requirements and attributable answers, source hash, and new necessary design questions. |

#### Outputs

| Name |
| --- |
| requirements |
| missing-decisions |

#### Results

| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| ready | Scope and acceptance criteria are sufficient for design; required decisions are resolved. | requirements | step:design | none |
| insufficient-input | Necessary decisions remain unresolved and the user cannot yet supply them. | missing-decisions | end:needs-input | none |

### design

#### Role

solution-architect

#### Instruction

Design against supplied requirements. Assess alternatives and define components,
constraints, risks, implementation plan and verification approach. Include the
agreed scope and acceptance criteria in the design handoff with their source hash,
so the developer can understand the work without looking up arbitrary older files.
Return precise clarification questions when design depends on unresolved meaning.
Do not substitute design assumptions for customer decisions.
The questions handoff must embed the complete supplied requirements and recorded
answers verbatim, identifying their accepted producer and hash, before adding the
new questions. A reference/hash alone cannot supply the next analyst's baseline.

#### Inputs

| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| requirements | incoming:requirements | yes | markdown | Accepted complete requirements from the preceding analyst attempt. |

#### Outputs

| Name |
| --- |
| design |
| questions |
| rejection |

#### Results

| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| designed | A feasible design covers the agreed requirements without necessary unresolved decisions. | design | step:implement | none |
| needs-clarification | Necessary meaning or acceptance criteria are unresolved. | questions | step:clarify | none |
| declined | The request cannot be responsibly designed within the agreed scope for reasons other than missing clarification. | rejection | end:declined | none |

### implement

#### Role

software-developer

#### Instruction

Implement the supplied design within the authorized product locations and run
appropriate developer checks. Record exact changed files and known partial effects.
The implementation handoff includes the agreed scope, design decisions and criteria
with source references and hashes. Never treat the workflow as publication authority.
If execution fails and evidence can be written, describe the actual failure and
checks rather than fabricating implementation success.

#### Inputs

| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| design | incoming:design | yes | markdown | Accepted design and agreed acceptance criteria. |

#### Outputs

| Name |
| --- |
| implementation |
| checks |
| implementation-failure |

#### Results

| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| implemented | The scoped change is implemented and all required developer checks pass. | implementation, checks | step:verify | none |
| failed | Attempted implementation or required developer checks failed and the failure is documented. | implementation-failure | end:implementation-failed | none |

### verify

#### Role

quality-assurance

#### Instruction

Independently assess behavior against the agreed acceptance criteria and inspect
the actual changed product and developer check evidence. Follow existing executor
independence requirements. A verified handoff must summarize accepted scope, actual
behavior, design deviations, exact changed paths and current hashes so the
specification manager can reconcile documentation. Do not accept an author's
completion claim as verification. If the environment cannot support required
verification, block the attempt instead of fabricating a product defect result.

#### Inputs

| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| implementation | incoming:implementation | yes | markdown | Actual changes and agreed criteria with source references. |
| checks | incoming:checks | yes | json | Developer check results and their stated limits. |

#### Outputs

| Name |
| --- |
| verification |
| findings |

#### Results

| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| accepted | All required acceptance criteria are verified and no blocking defect remains. | verification | step:document | none |
| changes-required | Verification demonstrates one or more blocking defects or failed acceptance criteria. | findings | end:changes-requested | none |

### document

#### Role

specification-manager

#### Instruction

Validate owned configuration and update the existing maintained specification to
match the supplied verified behavior, retaining intent, provenance and known limits.
Use the configured specification location; never create another tree in the run.
Record exact updated files and hashes in the receipt. Missing/disabled configuration
or a tree requiring unauthorized migration blocks dispatch or execution; it is not
permission to enable the feature. If an authorized attempted update fails, report
the failure and retained partial changes.

#### Inputs

| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| verification | incoming:verification | yes | markdown | Accepted verified behavior, scope, exact product paths/hashes and limitations. |

#### Outputs

| Name |
| --- |
| documentation |
| documentation-failure |

#### Results

| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| documented | Maintained specification accurately reflects the verified result and required documentation checks pass. | documentation | end:delivered | none |
| failed | An authorized attempted specification update failed with documented partial effects. | documentation-failure | end:documentation-failed | none |
