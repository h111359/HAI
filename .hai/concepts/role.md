# Role

A role is a job description: responsibilities, scope, professional perspective, expected quality, decision limits and handoff obligations. An AI agent is the executing tool or running worker that follows an assignment. Selecting a role does not launch an agent or grant authority.

Roles reference reusable [skills](skill.md), which own task methods, procedures, knowledge, scripts and templates. Several roles may reuse a skill, and a person or host may use a skill directly within actual task authority. A role may retain genuinely role-specific conduct or resources needed across its skills; it does not copy each skill implementation.

[Workflows](workflow.md) assign roles and expected results with dependencies and accepted inputs. The assigned role chooses suitable available skills; a workflow does not bind a skill. Missing capabilities are dependencies, not successful assignments. [Activities](activity.md) own actual work and retained run evidence; reusable definitions contain no execution status.

Root `roles/<name>/ROLE.md` packages are reusable sources. Installed `.hai_env/roles/<name>/ROLE.md` packages and their explicit catalogue are separate snapshots. Installation, registration, selection and authorization are distinct. Runtime skill lookup uses only installed `.hai_env/skills/`, without source fallback. Model and permission rules remain with the host and shared core.

Settings remain with their actual capability, service or role owner and are stored once. Settings-free roles need no configuration contract. A direct skill may read an installed owner's validated settings without selecting that role. See [role configuration](role-configuration.md), [role convention](../conventions/role_conv.md) and [skill convention](../conventions/skill_conv.md).

A direct role invocation and a spawned sub-agent are distinct execution modes. Apply the shared [execution policy](../conventions/role_conv.md#role-execution-and-delegation), model/capability prerequisites and [invocation convention](../conventions/agent-invocation_conv.md). Core initialization and Activity administration require no optional role.
