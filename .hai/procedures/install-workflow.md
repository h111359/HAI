# Install a workflow

## Description
Install a selected reusable workflow and preserve prior definitions and any
existing environment settings.

## Inputs
| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
| [input:definition] | Selected reusable format-3 or format-4 Markdown definition | Mandatory | Actual user scope or reviewed workflow | Resolve selection before installation. |
| [input:locations] | Human-chosen workspace-relative bases for format 3 | Mandatory for format-3 apply | Actual answers to preview questions | Present every purpose/contents question and wait. |

## Prerequisites
Valid core context and actual installation authority. Authoring a source is not
installation. No role, workflow execution, publication or Activity closure is implied.

## Rules
- **Actual choices.** The host MUST NOT invent live location values or describe fixture choices as human selections.
- **Preservation.** The host MUST stop on partial/incompatible installation and preserve material; no automatic repair or historical conversion.

## Steps
1. Validate the selected source with workflow validate. Review responsibilities,
   complete routes, accepted source bindings and human checkpoints separately.
   For format 4, preview and apply workflow install with definition and provenance.
   Supply the inspected expected_installed_sha256 for an update. File paths are
   resolved when a run starts. After applying, proceed to step 5.
2. Preview workflow install with definition only. Present each returned name,
   purpose and expected contents to the human; explain per-run isolation and
   per-step execution filenames. Obtain actual workspace-relative bases.
3. Preview again with locations. Resolve escaping, aliases, nested/protected paths,
   missing settings or output collisions. Identical shared bases are allowed when
   authored filenames remain distinct. Path meaning is always workspace-root-relative.
4. Apply with definition, locations and provenance. For a definition update supply
   expected_installed_sha256 from inspected existing bytes; omit locations to retain
   current chosen values. The runtime preserves predecessor definition/config bytes.
   Changed location contracts require separately reviewed migration.
5. Inspect the installed definition, any configuration and actual readiness. Installation
   starts no run. Execute-workflow handles an explicitly authorized later run.

## Outputs
| Output | Meaning | Completion criteria |
| --- | --- | --- |
| [output:installation] | Installed definition and separate environment settings or explicit blocked dependency | Actual chosen values saved, no run started; predecessors preserved on update. |

## References
- [Workflow convention](../conventions/workflow_conv.md) ? shared format/config contract.
- [Runtime commands](../tools/runtime/README.md) ? exact request and result fields.
- [Execute workflow](execute-workflow.md) ? later host coordination.
