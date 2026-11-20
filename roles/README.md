# Reusable roles

Direct child folders contain the reusable ROLE.md job descriptions. This flat source collection is separate from installed `.hai_env/roles/` snapshots and the explicit installed catalogue. Installation, registration, selection and actual authorization are distinct; source inspection never invokes a role.

Roles are complete job packages: responsibility, scope, quality, decisions, authority limits, handoffs and any job-specific conventions, procedures, scripts or templates. They may use independent skills when a task needs them; a role need not require a skill. Declared required skills use quoted comma-separated hai-skills metadata and matching Skills links. Each method and its resources have one owner. Backlog-manager owns its backlog methods without requiring a skill; Software-developer and quality-assurance currently share quality-verification.

Actual settings owners retain their contract and single saved file outside the package. Settings-free roles need no empty contract or procedure tree. Preserve model declarations; skills grant no model override or permissions. See the [role convention](../.hai/conventions/role_conv.md), [skill convention](../.hai/conventions/skill_conv.md), [skill collection](../skills/README.md) and [migration procedure](../.hai/procedures/migrate-capabilities.md).

Validate selected sources with roles validate. Install required skills first, then preview role installation, review local installed differences and chosen-setting compatibility, apply the explicit installation and register separately when requested. Preserve workspace-only customizations; source updates do not update installed snapshots automatically. Runtime lookup uses installed packages only.

## Collection scope

Keep reusable project capabilities here. Packages dedicated to this repository's HAI product remain in its environment. Preserve uninstalled packages; verify installed content before removing a repository-specific duplicate. Reusable capabilities may exist in both source and installed collections.

Role and workflow definition management are built into HAI core. Follow [role authoring](../.hai/procedures/manage-role-definitions.md) or [workflow authoring](../.hai/procedures/manage-workflow-definitions.md); no separate administration role or skill is installed or registered.
