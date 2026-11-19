# Manage workflow definitions

## Description

Maintain understandable, valid processes that coordinate HAI roles through
explicit instructions, file contracts and result-dependent next steps.

## Inputs

| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
| Request | Actual creation, update or review request and authority | Mandatory | Human and authorized context | Resolve necessary scope before dependent changes. |
| Target | Definition path or new definition objective | Mandatory | Request or inspected workspace | Retrieve known facts; clarify consequential gaps. |
| Context | Applicable instructions, current Activity and source evidence | Mandatory for substantive work | Host and runtime | Report missing prerequisites; continue permitted independent diagnosis. |

## Prerequisites

Apply fixed instructions, workspace boundaries and valid current Activity requirements. No authoring role, skill installation, registration or specialist model profile is required. Authoring does not grant authority for installation, registration, workflow execution or other runtime effects.

## Rules

- **Requested changes:** The host MUST limit writes to the user's
  requested definitions and necessary Activity-owned revision evidence.
- **Read-only checks:** The host MUST NOT repair files while
  validating or auditing; it MUST return proposed repairs separately.
- **No execution:** The host MUST NOT invoke participants or
  execute, advance, resume or cancel a target workflow.
- **Semantic findings:** The host MUST distinguish format checks
  from assessments of meaning and from current execution readiness.
- **Role boundaries:** The host MUST preserve participant rules,
  configuration ownership, task authority and independent-verification obligations.
- **Revision preservation:** The host MUST retain prior definition
  bytes before material updates and MUST NOT alter existing run snapshots or results.
- **No invented evidence:** The host MUST NOT invent user decisions,
  approvals, available models/tools or completed verification.
- **Unrelated content:** The host MUST preserve unrelated definitions,
  installed/source packages, settings and managed run records.
- **Partial operations:** The host MUST preserve and report partial
  writes and changed-input conflicts rather than blindly retry, clean up or roll back.
- **Core method.** The host MUST follow the linked core authoring method and report unavailable prerequisites without claiming success. Authoring grants no additional authority.

### Scope

- Author and maintain requested single-file definitions in `.hai_env/workflows/`.
- Validate selected definitions or a bounded collection using core tools, then
  assess role responsibility, instruction sufficiency and meaningful handoffs.
- Return findings, exact changes, verification scope and unresolved decisions.

### Out of scope

Workflow execution, participant invocation, run-state writes, Activity lifecycle,
role installation/registration, core/profile/configuration changes, product edits
and unrequested repair, migration, deletion or publication.

## Steps

1. Establish the request, target and authorized scope. Apply the [core authoring method](../conventions/workflow-authoring_conv.md) and its linked scope/inspection procedure.
2. Follow the method's create, update or read-only validation/audit procedure for the requested operation. Preserve its complete prerequisites, decision rules, output contracts and supporting conventions.
3. Validate structure with core tools and assess meaning separately. Return exact findings and partial results; authoring and validation do not execute the target or grant approval.
4. Use separately authorized runtime operations for any requested installation or registration. Preserve independent verification and human decision requirements; report pending effects accurately.

## Outputs

Actual authored paths or read-only findings, structural and semantic evidence, preserved revisions, unresolved decisions and separately pending runtime operations. Never imply execution, registration or approval from authoring alone.

## References

- [Core authoring method](../conventions/workflow-authoring_conv.md) - required before dependent work.
- [Role convention](../conventions/role_conv.md) ? responsibilities, host policy and execution boundaries.
