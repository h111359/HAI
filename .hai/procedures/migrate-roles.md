# Migrate HAI agents to roles

## Description

Convert the former HAI agent packages into HAI role packages. An AI agent is the
executing tool or worker; a HAI role is the reusable instructions it follows.
This is an explicit migration after installing the new core, never a startup effect.

## Inputs

| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
| Workspace | Validated current workspace | Mandatory | Host/user | Resolve before access |
| Authority | Instruction permitting this migration | Mandatory | User | Diagnose and preview only |
| Provenance | Actual source and reason | Mandatory | Host/user instruction | Return dependency |
| Expected snapshot | Hash from the current preview | Mandatory for apply | Runtime preview | Preview again |
| Writers ended | Actual host observation that package, settings and definition writers have stopped | Mandatory for apply | Host | Stop and reconcile writers |

## Prerequisites

Python 3.11+, the new .hai/ core, safely readable fixed instructions, supported
core state (2 or 3), and a valid current Activity. Resolve unfinished
workflow runs before migration. Existing source and installed packages may differ;
the migration preserves and converts them independently.

## Rules

- The host MUST inspect the preview and stop relevant writers before apply.
- The migration MUST preserve custom packages, saved values, profile bytes, native AI-agent integrations, genuine skills and historical records.
- The host MUST retain partial effects and recovery copies; the host MUST NOT remove a marker or repeat apply to bypass an incomplete migration.

## Steps

1. Run startup and apply the fixed agent_instructions.md. Inspect role_context.
   Complete an older environment-location migration first if required. The role
   migration preserves the current Activity layout and uses its owned paths.
2. Preview `roles migrate` with a request containing provenance. Use
   `--request-stdin` to avoid loose request files. Preview writes nothing and
   returns moves plus expected_snapshot. Compare source and installed differences.
3. Stop relevant writers, resolve unfinished workflow runs, then apply the exact
   inspected snapshot using the same command with `--apply`. The request contains:

   ```json
   {
     "provenance": {"source": "actual user instruction", "reason": "use HAI roles"},
     "expected_snapshot": "the hash returned by the latest preview",
     "writers_ended": true
   }
   ```

   The runtime stages and validates converted packages before replacing live roots.
   It retains original roots under the current Activity history/role-migration/ (or the layout-1 files area).
   It records status, mappings and hashes in .hai_env/config/role-migration.json.
   The lock coordinates runtime writes; it does not stop external processes.
4. Inspect actual changed_files and the migration marker. This legacy naming migration uses .hai_env/roles/, .hai_env/config/roles/, the intermediate hai_roles_library/roles/ bridge and
   ROLE.md package entries. This historical migration produces the identity
   role-definition-manager; later explicit package renames may use
   hai-role-definition-manager. Migration records retain their original identities.
   Source/installed local differences remain independent. Settings values and
   model profiles retain their original bytes and meaning.
5. Run startup, `roles audit`, selected configuration reads and reusable workflow
   validation. Check retained historical runs with workflow show. With core
   state 2, run environment migrate-specification after role migration; ordinary
   core mutations resume after that separate schema conversion.

New role contracts use contract_format_version 3 and the role identity. Saved
config_format_version is unchanged. Reusable workflows become workflow_format 2,
use Role sections and increment revision. Existing pinned run definitions,
events and allocation manifests are not rewritten. New invocation manifests use
version 2 and role; historical version 1 keeps its agent field. Old live agents
commands, package roots and workflow definitions are not transition aliases.

Mixed roots, changed snapshots, unsafe paths or interrupted migration block affected
role work. Inspect the marker, backups and actual paths before any scoped recovery.
Startup and independent diagnosis do not overwrite or merge these situations.
There is no automatic rollback or recovery command.

## Outputs

| Output | Meaning | Completion criteria |
| --- | --- | --- |
| Migrated live definitions | Canonical roles, contracts and reusable workflows | Staged validation and final readback pass |
| Migration evidence | Marker and Activity-owned original roots | Mappings and hashes identify preserved originals and actual effects |
| Verification | Role readiness, package checks and historical readback | Actual results and any gaps are reported |

## References

- [Role convention](../conventions/role_conv.md): definitions and execution.
- [Role configuration](../conventions/role-configuration_conv.md): contracts and saved values.
- [Runtime commands](../tools/runtime/README.md): operation requests.

After internal naming migration, installed roles are usable without a source library. Capability/source conversion is a separate optional operation only for explicitly identified legacy source packages; it is never a prerequisite for a new consumer workspace.

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
