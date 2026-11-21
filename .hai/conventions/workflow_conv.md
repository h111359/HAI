# Workflow definition convention

## Identity and structure

Reusable source definitions are explicitly selected UTF-8 Markdown files; installation puts a selected definition directly under
`.hai_env/workflows/<name>.md`. File presence establishes discovery/registration;
the host MUST validate before execution. No catalogue or recursive includes exist.
Names use lowercase letters/digits separated by single hyphens, start with a letter
and contain at most 64 characters. Names are unique in their own namespace;
case/alias collisions are invalid. Runtime-owned data MUST NOT be embedded in a definition.

The format-2 document starts with `---` frontmatter, one H1 title and these H2 sections in
order: Purpose, Inputs, Outcomes, Steps. Required metadata is exactly:

```yaml
workflow_format: 2
name: change-assessment
revision: 1
entry: assess
max_step_attempts: 2
max_run_attempts: 2
```

This format deliberately uses a scalar YAML subset: six unquoted key/value lines,
positive decimal integers for numeric fields, format 2 (or the versioned extensions below), name and entry
as canonical identifiers. Duplicate/unknown keys, comments, quoting, tags, nested
values and aliases are rejected. Definition revision is independent of core product
version, run-state format and the run's optimistic change counter.

Purpose is nonempty prose. Workflow Inputs is one table with columns Name, Location,
Format, Expectation. All declared initial inputs are required. Outcomes is one table
with columns Name, Meaning. Each H3 under Steps is its unique step ID. Each step
has exactly these H4 sections: Role, Instruction, Inputs, Outputs, Results.
Role contains one canonical role name. Instruction contains nonempty Markdown
without fake structural headings; it may reference relevant role-owned procedures.

| Section | Exact table columns |
| --- | --- |
| Step Inputs | Name, Source, Required, Format, Expectation |
| Step Outputs | Name, Location, Format, Expectation |
| Step Results | Name, When, Outputs, Next |

Table cells are nonempty single-line literal text, without embedded/escaped pipes.
Contract tokens do not use Markdown backticks or links. Required is yes or no.
Inputs may be header-only; Outputs and Results must be nonempty. Result Outputs
is a comma-separated nonempty set of output names declared by that step. Every
output must be used by some result. No implicit inheritance or row-order priority exists.

## Results and graph checks

The author MAY define any number of named results and outcomes. Each result states
its When condition, its required outputs and exactly one Next: `step:<step-id>` or
`end:<outcome-name>`. The workflow MUST have exactly one entry step. All referenced
steps/outcomes must exist and be reachable; each step must have some possible path
to an ending. Cycles and self-transitions are allowed within the declared limits.

The coordinator MUST check the selected result's actual outputs and written condition
before acceptance. Multiple applicable conditions require resolution, never an
invented priority. A failed process that cannot produce its declared failure outputs
is an interruption, not an accepted failure result. These checks do not guarantee
that every graph ending will occur or every business judgment will be correct.

## Explicit artifact references

| Reference | Meaning |
| --- | --- |
| workspace:path | Authorized initial file/directory inside the workspace. |
| activity:path | Initial artifact inside the owning Activity record. |
| workflow:name | Immutable initial input snapshot for this run. |
| incoming:name | Output from the immediately preceding accepted result in this run. |
| attempt:path | Declared output inside this step attempt's directory. |

Initial Locations use workspace/activity; step Sources use workflow/incoming;
output Locations use attempt. Required incoming values must exist in **every**
predecessor result that reaches the step; entry cannot require incoming data.
Producer and consumer Format descriptions must match. Local input names can differ
from producer names because Source establishes the binding explicitly.

There is no format/extension whitelist. Authors specify representation and meaningful
checks in Format, Expectation and Instruction. Binary files, directories, JSON arrays
and empty artifacts are permitted when the authored expectations allow them. Core
checks location, identity and content integrity; it MUST NOT claim to have established
business quality merely because a file exists or its fingerprint matches.

Paths use portable relative components and `/`. Reject absolute/drive paths, traversal,
unsafe names, links/junctions, hard-link aliases, escaping ancestors and special files.
Outputs cannot overlap each other or use assignment.json, result.json or rejection
record names reserved by runtime. New base names use lowercase hyphenated wording;
authors choose suffixes and formats. Referenced initial product material stays within
actual task authority; secrets, Git/config/profile metadata and another Activity's
managed records cannot be copied as ordinary workflow inputs.

At run start core snapshots initial artifacts exactly. At dispatch the assignment
freezes producer identities, locations and hashes. Agents MUST treat predecessor
artifacts as read-only. A changed input invalidates dependent acceptance. Product
code and maintained specifications keep their existing owners and locations; run
receipts identify actual changed paths/checks rather than becoming a second product.

## Configurable format 3

New portable definitions use workflow_format 3. The six metadata keys and role
assignment remain; ordered H2 sections are Purpose, Locations, Inputs, Outcomes,
Steps. Locations is a nonempty table with Name, Purpose, Contents. Names identify
required environment settings; Purpose/Contents explain the installation questions.
Every declared location must be used. Per-step Results adds Gate after Next, with
`none` or `human`. Other columns and arbitrary named result semantics remain.

Format-3 output Locations use `configured:<location>/<step>-{execution}-<filename>`.
The step prefix must equal the declaring step ID, the filename contains exactly
one execution token and no directory separator, and no other expression is allowed.
The runtime resolves `<human-chosen-base>/<run-uuid>/<step>-<number>-<filename>`;
number is the monotonic per-step execution counter padded to at least three digits.
Examples: clarify-001-requirements.md, design-001-solution-design.md and
clarify-002-requirements.md. Earlier attempts are retained. Final per-run receipts
use the same identity; canonical product names are declared in reports and retain
owner authority. No automatic stable-name publication is provided.

Step Sources additionally permit `accepted:<step>/<result>/<output>`. All three
names must exist, the result must declare that output and producer/consumer Format
must match. This binds the currently accepted execution of that named step/result,
never a similarly labeled file or a different result. Missing required bindings block.
On a partial QA return, declare current defects plus earlier requirements, design
and human approval explicitly. Superseded required sources invalidate downstream
lineage recursively. Use `feedback:<output>` for an exact immediate predecessor change request or QA
defect report. This explicitly historical edge retains and verifies the entire
provenance/content subtree while allowing superseded identities inside that subtree.
Declare continuing requirements/design/approval separately with live accepted
references; those reject superseded dependencies. No feedback record is rebound.

Installation uses separate `.hai_env/config/workflows/<name>.json` with format 1,
name, definition_sha256 and exact locations mapping. All destinations are canonical
workspace-relative bases. Identical shared bases are allowed when distinct step
filenames prevent collision; nested bases, case aliases, links, escaping/protected
metadata and source roots are rejected. Missing/unsafe settings block workflow start,
not ordinary core startup. Preview exposes every question; host asks the human and
apply requires actual choices. Reuse and compatible definition updates preserve
chosen values. Changed location contracts require reviewed explicit migration;
partial installations and historical conversion block without automatic repair.

Gate human requires a current checkpoint-bound host semantic attestation referencing
an actual received typed human instruction, its immutable ID/hash and the assignment
checkpoint digest. A natural response is sufficient in its presented context; the
host records it verbatim and assesses intent. Runtime requires a message after
checkpoint preparation; agent coordination and arbitrary approval evidence strings
cannot satisfy the gate. This verifies host-attributed records and does not provide
independent human authentication. Actual source-backed recording provenance, when
available, remains subject to its own validation contract. Material scope/design
changes invalidate stale approval; QA success alone is never human acceptance.

## Validation responsibilities

Core structural validation checks syntax, references, paths and graph/data contracts.
The host follows [core workflow authoring](../procedures/manage-workflow-definitions.md) to check instructions, role responsibilities, useful conditions
and sufficient handoffs. The host checks current authority, registration, configuration,
capability and actual input/output evidence. Structural validity MUST NOT be reported
as participant readiness, semantic acceptance or successful execution.

## References

- [Workflow concept](../concepts/workflow.md) — meaning and ownership.
- [Run convention](workflow-run_conv.md) — execution records and limits.
- [Workflow tools](../tools/workflows/README.md) — actual API, diagnostics and limits.
- [Artifact placement](artifact-placement_conv.md) and [workspace boundary](workspace-boundary_conv.md) — destinations and authority.

Workflow format 1 uses an Agent section and is read only for retained run records.
Reusable format-1 definitions require explicit role migration before validation
or a new run. Migration increments the definition revision and leaves pinned
historical definitions and event hashes unchanged.
