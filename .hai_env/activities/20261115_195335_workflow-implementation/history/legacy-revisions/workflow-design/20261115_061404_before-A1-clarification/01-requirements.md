# Workflow requirements and acceptance - draft 0.3

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
| U13 | HAI must provide a workflow-definition-manager agent that can author, maintain, verify and validate workflow definitions. | The manager uses core structural validation and performs semantic review without executing the target workflow. |
| U14 | The design author must present the complete solution for user review before implementation begins. | This package describes the proposal; the user's design decisions do not authorize runtime or installed-agent changes. |
| U15 | HAI must allow workflow authors to choose artifact formats without a framework format or extension whitelist. | The author defines each artifact's Format and Expectation, and the agent and coordinator assess the appropriate format checks. |
| U16 | HAI must include workflow-definition-manager in the golden agent library as well as its separately installed workspace copy. | The canonical library package supplies the reviewed workspace installation; runtime installation and registration remain separate operations. |
| U17 | Each completed step attempt must report exactly one declared final result, and the coordinator must verify that result's required artifacts before following its transition. | A result may require multiple artifacts, but one accepted result determines the next step or terminal outcome for that attempt. |
| U18 | A workflow author must be able to define a transition that returns work to an earlier step, and the coordinator must preserve the artifacts from previous attempts. | An explicit return creates a new attempt with its own output folder rather than overwriting an earlier attempt. |
| U19 | Each workflow definition must specify per-step and total-run attempt limits, and the coordinator must stop further dispatch when either applicable limit is reached. | The runtime retains the attempts and reports an attempt-limit block; the example's numeric values are illustrative rather than fixed framework limits. |
| U20 | The coordinator must allow several runs within one Activity but must permit only one run to execute at a time. | A prepared attempt reserves the Activity's workflow execution slot before an agent starts work. |

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

## Acceptance scenarios

Each scenario states an explicit trigger or actor. Each expected result identifies
the component responsible for the response. These scenarios describe future
verification; this document does not claim that HAI has executed them.

| ID | Scenario | Required observed result |
| --- | --- | --- |
| A1 | A reviewer submits either complete example to structural validation. | The validator accepts the example's structure, graph and bindings and reports execution readiness separately. |
| A2 | A definition contains a missing entry, duplicate step, unknown metadata key or unknown target. | The validator rejects the definition with a file, section or row diagnostic and makes no changes. |
| A3 | A target step requires an incoming output that one predecessor result does not provide. | The validator rejects that transition even if another predecessor result provides the output. |
| A4 | An author declares three custom result names. | The validator accepts all three names without requiring changes to the runtime's business-result vocabulary. |
| A5 | An agent reports a failure result but omits a required artifact or violates an authored expectation. | The coordinator rejects completion and does not follow the failure transition; the coordinator permits empty artifacts when the author explicitly allows them. |
| A6 | An agent supplies all required artifacts but fails a result's semantic criterion. | The coordinator declines acceptance, records its reason and does not dispatch the next step. |
| A7 | A required input artifact is missing, changed, linked or outside its permitted root. | The coordinator blocks dependent dispatch and preserves the existing state and evidence without inventing a step result. |
| A8 | The architect requests clarification, and the analyst performs another attempt. | The runtime creates a new attempt directory and preserves the previous result and consumed-input hashes. |
| A9 | A run reaches a per-step or total-run attempt limit. | The coordinator stops further dispatch, and the runtime records an attempt-limit block. |
| A10 | The coordinator starts two runs from the same definition. | The runtime assigns separate UUIDs, snapshots, states and artifact namespaces so the files do not collide. |
| A11 | A caller tries to mutate a run under another Activity ID or after its owner closes. | The runtime rejects the mutation and permits read-only inspection of the archived run. |
| A12 | The host crashes before or after accepting a result. | The recovery process distinguishes unaccepted work from accepted transitions and does not blindly repeat external effects. |
| A13 | A caller repeats a completion submission for an accepted attempt. | The runtime returns the retained acceptance for an identical submission and rejects a conflicting submission. |
| A14 | An author changes a definition while a run is paused. | The run keeps its pinned definition, and the coordinator checks role or configuration changes before resuming dependent work. |
| A15 | The optional manager is absent, or a workflow definition is invalid. | Core startup and unrelated agents remain usable, while the runtime reports the affected workflow dependency. |
| A16 | The coordinator reaches the documentation step while specification management is disabled. | The coordinator reports a readiness block and does not enable the feature implicitly. |
| A17 | The user requests cancellation while a worker may still be writing. | The coordinator stops new dispatch, requests worker termination where supported and retains cancellation-in-progress until the writer's termination is known. |
| A18 | An agent's evidence reports product modifications outside the agreed authority. | The coordinator rejects acceptance, preserves the partial-work evidence and requests resolution without claiming rollback. |
| A19 | The user approves the design package without authorizing implementation. | The host makes no runtime, installed-workflow, manager-registration or execution changes. |
| A20 | One run finishes successfully while another run is paused. | The runtime records the finished run's outcome, keeps the Activity active and preserves the unfinished-run closure check. |
| A21 | A caller prepares a second run after the first run has allocated an attempt but before its worker starts. | The runtime rejects the second preparation because the first prepared attempt already reserves execution ownership. |
| A22 | A caller resumes a paused attempt whose worker previously started but stopped before acceptance. | The coordinator requires effect reconciliation and explicit retry instead of blindly replaying work in the old attempt. |
| A23 | A caller replays an accepted completion with its original expected revision. | The runtime returns an identical retained acceptance before applying stale-revision rejection and rejects changed completion content. |
| A24 | An author declares an XLSX file, PNG image, JSON array, empty file or directory artifact. | The runtime does not reject the artifact solely for its format or extension, and the coordinator assesses it against the authored expectations and safe artifact checks. |
| A25 | The user requests archival of an Activity whose runs use the environment run store. | The runtime retains the runs at stable paths, makes them read-only through the owner's closed lifecycle and includes both stores in a later requested export. |
| A26 | The host installs the validated golden manager package. | The source remains non-executable data, and the host separately verifies the installed snapshot and registration while preserving settings. |

## Success measures and limits

The pilot reviewer should compare workflow use with normal host coordination by
measuring missed handoffs, user interventions, recovery effort, elapsed time,
observed token usage and acceptance quality. This package claims no measured
improvement. The validator can check structural consistency, but the agent and
coordinator must assess instruction sufficiency, scope and evidence meaning.
