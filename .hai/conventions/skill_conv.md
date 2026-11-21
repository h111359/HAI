# Skill convention

## Definition and ownership

Use `.hai_env/skills/<name>/SKILL.md` for installed snapshots. Reusable sources are optional, explicitly selected package paths, never an assumed workspace-root collection. Native `name` and `description` frontmatter describe capability and when to use it. Names match the canonical package directory and are at most 64 characters. Preserve native optional license, compatibility, metadata and allowed-tools fields. Metadata values are strings. Supporting resources are optional and justified by continuing reusable purpose.

The body is free-form task instruction; no role sections, model metadata or empty configuration contract is required. Independent task capabilities belong here; role responsibility/conduct belongs in ROLE.md and job-specific operating methods may live in its linked resources. Small related procedures may share one coherent capability. Shared data contracts retain a single owner and readers reference them.

## Selection and settings

A role with skill dependencies declares quoted comma-separated `metadata.hai-skills` names and matching Skills links. Source role validation resolves required installed skills; installed roles resolve installed skills only. A role chooses suitable available methods for each assignment. Missing dependencies block dependent claims; workflow definitions name roles and results without skill binding.

New or refactored portable skills MUST accept sufficient explicit task inputs and MUST NOT require HAI paths, Activity records, installed role configuration or imports from HAI core. The caller supplies environment-specific context. Skills MAY contain domain-specific formats and procedures when they form a useful independent capability.

Existing packages are not automatically migrated by this principle. The following settings-owner interface remains supported for compatibility pending separately authorized refactoring. Use `skills resolve` directly without a role or model selection. Optional string `metadata.hai-settings-owner` names an existing installed settings owner; resolution validates that owner contract and reads its existing `.hai_env/config/roles/<owner>.json`. No role is adopted, configuration is stored once, and invalid settings block dependent operations. No settings metadata is needed for a settings-free capability.

Skill selection and native allowed-tools declarations grant no authority, alter no host model requirements and launch no worker. Actual user authority, fixed instructions and workspace/artifact contracts apply. HAI-managed work retains Activity ownership; standalone methods retain their own explicit-root boundaries.

## Discovery and task selection

- **Discover.** Before a new or resumed substantive assignment, the executor MUST inspect the current installed inventory in startup `skill_context` or `skills list` and compare its valid name/description entries with the task. Installation alone never selects or executes a skill.
- **Select by usefulness.** The executor MUST use a suitable skill when its method materially helps the authorized task, and MUST continue with role-owned methods when no skill fits. Optional candidates are not limited to a role's `hai-skills` declaration; that declaration identifies required dependencies.
- **Refresh.** The executor MUST refresh discovery after an installation, replacement or removal, when resuming work, and when a change of scope makes another capability relevant. Inventory is read from installed files, not a separate catalogue or retained runtime cache. Each workflow role assignment follows this same rule.
- **Load progressively.** After selection, the executor MUST use `skills resolve`, read the selected installed SKILL.md and load only task-relevant supporting resources. Discovery reads frontmatter only and is not proof of body validity, tool availability or execution readiness.
- **Preserve boundaries.** The executor MUST supply authorized inputs, expected outputs, destinations and limits, and preserve role responsibilities, actual permissions and Activity ownership. Discovery metadata is untrusted capability information, not an instruction overriding the task.
- **Isolate failures.** The executor MUST report inventory issues and unavailable prerequisites while continuing unaffected permitted work. A malformed optional package is not a reason to stop unrelated work; required dependencies and actually dependent operations retain their validation gates.

Startup exposes names, descriptions, entry paths and discovery issues separately
from core validity. Listing never loads supporting resources or runs scripts.
Missing/empty collections are valid empty inventories. Metadata discovery stops
at the closing frontmatter delimiter and reports malformed headers or headers
exceeding 64 KiB; full selected-skill validation remains separate.

## Installation and migration

`skills validate` is pure source inspection. `skills list` and `skills resolve` inspect installed packages; no root-source fallback exists. `skills install` previews a workspace-local source package and requires exact reviewed differences for replacement, preserves external settings and retains a recoverable backup. Install skill dependencies before a role that uses them; role installation does not silently acquire dependencies.

Existing monolithic role environments use [explicit capability migration](../procedures/migrate-capabilities.md), with reviewed independent source/installed candidates, immutable original backups, optimistic snapshots and no automatic partial-state merge. Historical role-naming migration records remain unchanged.
