# HAI role source library

This is the golden source for reusable HAI roles. It is not a runtime registry.
AI agents follow roles; installing a role does not launch an AI agent or grant
permission to work. Genuine skills remain separate and use SKILL.md.

The roles/ folder contains business-analyst, solution-architect,
software-developer, quality-assurance, specification-manager, backlog-manager,
role-definition-manager, workflow-definition-manager, git-manager and release-manager.
Each complete package has a ROLE.md entry point and a configuration/contract.json.
The roles/ depth matches .hai_env/roles/ so relative core and peer links remain valid.

The host uses the core roles commands to install, validate and register selected
complete packages under .hai_env/roles/. Registration is explicit in that folder's
catalogue.md. Core startup and administration need no optional role. This library
is excluded from the core release ZIP; obtain selected packages from the chosen
release source when needed.

Maintain reusable source here. Update an installed snapshot only within the
requested scope after reviewing local differences or unknown provenance. Preserve
workspace settings under .hai_env/config/roles/ and retain a recoverable prior
package. Workspace-only customizations remain local unless separately promoted.
Source edits do not update installed snapshots automatically.

Use role_tools.py validate for workspace-contained source inspection. Validate
complete candidates in an isolated installed layout with compatible core and peers
before installation; roles audit and runtime resolution use the installed registry.
The host coordinates execution, while the core owns environment and Activity records.

Existing projects require the explicit [role migration](../.hai/procedures/migrate-roles.md).
