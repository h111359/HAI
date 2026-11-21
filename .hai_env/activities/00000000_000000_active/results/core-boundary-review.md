# Core deployment boundary review

## Conclusion

The core does not universally require the development library to start. An isolated
workspace containing only .hai/ and a minimal .hai_env/ starts successfully and
lists an empty skill collection. Installed role/skill/workflow lookup already uses
the environment rather than falling back to the development sources.

However, development-workspace conventions have leaked into generic core contracts,
live readiness/protection logic, source-package handling and shipped tests. Root
roles/, skills/ and workflows/ are not merely examples everywhere. A deployed
consumer can encounter real failures or restrictions because of those assumptions.

Review scope: all153core files inventoried; full text/Markdown-link and Python AST
candidate scans, followed by inspection of relevant paths and core-only probes.
This is not a claim that every optional operation or test suite was executed.
[File inventory and AST scan](../evidence/core-boundary-review/scan.json) and
[complete candidate line catalogue](../evidence/core-boundary-review/candidate-locations.json)
retain the search coverage. Candidate matches include internal paths and legitimate
examples; the findings below classify the actual issues.

## Findings

### F1. Root development names affect normal readiness ? high priority

.hai/tools/role_state.py:6-7,19-29 automatically inspects hai_agents_library/,
hai_roles_library/ and roles/ alongside installed paths, without environment
configuration. status() feeds startup and require_ready(), including skill lookup.

Reproduction: create an unrelated regular file named roles in a clean consumer
workspace. Core startup remains valid but reports a role-migration issue; skills
list becomes blocked with "Role root must be a directory: roles". An unrelated
root asset therefore affects ordinary installed operations. Legacy detection should
retain canonical internal paths, while external legacy/library locations should
require explicit context/configuration rather than universal probing.

### F2. Development folder names are globally reserved ? high priority

Fixed external source/library names are reserved in:

| File | Location |
| --- | --- |
| .hai/tools/configuration/configuration_tools.py |151and222:workspace directory validation and configured reserved-path collection. |
| .hai/tools/startup/startup_check.py |160:specification/store path protection. |
| .hai/tools/runtime/activities.py |44:Activity store validation. |
| .hai/tools/runtime/workflow_config.py |26:workflow output-location validation. |

The lists include root roles, skills, workflows and legacy source-library names.
These are deployment namespace restrictions even when the paths do not exist and
no such library is configured. The core-only probe accepts product/notes but rejects
roles/product, skills/product and workflows/product as reserved overlaps. This can
prevent a consumer's explicit custom location choices. Protect actual HAI stores,
configured resources and legitimate security metadata; do not infer HAI ownership
of ordinary root names. Generic .git/.aws/.codex/.agents protections are a separate
security concern and should not be removed as a side effect of this correction.

### F3. Source dependency resolution and link rebasing assume root libraries

- .hai/tools/skills/skill_tools.py:107-115 selects root skills/ for every
  non-installed role, instead of receiving its source dependency context.
- .hai/tools/runtime/package_content.py:47-63 recognizes root roles/ and skills/
  as source peer collections and maps them to installed peers automatically.
- .hai/tools/roles/role_tools.py:568-572,619-621,625-645 invokes that source
  dependency behavior during definition inspection. Installed execution remains
  restricted to .hai_env/roles/ by resolve at667.

These are conditional source-authoring/install behaviors, not unconditional
startup dependencies. A caller-supplied source package is legitimate; inferring a
particular sibling library from its workspace-root name is the portability issue.
Peer source roots/mappings should be explicit task/configuration inputs. Internal
Python imports from .hai/tools/roles and .hai/tools/skills are not external libraries.

### F4. Generic authoring/layout instructions prescribe this repository's layout

The affected instructions and their consumers are catalogued below. Some explicitly
prescribe root collections; others inherit that definition of source/origin or use
it in validation and staging guidance. Statements saying sources are data and not
runtime fallback are correct, but do not make the fixed source layout portable.

- .hai/start.md:85 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/concepts/definition-management.md:15 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/concepts/role.md:11 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/concepts/skill.md:7 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/concepts/workflow.md:17 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/conventions/framework-layout_conv.md:11 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/conventions/role-authoring_conv.md:46 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/conventions/role_conv.md:5 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/conventions/skill_conv.md:5 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/conventions/workflow-authoring_conv.md:25 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/conventions/workflow-authoring-format3_conv.md:3 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/procedures/author-role-establish-scope-and-inspect.md:29 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/procedures/author-role-create-definition.md:23 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/procedures/author-role-update-definition.md:48 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/procedures/author-role-validate-or-audit.md:27 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/procedures/manage-role-definitions.md:34 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/tools/roles/README.md:44 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/tools/skills/README.md:14 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/tools/workflows/README.md:76 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.
- .hai/tools/runtime/README.md:52 - source/origin/layout guidance, inherited authoring contract or hardcoded source example.

Notable direct prescriptions: framework-layout_conv.md:26,36; role-authoring_conv.md:69;
skill_conv.md:5; concepts/role.md:11; concepts/skill.md:7; concepts/workflow.md:17;
workflow-authoring-format3_conv.md:3; manage-role-definitions.md:56; and source-target
selection in author-role-establish-scope-and-inspect.md:29. Core authoring should
operate on installed definitions or explicitly selected/configured authoring
locations; maintaining this development repository is one such environment.

The runtime README's workflow-install example at100-105 assumes the non-shipped
workflows/software-development.md; skill-tool examples similarly use this
repository's root design-package source. Examples should use actual caller-supplied
sources or clearly marked placeholders, not appear to be ready-to-run core assets.
The outward Markdown-link scan found one root-source target inside a fenced role
template (role_conv.md:133), not an unconditional missing live-document link.

### F5. Legacy migrations contain fixed external source destinations

- .hai/tools/runtime/role_migration.py:18-20 and its dependent planning/move logic.
- .hai/tools/role_upgrade.py:6-9,41-52,76-92:fixed source-library rewrite rules.
- .hai/tools/runtime/capability_migration.py:9,27-43:fixed four-root destination
  allowlist and hai_roles_library retirement logic.
- .hai/procedures/migrate-roles.md:55,92 and
  .hai/procedures/migrate-capabilities.md:5,26-27,34-39.

These are explicit, versioned historical conversions, not automatic normal
installation. Preserve their historical records and recovery mappings. Scope any
future external-library conversion to explicitly identified inputs/destinations;
do not globally reinterpret old history or silently rerun migrations. Source
library migration must not be a prerequisite for a consumer that never had one.

### F6. Shipped regression checks depend on development assets

| File | External dependency and effect |
| --- | --- |
| .hai/tools/skills/test_skill_tools.py:157,196,222,249 | Actual root roles/skills packages used by four real-package integration cases; not self-contained in the core ZIP. |
| .hai/tools/runtime/tests/test_configurable_workflows.py:14 | Actual root workflows/software-development.md;12tests fail in the core-only probe when the file is absent. |
| .hai/tools/activities/test_role_migration.py:81 | Reads root README.md and INSTALL.md without an absence guard. |
| .hai/tools/activities/test_role_migration.py:90-101 | Optional SourceStagingTests skip without roles/, but existence of that root name assumes a compatible roles+skills development collection. |
| .hai/tools/runtime/tests/test_workflows.py:91-102 | Optional developer integration skips when its role source is absent, but otherwise copies fixed root collections and installed skills. |
| .hai/tools/run_tests.py:11,56-62 | Default runner includes these suites, exposing their development dependencies as core regression failures. |

Development integration tests can legitimately exercise this repository's source
library, but should live in development tooling or require explicit development
fixtures. Core-distributed tests should carry self-contained fixtures under .hai/.
Skipping a guarded integration is not itself a startup failure; the report
separates guarded cases from unguarded failures.

Related but inside the permitted boundary: test_layout_migration.py:92 reads an
optional installed Specification-manager contract and skips when absent. That is
not an outside-folder violation; a self-contained fixture would still improve the
core-test boundary.

## Reproduction evidence

[Raw core-only results](../evidence/core-boundary-review/reproductions.json):

- Core-only startup:exit0, valid.
- Core-only skills list:exit0, empty inventory.
- Add unrelated roles file:startup stays core-valid with migration issue;
  skills list exits1/blocked.
- Configured directory probe:ordinary product path accepted; three development
  namespace choices rejected without any configured development library.
- Shipped configurable-workflow suite:12tests run,12errors because the external
  sample definition is absent. These are expected audit reproductions, not a new
  regression introduced into the real repository.

The fixture lives only in Activity work/test-work; production core/packages and
settings were not changed.

## References that should remain supported

Configured Activity/specification locations, workflow output locations, user-chosen
package sources and task input files may be outside .hai_env/ within the workspace.
They are explicit environment/task data, not fixed core dependencies. A corrective
change must not prohibit them or move user data implicitly.

Chronicle sources can also be outside the workspace through explicit bindings and
host authorization. source_discovery.py:92 has a Codex-specific default derived
from codex_home/CODEX_HOME/Path.home rather than this development repository. Treat
this as an optional host-adapter convention, not a general core prerequisite. If
the boundary is meant to prohibit implicit external host defaults too, expose that
choice explicitly in environment adapter configuration; preserve existing source
attribution. Python and installed host tools are execution prerequisites, not
workspace library assets that should be bundled into .hai/.

## Recommended correction order

1. Establish the invariant in core concepts/layout:only .hai/ and .hai_env/ are
   fixed framework roots; other paths come from explicit task/environment context.
2. Remove unconfigured development namespace probes/reservations from ordinary
   runtime paths while preserving actual store/security/legacy safeguards.
3. Give source inspection, dependency mapping, installation and authoring explicit
   source-root context instead of inferring this repository's directory names.
4. Update the catalogued instructions/examples together and isolate historical
   migration behavior without rewriting existing migration records.
5. Separate development integration tests from portable core regression fixtures.
   Add core-only deployment and unrelated-root-name regression cases.

No framework fixes, commit or Activity closure were performed in this review.
