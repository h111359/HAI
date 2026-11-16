# HAI role rename: dependency review

Baseline: 94ac354. This audit informed the implemented rename. The user accepted
explicit migration and ROLE.md entries, then approved specialist implementation
and independent review. The workspace migration has completed; see
[implementation result](role-rename-result.md) and the Activity verification evidence.

## Accepted decisions

1. New live names follow explicit migration. Historical records remain readable;
   old commands and reusable workflow definitions are not transition aliases.
2. HAI role packages use ROLE.md. Genuine reusable skills keep SKILL.md.

The inventory below describes the observed pre-migration baseline. The dependency
map records the design applied; it does not request another approval.

## Meaning that should stay consistent

An AI agent executes work. A HAI role is the reusable instruction/tool/convention
package that an AI agent can follow. One executing agent can follow different
roles; one role can be used by multiple agents. Selecting or installing a role
neither creates an executor nor grants authority. Direct execution, separate
invocation, model requirements and independent-review rules retain their meaning.

## Current verified inventory

- Startup and the full installed package audit pass.
- There are 11 installed registered packages. Ten have library counterparts;
  hai-framework-advisor is installed only and must not be dropped.
- agent-definition-manager differs from its library counterpart in five files:
  SKILL.md and procedures/create-definition.md, establish-scope-and-inspect.md,
  update-definition.md, validate-or-audit.md. Their origin is not inferred.
  Rename both snapshots independently and preserve their differences; do not
  overwrite the installed copy with the library during this change.
- Saved role-owner settings exist for git-manager and specification-manager.
  Their values, unknown properties, Git enablement/auto-push choice and disabled
  specification feature must survive unchanged.
- Two reusable workflows and one template use the version-1 Agent heading.
  The only retained workflow run is a finished feasible change-assessment pilot;
  the current Activity has no workflow runs, so no running workflow blocks this
  workspace's migration. Migration must still handle that possibility elsewhere.
- A word-level scan finds agent references in 242 tracked files outside Activity
  history. This includes actual executing agents, generic skills and completed
  backlog/release records; it is not a count of files that should all be replaced.

## Proposed dependency map

| Area | Proposed treatment |
| --- | --- |
| Installed packages | .hai_env/agents -> .hai_env/roles; update catalogue header/links and all installed packages, including workspace-only ones. |
| Library | hai_agents_library/agents -> hai_roles_library/roles, preserving the two-level depth required by relative core links. |
| Saved settings | .hai_env/config/agents -> .hai_env/config/roles; preserve values and external ownership, no feature enablement. |
| Definition manager | agent-definition-manager -> role-definition-manager in package identity, source/installed paths, descriptions, contracts, catalogue and references. |
| Definition tools | .hai/tools/agents/agent_tools.py and imports/suite registration -> role-oriented equivalents; update startup/environment/package consumers together. |
| Runtime interface | Add canonical roles commands and role identity fields in package/configuration/model-resolution requests/results. packages can remain the neutral install operation group. Old live aliases are rejected after explicit migration. |
| Configuration contract | The current exact schema requires an agent identity key and supports contract formats 1 and 2. A role key requires deliberate versioned support; do not silently reuse an existing format with a new meaning. |
| Workflow format | Agent section and parsed step.agent mean package assignment; change these to Role/role through a versioned format, updating examples, validator, authoring manager and dispatcher together. |
| Invocation metadata | The legacy agent field denotes the selected package; a new manifest can identify the HAI role while executor handle and invocation UUID still identify actual execution. Old manifests remain historical evidence. |
| Startup/menu | Registered agents, agent setup and agent:<name> choices become roles, role setup and role:<name>. Keep availability checks separate from registration. |
| Security paths | Protect new role/config roots and relevant legacy roots in startup, configuration, Activity-store and workflow-input checks. Renaming must not weaken alias/link/containment guards. |
| Instructions | Update both library and installed role instructions, relative links, configuration helpers and authoring rules. Clarify whether each actor is the role author or AI agent performing a role. |
| CI/distribution | Update suite/import paths and fresh-workspace fixtures. Keep source library outside the core ZIP, as today; assess candidate release/upgrade notes without rewriting published manifests or publishing anything. |

This table proposes canonical names; it does not authorize blanket substitutions.

## Names and data that should remain

- AI agents, spawned subagents, executor handles and invocation identities still
  describe real execution. work/agents/<role>/<invocation-id> remains an appropriate
  place for an executing agent's work; it is not the installed role registry.
- Chat role=human/assistant/agent/system describes the speaker category, not a HAI
  role package. Do not change those values as a package rename.
- .hai_env/config/agent_instructions.md contains workspace-wide instructions for
  actual AI agents. Its name need not change to perform the HAI-role rename.
- Model classes light/standard/advanced and neutral hai-model-class,
  hai-reasoning-effort, hai-configuration-contract metadata do not need renaming.
- External .agents/ and .codex/ conventions and actual SKILL.md-based skills remain.
- Closed Activities, source transcripts, migration backups, accepted run snapshots,
  original hashes, completed backlog history and published release manifests remain
  original evidence. Compatibility readers interpret old versions; they do not
  rewrite those bytes or pretend historical roles had different names.

## Risks and safeguards

| Risk | Required safeguard |
| --- | --- |
| A global replacement changes the meaning of execution rules or chat actors | Classify references by meaning; preserve actual agent/executor language and authority boundaries. |
| Old settings appear missing and default to off or lose unknown data | Verify exact settings before/after migration, preserve unknown values, and never infer feature enablement. |
| A local package or installed modification disappears | Inventory all installed folders, not just source counterparts; preserve independent snapshots and local-only packages. |
| A validator accepts a renamed path but a consumer still uses the old one | Use shared path/identity handling and test startup, installation, model/config resolution, direct work and spawned role work together. |
| Two competing registries/settings roots exist | Preview and reject collisions/mixed partial state. Do not auto-merge, silently choose one or maintain two authoritative stores. |
| An interrupted migration leaves plausible new paths | Preserve a single auditable migration record, verify content and mark incomplete work so dependent mutations cannot continue until resolved. |
| Existing runs lose their meaning when definitions and role paths change | Preserve pinned snapshots, old parser support for inspection and actual evidence. Stop/reconcile affected writers before migration; never replay unknown effects or rewrite accepted evidence. |
| ROLE.md changes break package entry links or installers | Update the entry contract, catalogue, relative peers, authoring templates, pure validator and package install staging as one dependency set. |
| Migration evidence changes in Git checkout | Preserve exact retained bytes using the established attributes; check inclusion of renamed tracked files against ignore rules. |
| The core ZIP starts requiring optional roles | Verify clean initialization with no installed roles/profiles and install selected roles through core, without the library as a runtime fallback. |

Source-library prose also contains earlier owner names (Leader/Environment-manager)
that no longer describe the Python core. These are pre-existing documentation
issues, not evidence that the rename is done. Update affected explanations to actual
host/core ownership without restoring retired built-in owners or broadening scope.

## Proposed implementation order

1. Record the two human decisions and the exact naming/compatibility contract.
2. Implement canonical role paths, versioned data readers and explicit migration
   with collision, settings, custom-package and interruption safeguards.
3. Update definition validation/authoring, source and installed snapshots, catalogue,
   configuration and model-resolution consumers together.
4. Update workflow assignment and invocation metadata while preserving actual AI
   execution semantics and immutable historical inspection.
5. Update host instructions, startup/menu, CI paths and installation guidance.
6. Run maintained regression suites and independent review, then apply reviewed
   migration in this workspace and verify its complete before/after inventory.

## Acceptance evidence needed

All 11 installed roles remain registered and selectable; the workspace-only role
and the five installed/source differences remain attributable. Git/specification
settings and model-profile bytes retain their intended values. New names work from
fresh installs and the source library can be absent at execution. Migration preview
writes nothing; collisions and partial operations preserve content. Old closed
Activities and the accepted workflow pilot remain readable and byte-identical.
Both direct role execution and a separate real AI-agent handoff work with correct
role/worker identities. Full startup, Activity, configuration, parser, package,
recording and workflow regression suites pass, with platform skips stated.

The existing chronicle source-assignment/compatibility gap is separate from this
rename. It stays explicit under best-effort policy, not claimed repaired here.

## Status

No role/package/runtime source file has been changed during this audit. Human
compatibility and entry-file choices are pending. No commit, release, publication
or Activity closure is part of this review.
