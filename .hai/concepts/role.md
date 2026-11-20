# Role

A role is a complete job package whose ROLE.md entry defines its job description: responsibilities, scope, professional perspective, expected quality, decision limits and handoff obligations. An AI agent is the executing tool or running worker that follows an assignment. Selecting a role does not launch an agent or grant authority.

A role may own job-specific conventions, procedures, scripts, templates and domain knowledge in supporting resources. Keep ROLE.md concise and link the resources required for each operation. A role package is itself shareable across workspaces. It need not depend on a skill.

A role may use independently useful [skills](skill.md) when needed. Each skill owns its method and supporting resources; the role supplies task inputs, environment context and its applicable decision limits. A person or another role may invoke that capability directly. Extraction follows independent usefulness and coherent ownership, rather than file type or the number of procedure steps. Do not duplicate a skill implementation inside its callers.

[Workflows](workflow.md) assign roles and expected results with dependencies and accepted inputs. The assigned role chooses suitable available skills; a workflow does not bind a skill. Missing capabilities are dependencies, not successful assignments. [Activities](activity.md) own actual work and retained run evidence; reusable definitions contain no execution status.

Root `roles/<name>/ROLE.md` packages are reusable sources. Installed `.hai_env/roles/<name>/ROLE.md` packages and their explicit catalogue are separate snapshots. Installation, registration, selection and authorization are distinct. Runtime skill lookup uses only installed `.hai_env/skills/`, without source fallback. Model and permission rules remain with the host and shared core.

Settings remain with their actual capability, service or role owner and are stored once. Settings-free roles need no configuration contract. The role supplies validated environment settings to portable skills as explicit task inputs. Existing direct skill settings-owner resolution remains supported for compatibility during separately authorized refactoring. See [role configuration](role-configuration.md), [role convention](../conventions/role_conv.md) and [skill convention](../conventions/skill_conv.md).

A direct role invocation and a spawned sub-agent are distinct execution modes. Apply the shared [execution policy](../conventions/role_conv.md#role-execution-and-delegation), model/capability prerequisites and [invocation convention](../conventions/agent-invocation_conv.md). Core initialization and Activity administration require no optional role.

## Built-in authoring

HAI maintains its own role definitions through [core role authoring](../procedures/manage-role-definitions.md). The host follows it directly; optional role and skill packages are not prerequisites. Runtime remains the owner of installation and registration.
