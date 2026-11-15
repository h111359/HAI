# Understanding the solution specification

Storage revision: the user now requires runs inside their owning Activity at
`<activity>/workflow-runs/<run-id>/`, without another Activity-ID level. Runs
move with the Activity on archival. Earlier drafts are preserved in the Activity
revision files; this storage decision supersedes their external-root proposal.

Reading companion, version 1 — 2026-11-15.
Based on [solution specification draft 0.3](02-solution-specification.md).

This guide explains the same design in the same section order. It does not add
requirements, approve choices or replace the detailed specification. The commands,
folders and examples describe proposed behavior; they have not been implemented.

Read one numbered section at a time. Each section explains the purpose, gives an
example and identifies the decisions that remain yours to review. Open the linked
technical section when you want its exact rules. You do not need to understand the
Python request fields to review the intended behavior.

The labels below have specific meanings:

- **Agreed:** you have accepted this principle in the conversation.
- **Proposed:** the specification recommends this behavior, but you have not yet
  accepted its detail. Reading this explanation does not count as acceptance.
- **Technical detail:** the mechanism used to provide the behavior. Any mechanism
  that changes what you can do is also identified as a proposed decision.

## Words used throughout this guide

| Word | Plain meaning |
| --- | --- |
| Workflow definition | The reusable Markdown file describing a company process. |
| Run | One execution of that process for a particular assignment. |
| Step | One task assigned to an agent role. |
| Attempt | One performance of a step. If the architect must try again, that is a new attempt. |
| Result | The name the agent reports when its attempt finishes, such as designed or needs-clarification. |
| Outcome | The name describing how the whole run finishes, such as delivered or needs-input. |
| Artifact | An input or output file or folder, in the format chosen by the workflow author. |
| Coordinator | The main AI assistant, called the host coordinator in HAI. |
| Core program | HAI's Python tools for checking definitions and storing execution records; not another agent. |
| Snapshot | An exact saved copy. The original can change later without changing this copy. |
| Hash | A calculated fingerprint of file contents, used to detect changes. A matching hash does not prove that the contents are correct. |

The distinction between the four main objects is:

```text
customer-request.md                 reusable process
    |
    +-- Run A                       one execution in an Activity
    |     +-- clarify step
    |     +-- design step
    |           +-- attempt 1        architect asks a question
    |           +-- attempt 2        architect supplies the design
    |
    +-- Run B                       another execution, with separate records
```

## 1. Who does what?

**Meaning.** The definition manager helps write and check the process. The
coordinator follows it, assigns work and checks reported results. Specialist agents
do their assigned work. The core program stores records and performs checks that
can be expressed as precise rules, such as whether a required file exists.

**Why.** The architect should design the solution without also owning the entire
process or deciding that its own work has passed independent verification.

**Example.** The architect writes a design and reports designed. The coordinator
checks the written result condition and output expectations, then asks the core
program to record the accepted result. The developer can then receive its task.

**Agreed:** the process coordinates agent roles, and the definition manager authors
and validates definitions. **Proposed:** the precise division of checks between
manager, coordinator and core program follows this design. Existing HAI policy still
decides when a role can run in the main conversation and when a separate agent is
needed; a step does not automatically mean another independent AI session.

[Technical section 1](02-solution-specification.md#1-ownership-and-concepts)

## 2. Where do the files go, and how are runs kept separate?

**Meaning.** Reusable definitions have one location. Each execution has a separate
location for its saved definition, progress and produced files.

```text
.hai_env/
  workflows/
    customer-request.md
  activities/                       configured Activity store
    <current-or-archived-activity>/
      workflow-runs/
        <run-id>/
          definition.md            saved definition for this execution
          state.json               current progress
          events.jsonl             history of recorded changes
          inputs/                  saved initial inputs
          attempts/
            design/
              attempt-0001/        first architect attempt and its files
              attempt-0002/        second architect attempt and its files
```

The angle-bracket names stand for actual unique identifiers, not literal folder
names. The short attempt numbers do not identify the run by themselves.

**Why.** Two requests can use the same process without overwriting each other's
design.md. A second attempt does not erase what happened in the first attempt.

**Agreed after the storage revision:** a dedicated workflow-runs folder inside each
Activity, separate space per run and fixed output locations per attempt. The run
UUID is directly below workflow-runs; the Activity ID is not another folder level.
Run folders move with their owner on archival, become read-only through its closed
lifecycle and are included in an Activity export. Stable Activity/run IDs resolve
their location after the move. The Activity store may be configured elsewhere.

The naming proposal also uses lowercase hyphen-separated logical names, such as
customer-request, with a 64-character limit. The format of output files remains
the workflow author's choice. These naming rules are distinct from format rules.

[Technical section 2](02-solution-specification.md#2-locations-and-identity)

## 3. What does the workflow Markdown file contain?

**Meaning.** One file describes the process and all of its steps. YAML metadata at
the beginning identifies the workflow and its starting step. Named sections and
tables contain the instructions and file expectations.

**Example.** A design step names solution-architect, tells it to design against the
supplied requirements, names the required input, declares solution-design.md as an
output, and explains which result should lead to the developer.

The whole file has Purpose, Inputs, Outcomes and Steps sections. Each step has Agent,
Instruction, Inputs, Outputs and Results sections. A result row answers:

| Question | Example answer |
| --- | --- |
| What result can this attempt report? | designed |
| When is that result justified? | The design covers the agreed requirements. |
| Which outputs must exist? | The declared design artifact. |
| What happens next? | Start the developer step. |

**Why.** Authors, readers and tools can find the same information in the same place.

**Agreed:** one Markdown file with YAML and exactly one entry step. **Still proposed:**
the precise fields, section order, table columns and restricted YAML syntax. In
particular, the draft supports only its six simple metadata fields; it rejects
comments, quoted values, nested YAML and extra fields. This is narrower than general
YAML and deserves an explicit review decision. The draft also limits table cells
to one line and does not allow extra structural headings in step instructions.

The example's limits of three attempts per step and twelve per run are examples,
not framework-wide fixed numbers.

[Technical section 3](02-solution-specification.md#3-exact-single-file-definition-format)
and [complete customer-request definition](examples/customer-request.md)

## 4. How does one agent receive another agent's output?

**Meaning.** The author names each required input and says where it comes from.
HAI does not guess based on a filename or automatically reuse a file from an old
attempt. The following prefixes are proposed shorthand inside the definition:

| Written reference | Plain meaning |
| --- | --- |
| activity:input.md | Read input.md from the owning Activity. |
| workspace:requests/change.md | Read this exact authorized path in the workspace. |
| workflow:request | Use the initial request copy saved when this run started. |
| incoming:requirements | Use requirements from the immediately preceding accepted result. |
| attempt:solution-design.md | Write solution-design.md inside this attempt's folder. |

**Example.** Architect attempt 2 must receive the revised requirements from analyst
attempt 2, not the earlier requirements merely because both files share a name.
On a clarification return, the questions handoff must include the full already
clarified requirements and answers, so the analyst does not lose earlier decisions.

**Why.** A file can exist yet belong to the wrong run, attempt or decision. Explicit
references keep each handoff attributable and prevent accidental reuse.

**Agreed:** named inputs/outputs, exact locations, checks before the next step, and
no artifact-format whitelist. **Proposed details to review:**

- HAI saves initial input copies. Changes to those original inputs require a new
  run; answers obtained during a clarification attempt can remain in the same run.
- Steps consume declared initial inputs or the immediately preceding result. They
  cannot silently fetch the last file produced by any earlier step.
- The producer and consumer must use the same written Format description in their
  declarations. Authors choose those descriptions, but the draft requires an exact
  match rather than automatically deciding that two differently named formats agree.
- Run output files document the work. Actual product code and maintained
  specifications stay in their established product locations. A run receipt lists
  those changes; it does not create a second product specification inside the run.

The author defines whether an artifact must be valid JSON, an image of a particular
size, a spreadsheet or something else. The assigned agent performs those checks,
and the coordinator examines the actual evidence. Core file-existence and hash
checks alone cannot establish that the author-required contents are correct.

[Technical section 4](02-solution-specification.md#4-file-contracts-and-bindings)

## 5. How does HAI decide what happens next?

**Meaning.** The agent reports one declared result. The coordinator checks the
written condition for that result and its required outputs. HAI follows the next
step written for that result only after those checks succeed.

| Architect's result | Required output | Next action |
| --- | --- | --- |
| designed | Solution design. | Continue to developer. |
| needs-clarification | Earlier requirements, answers and new questions. | Return to analyst. |
| declined | Explanation of why the request cannot proceed. | Finish with the declared declined outcome. |

**Why.** A reported success is insufficient if the required design file is missing
or does not cover the agreed requirements. The checks come from the definition,
applicable role rules and agreed scope, not new conditions invented by the coordinator.

**Agreed:** arbitrary result names, one final result per completed attempt, returns
to earlier steps, and attempt limits. A result can require several files.

**Proposed details:** if two result conditions both apply, the coordinator must
resolve that ambiguity rather than choose the first table row. If an agent crashes
before it can provide its declared failure evidence, HAI records an interruption
and stops the affected work; it does not invent a failure result and follow its path.
Waiting for a human answer is not automatically a completed failure.

The draft checks that every step has some possible route to an ending. That does
not guarantee that real agents will reach that ending within the attempt limits.

[Technical section 5](02-solution-specification.md#5-graph-and-result-semantics)

## 6. What happens when work waits, stops or resumes?

**Meaning.** HAI records what happened so the coordinator can distinguish work that
is ready to start, actually running, waiting, blocked, paused, cancelled or finished.
The proposed prepared status means HAI has reserved an attempt before the agent starts.
These progress labels are different from authored results such as designed.

**Why.** Without that distinction, a resumed conversation might repeat work that
already changed the product or assign two agents to the same execution slot.

**Example.** The developer changes a file, but the conversation stops before its
completion is recorded. On return, the coordinator must inspect the actual changes
and determine what remains. It must not assume the change failed and blindly apply it again.

**Agreed:** several runs per Activity, one executing run at a time, and per-step/
total-run attempt limits. **Important proposed consequences to review:**

- Reserving an attempt occupies the execution slot before launch. Waiting or blocked
  unfinished work also holds it. Another run can execute only after the first run
  is safely paused, cancelled or otherwise releases that unfinished work.
- Pausing and cancelling require the relevant agents to stop writing. A stop request
  alone is not proof that an agent has stopped. Cancellation does not undo its edits.
- Resuming previously started work that has no accepted result requires a check of
  its actual effects before a new attempt. Work known never to have started can
  resume from its prepared assignment.
- HAI can accept corrections to an attempt's output before accepting its result.
  Once accepted, that result stays unchanged; rework creates another attempt.
- Failed launches count toward attempt limits. Continuing a waiting attempt does
  not add an attempt. Reaching a limit blocks further assignment; the draft does
  not provide an in-place limit override for that run.

**Technical detail.** HAI keeps current status and a history of changes. A completed
history entry can restore an out-of-date status record after interruption. An
incomplete or contradictory history needs investigation; HAI does not erase it.

When the coordinator repeats a completion report that HAI already accepted, HAI
confirms the earlier result without recording it twice or assigning the next step
twice. This is the behavior discussed under A23. It does not guarantee that an
external tool can never perform an action twice; actual effects still need checking.

[Technical section 6](02-solution-specification.md#6-runattempt-states-serialization-and-recovery)

## 7. Which actions will the coordinator be able to request?

**Meaning.** The core program exposes named operations. The coordinator uses them
to inspect definitions, start runs and record actual work. The operations do not
themselves create an AI agent; the host uses its available execution tools for that.

| Proposed operation | Plain purpose |
| --- | --- |
| list / validate | Show definitions or check their format and references. |
| start / show | Create a run or inspect its progress. |
| prepare-step | Reserve one attempt and record its assignment. |
| record-execution | Record an agent's actual start, wait or interruption. |
| complete-step | Check and record a reported result and its next action. |
| pause / resume / cancel | Control the run under the stop/resume rules above. |
| retry-step | Allocate another attempt after earlier effects and writer status are resolved. |

**Why.** A small set of checked operations is more predictable than asking agents
to edit shared status files directly.

**Proposed behavior:** inspecting or previewing an operation changes no records;
applying it performs the stated change under existing authority. The coordinator
does not need your approval for every internal operation already covered by your
assignment. A missing necessary decision or permission remains a reason to ask you.

The exact command names, request fields and status-record counters are technical
details in the linked section. The validation tool can establish that a definition
is well formed without establishing that a required agent, tool or setting is available.

[Technical section 7](02-solution-specification.md#7-proposed-runtime-interfaces)

## 8. How does this fit existing HAI work?

**Meaning.** Workflows add a way to organize work; they do not replace Activities,
agent procedures, chat, recording or existing configuration owners.

**Example.** A workflow can finish delivered while its Activity stays open for
other related work. If you later ask to close the Activity while another run is
paused, the proposal requires resolving that unfinished run first.

**Agreed:** one Activity owns each run; one Activity can have several runs; file
presence registers a workflow without a catalogue; the manager belongs in the
golden library and has a separately installed workspace copy.

**Proposed details:** HAI remains usable without any workflows. Adding a definition
does not execute it. Editing a reusable definition affects new runs; an existing
run keeps its saved definition. Changed agent instructions, tools or settings must
be checked before paused work resumes. A golden manager update does not silently
replace the installed manager. Activity closure checks unfinished runs and agents.

The specification discusses several different numbers:

| Number | Meaning | Example |
| --- | --- | --- |
| Definition revision | The author's edition of one reusable process. | customer-request revision 2. |
| Status-record change counter | The number tracking updates to one run's saved status. | Counter 7 becomes 8 after a change. |
| File-format version | The layout that HAI's parser understands for a definition or record. | workflow_format 1. |

These numbers serve different purposes. None is the version of the product being
developed. This companion's version and the design draft numbers describe documents
only. An unsupported file format requires explicit compatibility work; HAI must not
silently rewrite it to look supported.

[Technical section 8](02-solution-specification.md#8-integration-authority-and-compatibility)

## 9. What does the workflow permit, and what does it not prove?

**Meaning.** A workflow organizes work within existing permission. Its instructions
cannot authorize an unrelated change simply by naming it as the next step.

**Example.** A deployment step written in a definition does not itself grant permission
to publish. A specification-update step cannot silently enable disabled specification
management. If a task needs credentials, agents use the existing protected tool setup
rather than copying secrets into workflow artifacts.

**Why.** A process definition describes an assignment; it is not a new source of
authority over the workspace, external services or other agents.

**Existing HAI boundaries, retained by the proposal:** artifact locations and writes
must stay within their authorized scope; failed or unrun checks cannot be presented
as successful; agents cannot invent user approval. **Technical limit:** files, hashes
and cooperative locks can detect many conflicts but do not isolate an agent from
every other program using the same account. A valid definition and complete records
are not proof that all business judgments or product changes are correct.

[Technical section 9](02-solution-specification.md#9-security-and-semantic-limits)

## How to use this companion in review

Choose one numbered section. Ask about its example or comment on the proposed
behavior. The coordinator will revise the linked specification only when a design
change is requested or a discrepancy needs correction; it will not treat a request
for explanation as approval of that section.

The decisions most likely to affect your use are the exact YAML/template restrictions
(3), saved initial inputs and immediate-predecessor handoffs (4), ambiguous-result and
interruption handling (5), and pause/retry/limit behavior (6). Those remain visible
proposals, rather than details you are presumed to have accepted by reading this guide.
