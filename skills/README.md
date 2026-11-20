# Reusable skills

Each direct child package has a native SKILL.md entry point and an independently
useful method, with only the resources needed for that capability. Skills work
without a selected role or HAI environment. Callers supply task inputs, expected
results, destinations and applicable limits.

- [crete-design-package](crete-design-package/SKILL.md) prepares a human-reviewable design proposal for technical or nontechnical topics.

Job-specific operating manuals now belong to the respective role packages under
[roles/](../roles/README.md). Workspace-only HAI release and framework-review
methods remain with their installed roles, outside this shared collection.

These are source packages. Installed snapshots live in .hai_env/skills/;
runtime never falls back to the source collection. Install required skills before
dependent roles, preview replacements and preserve local differences. Existing
legacy settings-owner integration remains readable by core for compatibility;
it is not required by the portable skills in this collection.

See the [skill convention](../.hai/conventions/skill_conv.md) and
[tools](../.hai/tools/skills/README.md). Generated results and run evidence belong
to the caller's designated destinations rather than reusable packages. HAI role
and workflow authoring remain core functionality.
