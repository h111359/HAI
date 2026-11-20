# Reusable skills

Each direct child package has a native SKILL.md entry point with name/description frontmatter and free-form task instructions. Resources belong to the task method; no ROLE persona, empty configuration contract or model policy is imposed. Skills may be used directly or selected by several roles within actual task authority.

Skills provide useful capabilities across roles and workspaces. Backlog and specification methods belong to Backlog-manager and Specification-manager respectively, rather than separate skills. The existing crete-design-package and other packages remain unchanged pending their separate review. Related procedures stay with their actual method owner; shared contracts have one owner.

These are source packages. Installed independent snapshots live in `.hai_env/skills/`; runtime never falls back to this collection. Install dependencies explicitly before dependent roles and review differences before replacement. Existing integration skills can consume one installed service owner's validated settings for compatibility. That coupling does not make them HAI-independent. New portable skills receive sufficient explicit task inputs; callers supply their environment context.

See the [skill convention](../.hai/conventions/skill_conv.md), [tools](../.hai/tools/skills/README.md), [roles](../roles/README.md) and [explicit capability migration](../.hai/procedures/migrate-capabilities.md). Runtime records and generated results stay with their Activity or established product owner, outside reusable definitions.

## Collection scope

Keep reusable project capabilities here. Packages dedicated to this repository's HAI product remain in its environment. Preserve uninstalled packages; verify installed content before removing a repository-specific duplicate. Reusable capabilities may exist in both source and installed collections.

Role and workflow definition management are built into HAI core. Follow [role authoring](../.hai/procedures/manage-role-definitions.md) or [workflow authoring](../.hai/procedures/manage-workflow-definitions.md); no separate administration role or skill is installed or registered.
