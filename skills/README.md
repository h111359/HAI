# Reusable skills

Each direct child package has a native SKILL.md entry point with name/description frontmatter and free-form task instructions. Resources belong to the task method; no ROLE persona, empty configuration contract or model policy is imposed. Skills may be used directly or selected by several roles within actual task authority.

The existing crete-design-package skill remains unchanged. Extracted capabilities cover backlog management, requirements analysis, Git operations, quality verification, release management, role authoring, software implementation, solution design, specification management and workflow authoring. Small related procedures stay together in a coherent capability; shared contracts have one owner.

These are source packages. Installed independent snapshots live in `.hai_env/skills/`; runtime never falls back to this collection. Install dependencies explicitly before dependent roles and review differences before replacement. A direct skill can consume one installed service owner's validated settings without selecting that role or duplicating saved configuration.

See the [skill convention](../.hai/conventions/skill_conv.md), [tools](../.hai/tools/skills/README.md), [roles](../roles/README.md) and [explicit capability migration](../.hai/procedures/migrate-capabilities.md). Runtime records and generated results stay with their Activity or established product owner, outside reusable definitions.
