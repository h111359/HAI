# Skill

A skill is an independently usable, reusable capability: task instructions, internal procedures, supporting scripts, templates and task-specific knowledge or conventions. Its entry point is `SKILL.md`. A skill packages a useful task method and its resources without requiring a HAI role or HAI environment. A role owns responsibility, decisions and job-specific operating knowledge, and can use skills as needed. Domain-specific capabilities can be portable; universal applicability is not required.

Skill extraction is optional: job-specific methods may stay with a role. When a role uses a skill, it references that skill rather than copying its method. Several roles may use the same skill. Direct skill use needs no HAI role selection, within actual task authority and applicable host instructions. A skill supplies neither permissions nor model policy and does not launch an AI agent.

Installed snapshots live under `.hai_env/skills/`. Source packages may be supplied from an explicitly selected workspace location; no source library is required or discovered. Runtime lookup uses installed packages only and reports unavailable dependencies. Native skills have name/description frontmatter and free-form instructions; HAI does not impose ROLE headings, an empty configuration contract or a role persona.

Reusable definitions carry no run status or generated outputs. Actual task evidence belongs to its Activity or established product owner. Shared contracts have one owner. Portable skills receive sufficient explicit inputs, including locations and relevant conventions, without importing HAI core or discovering role settings. Existing settings-owner integration remains readable for compatibility; it does not establish HAI independence and is not the pattern for newly authored portable skills.

See [role](role.md), [workflow](workflow.md), [Activity](activity.md) and [skill convention](../conventions/skill_conv.md).

## HAI definition maintenance

HAI role/workflow definition maintenance is built into core [role authoring](../procedures/manage-role-definitions.md) and [workflow authoring](../procedures/manage-workflow-definitions.md). These methods are core procedures, not installed skills.
