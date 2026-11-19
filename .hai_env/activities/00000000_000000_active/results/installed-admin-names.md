# Installed administration names

The human explicitly requested that installed roles and skills match the hai- identities already adopted in the reusable sources.

Renamed installed packages:

- `.hai_env/roles/role-definition-manager` to `.hai_env/roles/hai-role-definition-manager`.
- `.hai_env/roles/workflow-definition-manager` to `.hai_env/roles/hai-workflow-definition-manager`.
- `.hai_env/skills/role-authoring` to `.hai_env/skills/hai-role-authoring`.
- `.hai_env/skills/workflow-authoring` to `.hai_env/skills/hai-workflow-authoring`.

Updated canonical definition names, self-references, skill dependencies/links and the installed role catalogue under the runtime mutation lock using validated paths and exclusive renames. No configuration files exist for these settings-free roles, and no state/profile/live-workflow references required changes. Updated source collection guidance and current authoring/tool examples. Legacy migration transformation targets and historical manifests/Activity evidence retain their original identities.

Exact original package and catalogue bytes are retained in [the pre-rename backup](../evidence/installed-admin-rename-before.json).

Verification:

- All 41 source/installed definitions validate.
- The registered-role catalogue audit and startup pass; startup lists both prefixed role identities.
- Each renamed installed role resolves its prefixed installed skill; direct resolution of both skills passes.
- All 140 installed resource files remain present under their expected original or renamed paths. Unrelated installed files retain their original hashes.
- Old installed package folders and unprefixed live Markdown identity references are absent.
- Installed actual local Markdown link targets exist; fenced examples are excluded.
- `git diff --check` passes; Git reports only its normal line-ending conversion notice for the catalogue.

No commit or Activity closure was requested or performed. Broader skill portability refactors remain pending. The previously recorded best-effort native chronicle coverage limitation is not resolved by this naming change.
