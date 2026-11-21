# Migrate role methods to reusable capabilities

## Description

Explicitly flatten the former hai_roles_library/roles source collection and extract reusable methods into skills, while independently preserving installed role customizations and settings. This is an authorized migration after design and compatibility review, never a startup effect. Legacy agent naming uses [roles migrate](migrate-roles.md) first; its historical marker remains unchanged.

## Inputs

- Actual authority to migrate the affected workspace packages; without it perform diagnosis and pure preview only.
- The current Activity ID, reviewed source/installed before inventory and independently prepared candidate workspace under its allocated work area.
- Canonical package destination list, exact preview hash, provenance and an observed ended-writer declaration scoped to the affected packages.

## Prerequisites

Valid compatible core state, readable fixed instructions, the sole current Activity, no unfinished workflow runs or unresolved workflow writers, safe contained candidates and no retained capability migration marker. Inspect unknown customizations before preparing replacements. Source and installed differences require separate candidates; do not overwrite local variants from the source collection.

## Rules

- The host MUST preserve exact source and installed originals before mutation, selected settings once at their owner, existing skills, model profiles, fixed instructions and all historical records.
- The host MUST review the complete capability inventory and all candidate dependencies before apply.
- The host MUST stop affected writes on unsafe paths, stale snapshots, conflicting destinations or partial effects; the host MUST NOT merge or retry partial state automatically.

## Steps

1. Inventory every existing role capability and file. Assign reusable methods/resources to coherent skills and retain responsibility, conduct, decision limits and handoffs in roles. Keep actual settings-owner contracts with their role and omit unnecessary empty contracts. Preserve native existing skills unchanged. Adapt links/imports for the explicitly supplied source and installed contexts.
2. Prepare a complete independent candidate workspace in the current Activity allocated work area. Source role/skill targets are roles/<name> and skills/<name>; installed targets are .hai_env/roles/<name> and .hai_env/skills/<name>. Validate source and installed dependencies separately; the installed resolver must never use source fallback. Keep working inventory/evidence in the Activity, rather than reusable packages.
3. Preview `skills migrate` without --apply. Its JSON request contains `activity_id`, `candidate_workspace`, a distinct `packages` list of the exact package target paths, optional Boolean `retire_legacy_source`, `writers_ended: true`, and actual `provenance` source/reason. Candidate_workspace must be under the current Activity work area. Targets are restricted to canonical immediate packages in the four allowed roots; aliases, traversal, unsafe parents and unfinished workflow executions block preview. With retire_legacy_source every legacy role needs an explicit flat candidate.
4. Review the returned plan and `preview_sha256`. It binds full candidate and destination manifests, chosen role settings and workflow-state dependencies. Review source/installed variants independently; installation does not grant authority or start work.
5. Reconcile other writers of the affected packages. Apply the same request with `expected_preview` equal to the reviewed hash and --apply. Runtime stages exact candidates beside the allocated candidate workspace, rechecks the preview, records its own versioned marker, moves originals without replacement into `<activity>/history/capability-migration-v1/originals/`, verifies backup identity, then publishes validated packages. It rechecks each destination and stage before its move and all published manifests and chosen settings before completion. Retiring the old source container retains it intact in that history location. No generic automatic extraction or merge is performed.
6. Inspect actual status, changed_files, `.hai_env/config/capability-migration-v1.json` and preserved originals. `complete` means this explicit migration finished; further ordinary updates use package installation. The marker does not alter historical role-migration.json. Verify flat source depth, all links/imports, role/skill resolution, selected settings/profiles/instructions and existing native-skill bytes. Record actual task reuse directly and through two roles with meaningful check outcomes, separately from structural availability.
7. On partial state stop affected writers, retain all candidates, partial destinations, marker and backups. The marker blocks dependent installed role/skill use. An owner must inspect each recorded mapping and exact hashes, preserve new/partial destinations separately, restore the original directory with explicit no-replace moves, and remove only reviewed newly-created targets. Restore the original legacy source container if retired. Never delete the marker merely to bypass the gate or rerun a partial migration; reconcile and authorize an explicit recovery plan first.

## Outputs

A reviewed complete migration has flat source roles, reusable native skills, independently preserved installed variants, unchanged existing skill/settings/history bytes and retained exact originals plus migration evidence. Partial operations retain their actual effects and recovery material and remain blocked pending explicit owner resolution. Activity closure and publication are separate authorized operations.

## References

- [Role convention](../conventions/role_conv.md) and [skill convention](../conventions/skill_conv.md).
- [Skill tools](../tools/skills/README.md), [workspace boundary](../conventions/workspace-boundary_conv.md) and [artifact placement](../conventions/artifact-placement_conv.md).

## Scope of the legacy conversion

This versioned migration preserves its historical conversion behavior. It is not a requirement to extract every role method into a skill. New authoring and separately authorized refactoring follow the current [ownership rules](../conventions/role-authoring_conv.md#ownership-and-extraction-checks); do not rerun a migration to impose a thin-role design.

## Deployment boundary

This historical conversion is not a normal installation prerequisite. Never
search for external source libraries. Default role naming migration handles only
internal legacy roots. Historical external naming conversion requires the caller
to select legacy_source: "hai_agents_library" explicitly. Capability retirement
requires legacy_source: "hai_roles_library" explicitly. Source package destinations
are explicit migration inputs, not required consumer layout. Preserve old markers
and backup mappings without reinterpreting historical results. Current ordinary
authoring uses installed definitions or caller-selected sources; a new workspace
requires no source collection.
