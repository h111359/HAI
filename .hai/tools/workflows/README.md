# Workflow definition validation

Requires Python 3.11+ and the standard library. This module parses versioned (2/3, historical 1)
single-file workflow definitions; it does not run instructions, invoke agents,
inspect product artifacts, evaluate result conditions or write execution records.

The runtime exposes these checks through `hai.py workflow validate` and uses the
same contract before starting a run. Pure structural validation does not require
the optional workflow authoring skill/role or prove role/configuration/tool readiness.

## Python API

With `.hai/tools` on the import path:

```python
from workflows.definition import DefinitionError, parse_definition, load_definition

contract = parse_definition(raw_bytes, source="chosen-file.md")
contract = load_definition(canonical_path)
```

`parse_definition` accepts UTF-8 bytes or Python text and returns a
JSON-serializable dictionary. It raises `DefinitionError`, a `ValueError` subclass,
with source, section, row or line context for invalid/unsupported content. Exact
original bytes determine `sha256`; LF and CRLF parse equivalently without changing
that fingerprint. BOM, malformed UTF-8 and NUL are rejected.

The result contains:

- The six metadata keys: `workflow_format`, `name`, `revision`, `entry`,
  `max_step_attempts`, `max_run_attempts`.
- `title`, `purpose`, and exact-byte `sha256`.
- `inputs`, a map from name to `name`, `location`, `format`, `expectation`.
- `outcomes`, a map from name to `name`, `meaning`.
- `steps`, a map from step ID to `id`, `role`, `instruction`, `inputs`, `outputs`,
  `results`. Step inputs contain `name`, `source`, Boolean `required`, `format`,
  `expectation`; outputs contain `name`, `location`, `format`, `expectation`;
  results contain `name`, `when`, a list `outputs`, and the literal `next` reference.

`load_definition` additionally checks a canonical, nonlinked, singly-linked regular
file, stable read and exact `<name>.md` filename identity. It does not authorize a
source path or restrict it to the workflow collection; callers establish the
workspace and selected definition scope before reading.

## Supported format and checks

Definitions use exactly six bare-scalar YAML frontmatter keys, one H1 title and
the specified ordered Markdown sections/tables. This deliberately supports a
documented subset rather than general YAML or arbitrary Markdown extensions.
Duplicate/unknown keys and sections, missing/empty contract cells, unknown format
versions, malformed identifiers, disguised structural headings, embedded literal
pipes and unsupported references are explicit errors. Instruction code fences may
contain ordinary code, but cannot imitate the definition's H1–H4 structure.

Validation checks one existing entry; valid transitions/outcomes; reachable steps
and outcomes; a possible route to termination from every step; used output names;
mandatory incoming data on every actual predecessor result; and matching authored
Format descriptions. Cycles and arbitrary result names are permitted. Positive
per-step and total-run limits are required. This does not predict which business
condition will occur or whether a process will terminate within its limits.

Artifact formats are author-defined. No extension, binary/text, directory or
content-shape whitelist is imposed. The parser checks portable literal relative
path syntax, explicit source prefixes, case-insensitive/ancestor output collisions,
and reserved attempt metadata names. It rejects protected metadata/configuration
as explicit workspace artifact inputs. The runtime separately resolves paths,
checks actual containment, owning Activity, aliases, files/directories, snapshots
and evidence stability. A valid contract is not proof that artifacts exist or meet
their written expectations.

## Configurable installation and execution

Format 3 adds Locations, configured filename patterns, result-specific accepted
sources and human result gates. `runtime/workflow_config.py` owns explicit
installation/settings and `runtime/workflow_lineage.py` validates accepted sources
and checkpoint-bound host attestations. Reusable source workflows/ stays separate
from installed .hai_env/workflows/ and config/workflows settings. See the shared
[format convention](../../conventions/workflow_conv.md),
[installation procedure](../../procedures/install-workflow.md) and runtime workflow
commands for exact request shapes. Structural parsing requires no role or skill.

## Checks

Run maintained fixtures through the workspace-contained runner:

```text
<absolute-python> -B .hai/tools/run_tests.py --workspace . --work-dir <Activity-owned-test-work> --suite workflows/tests
```

The runner's suite registration and runtime integration are maintained alongside
this module. When running `unittest` directly, set `TEMP`, `TMP`, `TMPDIR` and the
working directory to an Activity/invocation-owned folder inside the workspace,
and disable bytecode writes. Tests cover real contract behavior, not an implementation
mirror: branches, loops, missing data, formats, Unicode/line endings, protected paths,
unsafe aliases, file identity and readable diagnostics. Platform link-creation limits
are reported as skips. No network, actual agent invocation or external source reads
are needed.
