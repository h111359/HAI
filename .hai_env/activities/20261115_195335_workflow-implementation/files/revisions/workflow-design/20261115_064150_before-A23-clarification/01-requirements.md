# Workflow requirements and acceptance - draft 0.5

## User requirements

The following requirements summarize the user's statements and accepted decisions.
They are attributed summaries, not verbatim quotations. Each requirement identifies
its subject and the action or capability that the subject must provide.

| ID | Requirement | Design coverage |
| --- | --- | --- |
| U1 | HAI must support workflows that represent company processes and coordinate assigned agent roles in a defined order. | The host coordinator assigns roles and follows explicit transitions. |
| U2 | HAI must store each workflow definition as one Markdown file in `.hai_env/workflows/`. | The definition filename identifies the workflow, and the file contains the complete definition. |
| U3 | Each workflow definition must follow a documented file template that specifies the required YAML metadata, Markdown sections, tables and their order. | The workflow format specification defines the template that authors follow and validators check. |
| U4 | Each workflow must have exactly one entry step. | The definition's required `entry` field identifies one existing step as the start of the workflow. |
| U5 | Each workflow step must identify its assigned agent, instruct that agent what to do and state the expected result of the work. | The step's Agent, Instruction, Inputs, Outputs and Results sections describe the assignment and its expectations. |
| U6 | Each workflow step must declare its required inputs and expected outputs, including their names, naming rules and locations. | Explicit artifact references identify the inputs and the output paths for each attempt. |
| U7 | A workflow author must be able to define any number of named step results and the business conditions that distinguish those results. | The definition declares its own result names, selection criteria and transitions; the runtime does not impose a fixed vocabulary of business results. |
| U8 | Each declared step result must specify its required evidence artifacts and their exact locations. | Every result identifies a nonempty set of required output artifacts, including failure and needs-input results. |
| U9 | The coordinator must verify that a step's required predecessor artifacts exist and satisfy their declared expectations before dispatching that step. | Explicit incoming references and edge checks identify the expected producer artifacts, while runtime and host checks verify their existence, integrity and meaning. |
| U10 | Each workflow execution must belong to exactly one Activity and must not transition to work in another Activity. | The run retains an immutable owning Activity ID, and the runtime rejects cross-Activity transitions. |
| U11 | HAI must allow one Activity to contain several workflow executions. | The runtime assigns a distinct UUID and storage namespace to each run. |
| U12 | HAI must store workflow metadata, status and produced artifacts in dedicated subfolders of `.hai_env/`, separate from general working files. | Definitions use `.hai_env/workflows/`, and the proposed run layout uses `.hai_env/workflow-runs/<activity-id>/<run-id>/`, independently of the Activity record store. |
| U13 | HAI must provide a workflow-definition-manager agent that can author, maintain, verify and validate workflow definitions. | The manager uses the validation tool to check the file format and references, then checks whether the instructions, assigned roles and expected results make sense without executing the workflow. |
| U15 | HAI must allow workflow authors to choose artifact formats without a framework format or extension whitelist. | The author defines each artifact's Format and Expectation, and the agent and coordinator assess the appropriate format checks. |
| U16 | HAI must include workflow-definition-manager in the golden agent library as well as its separately installed workspace copy. | The canonical library package supplies the reviewed workspace installation; runtime installation and registration remain separate operations. |
| U17 | Each completed step attempt must report exactly one declared final result, and the coordinator must verify that result's required artifacts before following its transition. | A result may require multiple artifacts, but one accepted result determines the next step or terminal outcome for that attempt. |
| U18 | A workflow author must be able to define a transition that returns work to an earlier step, and the coordinator must preserve the artifacts from previous attempts. | An explicit return creates a new attempt with its own output folder rather than overwriting an earlier attempt. |
| U19 | Each workflow definition must specify per-step and total-run attempt limits, and the coordinator must stop further dispatch when either applicable limit is reached. | The runtime retains the attempts and reports an attempt-limit block; the example's numeric values are illustrative rather than fixed framework limits. |
| U20 | The coordinator must allow several runs within one Activity but must permit only one run to execute at a time. | A prepared attempt reserves the Activity's workflow execution slot before an agent starts work. |

U14 and A19 have been removed from the product requirements and acceptance
scenarios because they described this Activity's design-review authorization,
not workflow functionality. The remaining identifiers retain their original
numbers so existing review references stay valid. HAI must not implement a new
core feature or permanent regression test for the removed items.

## Explanation of U3

U3 specifies the **layout inside the workflow Markdown file**, not the folder
structure in which HAI stores workflow runs. A common template tells an author
where to put information and tells a reader or validator where to find it.

For example, the proposed template places the workflow name and entry step in YAML
metadata, followed by Purpose, Inputs, Outcomes and Steps sections. Each step then
has Agent, Instruction, Inputs, Outputs and Results sections. The detailed
specification proposes the exact fields and table columns; the user can review
those details separately. U3 does not treat those unreviewed details as approved.

## First-version scope and remaining proposals

The host coordinator selects and executes workflows under the user's authority.
The proposed first version does not provide a daemon, scheduler, remote workers,
nested workflow calls, parallel branches, joins, cross-Activity runs or automatic
publication. HAI allows ordinary direct tasks to continue without a workflow.

The host can execute an assigned role directly or create a separate invocation
according to the existing agent policy. A role name alone does not require a spawn.
The host explicitly maps resolved workflow inputs to the selected role procedure's
inputs; the runtime does not inherit files merely because their names match.

The user accepted one final result per completed attempt, explicit returns to earlier
steps, and the proposal for per-step and total-run limits. The user's acceptance
covers those principles, not every detailed runtime rule or the example limit values.
The rest of the detailed specification remains subject to continued user review.

## Terms used in the acceptance scenarios

| Term | Meaning in this document |
| --- | --- |
| Coordinating AI | The main AI assistant that HAI calls the host coordinator. It assigns work to agents, checks their reported results and decides whether the defined next step can start. |
| Workflow-definition-manager | The proposed agent that authors and reviews workflow definitions. |
| Workflow-validation tool | Proposed Python code that checks the definition's required fields, step names, next-step references and input/output declarations. This tool is not another agent. |
| HAI core program | The framework's supporting Python code that stores execution records and applies the workflow rules. Earlier drafts called this the runtime. |
| Run | One execution of a workflow within an Activity. |
| Attempt | One execution of a particular step. Returning to that step creates another attempt. |
| Artifact | A file or folder that a step reads or produces. The workflow author specifies its format, location and expected contents. |
| Result | A declared completion name, such as designed or needs-clarification, that determines the next step or how the workflow finishes. |
| Result condition | The workflow author's written description of when an agent may report a particular result. The proposed Results table places this description in the When column. |
| Output expectation | The workflow author's written description of what an output must contain or demonstrate. The proposed Outputs table places this description in the Expectation column. |
| Accepting a result | The coordinating AI checks the reported result against its written condition and required outputs, then allows the workflow to follow that result's next-step instruction. |

The tool can check a definition without executing its steps. The coordinating AI
can invoke the tool directly, so the optional manager is not required for that
check. None of these proposed workflow capabilities has been implemented yet.

## Explanation of A6

A6 checks whether the output actually satisfies the workflow's written requirements,
not merely whether a file exists. For example, an architect could provide the
required design file while leaving out an agreed customer requirement. The file
exists, but the architect cannot report designed if the written result condition
requires the design to cover the agreed requirements.

The previous phrase "semantic criterion" meant these written result conditions
and output expectations; it did not identify an additional rule. The coordinator
must use the conditions and expectations in the workflow definition together with
applicable agent rules and agreed requirements, rather than inventing extra checks.
The [customer-request example](examples/customer-request.md#design) illustrates
these declarations in the architect's step. The [solution specification](02-solution-specification.md#5-graph-and-result-semantics)
explains the proposed result-selection behavior; its detailed rules remain under review.

## Acceptance scenarios

Each scenario describes a situation and the response that the proposed solution
must provide. Each expected response names the responsible agent, coordinating AI,
validation tool or HAI core program. These are future checks; this document does
not claim that HAI has executed them.

| ID | Scenario | Required observed result |
| --- | --- | --- |
| A1 | The workflow-definition-manager gives the workflow-validation tool a definition that follows the documented format and uses valid step references. | The tool checks the required fields, step names, next-step references and input/output declarations and reports that the definition passes those checks; the tool does not execute the workflow or claim that the agents are available. |
| A2 | A definition omits its entry step, repeats a step name or refers to an unknown field or step. | The workflow-validation tool rejects the definition, identifies the affected field or step and leaves the file unchanged. |
| A3 | A step can follow either of two results, but one result does not provide an input that the step requires. | The workflow-validation tool rejects the definition and identifies the result that does not provide the required input. |
| A4 | A workflow author defines three result names that HAI has not seen before. | The workflow-validation tool accepts those names when their declarations follow the format; the author does not need to change HAI's program code to introduce those result names. |
| A5 | An agent reports a failure result but does not provide one of the files or folders that this result requires. | The coordinating AI refuses to accept the reported result and does not follow its next-step instruction. |
| A6 | An agent provides all required files or folders, but their contents do not satisfy the reported result's written condition or output expectations. | The coordinating AI refuses to accept the reported result, records which written requirement was not satisfied and does not start the next step. |
| A7 | A required input file or folder is missing, changes after it was checked, is a filesystem shortcut instead of the declared artifact or lies outside its permitted location. | The coordinating AI does not start the affected step, preserves the existing records and explains the input problem without inventing a step result. |
| A8 | The architect returns questions to the business analyst, and the analyst performs the step again. | The HAI core program creates a new attempt folder and keeps the earlier attempt's outputs and records unchanged. |
| A9 | A run reaches the workflow's limit for attempts of one step or attempts across the whole run. | The coordinating AI does not start another attempt, and the HAI core program records which limit was reached. |
| A10 | The coordinating AI starts two separate runs of the same workflow. | The HAI core program gives each run its own identifier, saved definition, execution records and output folders so that neither run overwrites the other's files. |
| A11 | The coordinating AI requests a change to a run using another Activity's identifier or after the owning Activity has closed. | The HAI core program rejects the change and still permits inspection of the saved records without modifying them. |
| A12 | The coordinating AI stops unexpectedly before or after it accepts a step result. | When work resumes, the coordinating AI checks the saved records to determine whether the result was accepted and does not repeat product or external changes without checking what already happened. |
| A13 | The coordinating AI submits the same step-completion information more than once. | The HAI core program returns the earlier acceptance when the information is unchanged and rejects a submission that conflicts with the accepted result. |
| A14 | A workflow author edits the definition while an existing run is paused. | The HAI core program keeps that run's saved definition unchanged, and the coordinating AI checks whether changes to the assigned agents or their settings affect the resumed work. |
| A15 | The workflow-definition-manager is not installed, or a workflow definition contains an error. | HAI continues to support startup and unrelated agent work and explains which requested workflow operation cannot proceed and why. |
| A16 | The coordinating AI reaches the specification-update step while specification management is disabled. | The coordinating AI explains that the step cannot start and does not enable specification management without authorization. |
| A17 | The user requests cancellation while an assigned agent may still be writing files. | The coordinating AI stops assigning new steps, requests that agent to stop where possible and records cancellation as unfinished until the agent has stopped writing. |
| A18 | An agent reports product changes outside the work that the user authorized. | The coordinating AI refuses to accept the result, preserves the record of the changes and asks how to resolve them without claiming that the changes have been undone. |
| A20 | One run finishes while another run in the same Activity remains paused. | The HAI core program records the finished run's result and keeps the Activity open; a later closure request still requires the paused run to be resolved. |
| A21 | The coordinating AI prepares a second run after the first run has reserved a step attempt but before its assigned agent starts. | The HAI core program refuses to prepare the second run because the first run already holds the Activity's single workflow execution slot. |
| A22 | The coordinating AI resumes a paused step whose agent started work but stopped before its result was accepted. | The coordinating AI checks what the agent changed and resolves any unfinished changes before explicitly starting another attempt; it does not automatically repeat the old work. |
| A23 | The coordinating AI repeats an accepted completion request whose saved execution-record version number is now older than the current version. | The HAI core program returns the original acceptance when the result, assessment and required outputs are unchanged; it rejects conflicting information instead of accepting it as a new completion. |
| A24 | A workflow author declares an XLSX file, PNG image, JSON array, empty file or folder as an output. | The HAI core program does not reject the output solely because of its format or extension, and the coordinating AI checks whether it meets the author's written expectations and file-location rules. |
| A25 | The user requests archival of an Activity whose run records are stored in the dedicated environment folder. | The HAI core program keeps the run folders at their existing locations, prevents further changes through the closed Activity and includes those folders if the user later requests an export of that Activity. |
| A26 | The coordinating AI installs the reviewed workflow-definition-manager package from the golden library. | The coordinating AI verifies the installed copy and its registration, preserves existing settings and uses the installed copy rather than treating the library source as an executable agent. |

## Success measures and limits

The user and coordinating AI should compare trial workflow use with ordinary host
coordination by measuring missed handoffs, requests for user intervention, effort
to resume interrupted work, elapsed time, observed token usage and the quality of
the final results. This package claims no measured improvement. The validation
tool can check the definition's format and references, but the assigned agent and
coordinating AI must check whether the work satisfies the written requirements.
