# Skill tools

Skills contain reusable task methods with native SKILL.md frontmatter and a free-form Markdown body. They need no ROLE headings, model metadata or empty settings contract. Core host authority and model policy still apply.

From the workspace root, using the verified absolute Python executable:

```text
python -B .hai/tools/hai.py skills validate --request-stdin
python -B .hai/tools/hai.py skills list
python -B .hai/tools/hai.py skills resolve --request-stdin
python -B .hai/tools/hai.py skills install --request-stdin
```

`validate` accepts `{"definition":"skills/crete-design-package/SKILL.md"}` and performs source inspection without initialized environment state. The conservative safe YAML reader supports standard mappings/scalars, reports unsupported syntax without guessing and does not execute a skill. Installed `list` takes no request; `resolve` accepts `{"name":"crete-design-package"}`. The source example is not assumed installed: resolve requires an explicitly installed snapshot. Runtime resolution uses only `.hai_env/skills/`, rejects linked/aliased packages and never falls back to root source skills. All three operations are read-only and reject --apply.

Roles declare quoted comma-separated `metadata.hai-skills`. `roles skills` accepts `{"definition":".hai_env/roles/software-developer/ROLE.md"}` and returns installed method paths independently of optional model resolution. Pure role validation checks source references against root skills and installed references against installed skills. Missing skills are dependencies rather than successful assignments. Workflow definitions name roles and expected results; roles choose suitable skills.

A skill may declare string `metadata.hai-settings-owner`. Direct resolution validates that existing installed owner contract and reads its single `.hai_env/config/roles/<owner>.json`. Invalid or missing owner contracts block dependency resolution; saved settings are not copied and the owner role is not selected. No configuration metadata is required for a settings-free skill.

Installation accepts workspace-relative local `source`, canonical `name` and actual `provenance` with source/reason. Preview without --apply first; apply after review within actual task authorization. For replacement provide `replace: true` and the exact returned `reviewed_differences` list. The installer checks source identity, stages and hashes the candidate, rechecks source and destination before publication, retains a recoverable prior package and reports partial effects without retry or cleanup. Install required skills before dependent roles; role installation never silently acquires them. Installed package updates preserve external selected settings.

Existing monolithic role environments use [explicit capability migration](../../procedures/migrate-capabilities.md). An incomplete capability migration marker blocks installed-dependent role and skill operations. Pure inspection remains available for diagnosis.

`skill_tools.py` exposes read_definition, validate, names, dependencies and resolve to trusted core callers. Parsing does not establish semantic quality or successful execution. Run `run_tests.py --suite skills` with a workspace-owned --work-dir; fixture paths explicitly reject outside-workspace temporary parents. Tests cover direct native skills, two-role reuse, source/installed separation, missing owners/dependencies, reviewed installation, stale previews, publication races and recoverable partial migration. Symlink fixtures may skip when the host lacks privilege.

Source-to-installed installation rebases actual Markdown links outside fenced examples and matching-backtick inline code spans from root roles/skills to canonical installed peers and core owners. Own resources and fenced examples keep their meaning; raw source bytes remain unchanged. Preview differences compare relocated candidate bytes, and staging verifies those transformed hashes. Missing recognized peer/owner links are reported as unavailable dependencies, without source fallback or a readiness claim; this permits skill-first installation followed by the settings-owner role. Missing own-package/core references or unsafe paths block the affected installation. Staged role procedures are validated using the final logical destination rather than the extra staging-folder depth.
