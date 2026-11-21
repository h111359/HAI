# Manage role definitions

## Description

Create and maintain meaningful, self-sufficient role definitions and verify their
convention compliance, keeping authorship separate from installation, registration
and agent execution.

## Inputs

| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
| Request | Actual creation, update or review request and authority | Mandatory | Human and authorized context | Resolve necessary scope before dependent changes. |
| Target | Definition path or new definition objective | Mandatory | Request or inspected workspace | Retrieve known facts; clarify consequential gaps. |
| Context | Applicable instructions, current Activity and source evidence | Mandatory for substantive work | Host and runtime | Report missing prerequisites; continue permitted independent diagnosis. |

## Prerequisites

Apply fixed instructions, workspace boundaries and valid current Activity requirements. No authoring role, skill installation, registration or specialist model profile is required. Authoring does not grant authority for installation, registration, workflow execution or other runtime effects.

## Rules

- **Settings separation:** The host MUST preserve workspace configuration files during definition and package operations and report required migrations without performing them implicitly.
- **Installer boundary:** The host MUST return package installation/replacement and registration requests through host coordinator to runtime rather than perform them.
- **Catalogue ownership:** The host MUST preserve the workspace catalogue and return any required metadata synchronization to runtime.
- **Requested creation:** The host MUST NOT create a definition outside the user's explicitly requested work.
- **Existing row:** The host MUST return the changed installed identity, exact decoded description and verification evidence when an authorized definition update requires runtime to synchronize an existing row.
- **Unregistered targets:** The host MUST leave an unregistered definition unregistered; even a combined request returns the separate registration work to runtime through host coordinator.
- **Definition inspection:** The host MAY inspect, maintain or validate unregistered definitions as data within the user's requested work.
- **No target execution:** The host MUST NOT treat inspection, authoring or validation as target invocation or permission to execute the target.
- **Read-only review:** The host MUST NOT repair definitions, catalogues or configuration while auditing or validating them.
- **Repair distinction:** The host MUST distinguish review findings from separately authorized repairs.
- **Definition paths:** The host MUST use the target's defined installed or source-package location with resolved paths inside the permitted workspace directories.
- **Source authority:** The host MUST edit shared package behavior in the golden source and leave installed snapshots unchanged until the human explicitly requests their update.
- **Local customizations:** The host MUST report local changes or an unknown installed baseline as dependencies for runtime's replacement review, without copying a replacement itself.
- **No source execution:** The host MUST treat source-package inspection, maintenance and disposable validation staging as data operations rather than invoking that package as a role.
- **Separate counterparts:** The host MUST distinguish a matching source package from runtime name collisions between workspace definitions.
- **Workspace changes:** The host MUST require a valid initialized environment before changing workspace definitions.
- **Fixed instructions:** The host MUST apply the fixed mandatory instructions before dependent work regardless of state validity, accepting an existing readable empty file.
- **Independent checks:** The host MAY check definition format or diagnose missing prerequisites without initialized or compatible environment state.
- **Tracked maintenance:** The host MUST require Activity context for substantive HAI maintenance and audits after bootstrap.
- **Unrelated content:** The host MUST preserve unrelated resources, catalogue rows/prose, optional metadata, state and profiles.
- **Useful resources:** The host MUST NOT create supporting resources without a demonstrated need.
- **Shared references:** The host MUST reference shared conventions and other roles' procedures instead of copying them into a target.
- **Write interruption:** The host MUST stop dependent writes when inputs change, an affected catalogue is malformed, a conflict appears or an operation partially fails.
- **Partial results:** The host MUST preserve and report completed work after an interruption.
- **No automatic recovery:** The host MUST NOT automatically retry, clean up or repair a partial operation.
- **Several-file writes:** The host MUST NOT claim that coordinated file changes always succeed or fail together.
- **Unrun checks:** The host MUST report unavailable checks as unrun rather than passed.
- **Core method.** The host MUST follow the linked core authoring method and report unavailable prerequisites without claiming success. Authoring grants no additional authority.

### Scope

- Create, update, validate, and audit workspace definitions and
  their necessary supporting resources.
- Maintain explicitly selected source packages as data, at their caller-selected locations.
- Return validated canonical identity, decoded description, contract/check evidence and required catalogue changes through host coordinator to runtime; do not mutate the workspace catalogue or install packages.
- Perform repairs or migrations only within an explicitly requested scope.
- Do not invoke agents, coordinate execution, change environment state or model
  profiles, or initialize an environment. host coordinator owns execution and orchestration;
  runtime owns environment configuration, package installation, the workspace catalogue and lightweight startup validation.
- Audits are read-only. No operation implicitly unregisters, deletes, renames,
  repairs unrelated material,.

### Out of scope

Agent execution/orchestration, package download/installation/replacement, runtime catalogue writes/registration, environment initialization/configuration, state/profile changes, and unrequested repair, renaming, deletion, unregistration or ownership changes.

## Steps

1. Establish the request, target and authorized scope. Apply the [core authoring method](../conventions/role-authoring_conv.md) and its linked scope/inspection procedure.
2. Follow the method's create, update or read-only validation/audit procedure for the requested operation. Preserve its complete prerequisites, decision rules, output contracts and supporting conventions.
3. Validate structure with core tools and assess meaning separately. Return exact findings and partial results; authoring and validation do not execute the target or grant approval.
4. Use separately authorized runtime operations for any requested installation or registration. Preserve independent verification and human decision requirements; report pending effects accurately.

## Outputs

Actual authored paths or read-only findings, structural and semantic evidence, preserved revisions, unresolved decisions and separately pending runtime operations. Never imply execution, registration or approval from authoring alone.

## References

- [Core authoring method](../conventions/role-authoring_conv.md) - required before dependent work.
- [Role convention](../conventions/role_conv.md) ? responsibilities, host policy and execution boundaries.
