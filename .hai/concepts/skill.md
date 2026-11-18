# Skill

A skill is a reusable capability: task instructions, internal procedures, supporting scripts, templates and task-specific knowledge or conventions. Its entry point is `SKILL.md`. A skill explains how to perform a task; a role defines who is responsible for it and the quality, decision and handoff obligations.

A role references skills rather than copying their methods. Several roles may use the same skill. Direct skill use needs no HAI role selection, within actual task authority and applicable host instructions. A skill supplies neither permissions nor model policy and does not launch an AI agent.

Source skills live under root `skills/`; installed snapshots live under `.hai_env/skills/`. Runtime lookup uses installed packages only and reports unavailable dependencies. Native skills have name/description frontmatter and free-form instructions; HAI does not impose ROLE headings, an empty configuration contract or a role persona.

Reusable definitions carry no run status or generated outputs. Actual task evidence belongs to its Activity or established product owner. Shared contracts have one owner. When a capability uses installed role-owned service settings, it reads that owner's single validated configuration; this does not adopt the owner role or duplicate settings.

See [role](role.md), [workflow](workflow.md), [Activity](activity.md) and [skill convention](../conventions/skill_conv.md).
