# Roles and skills: discussion starting point

Status: brainstorming. The human accepted a role as a job description with
responsibilities and limits, supported by reusable skills (answer: "1 + maybe
something else"). Additional role contents and ownership details remain proposals.
Implementation has not started.

## Intended outcome

Agree on the distinct purposes of roles and skills, decide whether both are
needed, assign ownership of procedures/conventions/scripts/settings, and only
then prepare any HAI change proposal. Preserve the company/employee model and
Activity/workflow boundaries already agreed unless the human changes them.

## Observed current state

HAI roles are complete packages with ROLE.md, responsibility/scope rules,
procedures, configuration contracts and optional scripts/concepts/conventions.
The core currently requires a configuration contract even for empty settings.
The actual crete-design-package skill has SKILL.md and two reference documents;
it has no configuration contract. Therefore not every existing skill duplicates
the current role structure, although both formats can contain detailed procedures
and supporting resources. Current HAI has not yet implemented role composition
from an explicitly managed skill collection.

The Agent Skills specification permits SKILL.md instructions, executable scripts,
references, assets and additional directories. File types do not provide a useful
semantic boundary between role and skill. Source consulted:
https://agentskills.io/specification

## Provisional distinction

- AI agent: the tool or running worker that executes an assignment.
- Role: the responsibility the executor accepts, its scope, handoff obligations
  and quality criteria, plus the relevant skills. Role constraints remain within
  actual user/host permissions; a definition grants no new authority.
- Skill: a reusable capability for a bounded task, including its method and any
  supporting procedures, scripts, templates or task-specific conventions.
- Workflow: the process ordering assignments and handoffs between roles.

A role may have role-specific instructions and resources. Shared operational
methods should live once in skills; project-wide rules should live in shared
conventions. Do not require identical folder trees or empty files at both levels.
A thin role should carry useful responsibility/constraints, rather than merely
repeat every skill description.

## Illustrative example

A business-analyst role could be responsible for understandable business
requirements, unresolved questions and a handoff to architecture. Its skills
could include interviewing stakeholders, writing acceptance scenarios and
creating a design package. An architect could use that same design-package
skill for a different responsibility and different outputs. A technical skill's
availability would not expand either role's authorized scope.

For Git, a skill could implement preparing a commit, with its scripts and method.
Role-specific boundaries could require returning repository results and respecting
separation from publication. Git enablement is a workspace/service setting whose
owner must be decided; copying the same switch into several skills would create
competing sources. No settings relocation has been approved.

## Ownership proposal for discussion

| Material | Suggested owner |
| --- | --- |
| Responsibility, scope, required handoffs | Role |
| Reusable task method and associated procedures | Skill |
| Script/template supporting a task | Skill |
| Task-specific output format | Skill, or a shared contract if used independently |
| Rules applying across the workspace | Shared project/framework convention |
| Role-specific conduct or acceptance expectations | Role |
| Role selection among its capabilities | Short role instructions where needed |
| Multi-role sequence and dependency handoffs | Workflow |
| Settings | The actual capability/service owner, stored once; optional when unnecessary |

## Alternatives and critical questions

Roles could be responsibility-bearing compositions, simple skill bundles, or
removed in favor of skills selected directly. A bundle offers convenience, but
if no enduring responsibilities or constraints remain, a separately validated
package/runtime layer may not justify its maintenance cost. Conversely, moving
every policy into skills can duplicate role responsibilities across capabilities.
Do not split every small internal procedure into an independent skill; its reuse
and discoverability must justify another package and dependency.

The first question sent to the human asks whether the role should primarily be
a responsibility/limits description with skills, a convenient skill bundle, or
whether to explore both. Follow-up design decisions include skill reuse across
roles, shared contracts/settings ownership, role-specific resources, explicit
selection/loading behavior and conflict handling. The responsibility-based starting point is accepted; detailed composition and
ownership choices remain open.

## Scope and recording

Only Activity discussion material is being created. No role, skill, workflow or
runtime definitions have been changed. Chronicle synchronization was attempted;
source assignments are missing and coverage is unverified under best-effort policy.
The human's original instruction is retained in system/chat.jsonl.

## Workflows in the proposed model

Status: comparison for discussion. Existing workflow storage/execution rules remain
in effect; role-to-skill composition and explicit skill selection in workflow steps
have not been implemented or approved.

A role answers who is responsible, a skill answers how to perform a reusable task,
and a workflow answers what must happen next, by whom, with which inputs/outputs,
and after which result. An AI agent executes the assignment. The Activity holds
the actual work and its records.

| Material | Proposed owner | Reason/example |
| --- | --- | --- |
| Responsibility, scope, perspective and role-wide obligations | Role | Analyst owns clear business intent and identifies unresolved decisions. |
| Skills available to perform that responsibility | Role references shared skills | Composition, not copies of every skill. |
| Reusable task method, internal procedure, supporting script/template | Skill | The method for writing acceptance scenarios can serve several roles. |
| Knowledge/convention specific to one role | Role, when genuinely role-specific | Cross-skill professional judgement or role-wide handoff obligations. |
| Task-specific format or general input/output contract | Skill, or shared contract | General requirements-document structure, independent of a particular run. |
| Concrete assignment and initial inputs | Workflow step | Clarify this request using the customer's supplied material. |
| Step order, dependencies and assigned role | Workflow | Clarification before design; design before implementation. |
| Concrete filenames, locations and required outputs per result | Workflow | This step must produce its declared requirements.md output for its successor. |
| Named results, selection conditions, next steps, business retries and attempt limits | Workflow | Clarified goes to architecture; questions-needed returns to clarification. |
| Internal task error handling | Skill | Diagnose an unreadable input; report supported result/evidence rather than inventing success. |
| Conventions used by multiple roles/skills/processes | Shared project/framework location | Common naming, requirement structure and workspace boundaries have one source. |
| Configuration | The responsible capability/service/role, once | Workflow supplies run inputs; it does not duplicate Git enablement or grant permissions. |
| Execution state, accepted results and produced files | Activity workflow run | These are instance records, not reusable skill or role contents. |
| Runtime orchestration/validation scripts and locks | HAI core | A workflow definition remains one Markdown file; it has no mandatory script package. |

The workflow instruction states the assignment and its acceptance expectations;
it should reference a reusable skill/procedure rather than copy its detailed method.
It still needs enough information for the recipient to know what to accomplish.
The same role may perform several steps. A role may also use a skill outside a
workflow when the task permits it. Several internal procedure steps do not by
themselves require a separately managed workflow.

An explicit required-skill reference in a step is a possible future feature, not
an existing workflow field. A process could require a particular method, or let
the assigned role select among its available skills. This choice remains open.

### Illustrative customer-request process

| Step assignment | Responsible role | Skill used (illustrative) | Output for this run |
| --- | --- | --- | --- |
| Clarify the request | Business analyst | Clarify requirements | requirements.md |
| Design an agreed solution | Solution architect | Create a design package | design.md |
| Implement the approved design | Software developer | Implement a change | Declared change evidence plus product edits in their canonical locations |
| Update durable documentation | Specification manager | Maintain specifications | Updated canonical documentation plus the declared update report |

The workflow determines role order, output contracts and paths for those handoffs.
Each role brings its responsibility and limits; each skill brings a method. Durable
product edits remain in their canonical project locations. Run-owned handoff files
and evidence are written under the run's step attempts. Skill/role folders do not
receive generated run results.

### Physical placement

- .hai_env/roles/<name>/ROLE.md: existing role entry; composition would change its contents.
- skills/<name>/SKILL.md: the repository's current skill location; final HAI skill installation, registration and library layout remain undecided.
- .hai_env/workflows/<name>.md: existing single-file reusable workflow definition.
- <activity>/workflow-runs/<run-id>/: existing run records, immutable input snapshots and step attempt outputs; no extra Activity-ID level.
- .hai/conventions/: shared HAI rules. Product/domain conventions stay in the project's established location.
- .hai/tools/: existing core runtime and validation machinery.

All runs remain within one Activity; several runs may exist, with only one executing
at a time, under the existing workflow design. A finished run does not close its
Activity. No implementation change is authorized by this comparison.
