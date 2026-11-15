# Workflow requirements and acceptance — draft 0.1

## User requirements

The following are attributed summaries of the conversation, not fabricated quotations.

| ID | Requirement | Design coverage |
| --- | --- | --- |
| U1 | Model company processes involving employee/agent roles in a defined order. | Host-coordinated role assignments and explicit transitions. |
| U2 | Store each workflow as one Markdown file in `.hai_env/workflows/`. | Filename identity and self-contained contract. |
| U3 | Use a predefined file structure. | Versioned frontmatter, headings and exact tables. |
| U4 | Have exactly one entry step. | Required `entry` points to a defined step. |
| U5 | Each step instructs an agent what to do and states expectations. | Agent section, instruction prose, named input/output contracts. |
| U6 | Define expected input/output names, naming rules and file locations. | Typed file references and per-attempt artifact paths. |
| U7 | Allow any number of named step results and arbitrary business conditions. | No fixed completion-result enum; each result has selection criteria and a transition. |
| U8 | Every result has clear evidence files at specified locations. | Nonempty required output set per result, including failure and needs-input results. |
| U9 | Next steps require the predecessor files they consume. | Explicit `incoming:<name>` references, edge validation and existence/hash/content checks. |
| U10 | Every workflow execution stays inside one Activity. | Immutable owning Activity ID; cross-Activity transitions rejected. |
| U11 | One Activity can contain several workflow executions. | Independent run UUIDs and attempt namespaces. |
| U12 | Keep workflow metadata/status under `.hai_env/`, analogous to agent files. | Definitions under `.hai_env/workflows/`; run records under the default `.hai_env/activities/` store. Custom-store interpretation is an explicit review decision. |
| U13 | Provide a workflow-definition-manager to author, maintain, verify and validate definitions. | Proposed role and procedures, using core validation without executing workflows. |
| U14 | Provide the entire design for review before implementation. | This package; no runtime or installed agent changes in this phase. |

## Proposed first-version boundaries

Manual selection and host-coordinated execution; no daemon, scheduler, remote workers,
nested workflow calls, fan-out, joins, cross-Activity runs or automatic publication.
Many definitions may exist; workflow use remains optional. Ordinary direct tasks
continue to work. A step may execute directly under the role or through a separate
invocation according to existing agent policy; a role name does not force a spawn.

There are no global input variables or implicit file inheritance. The new workflow
file-reference grammar is distinct from existing procedure `[input:name]` notation;
the host explicitly translates a step assignment into its selected role procedure.

## Acceptance scenarios

| ID | Scenario | Required observed result |
| --- | --- | --- |
| A1 | Validate either complete example. | Valid structure/graph/file bindings; readiness reported separately, not assumed. |
| A2 | Missing entry, duplicate step, unknown frontmatter key or unknown target. | Deterministic failure with file/section/row diagnostic; zero writes. |
| A3 | A target requires an incoming output absent on one predecessor result. | Reject that edge even if another branch would provide it. |
| A4 | A step declares three nonstandard results. | Accept all three without changing the validator or runtime result enum. |
| A5 | Failure result omits an output file or produces empty/invalid content. | Reject completion and remain blocked; do not take its failure transition. |
| A6 | Completed result includes all expected files but fails a semantic criterion. | Host declines acceptance with attributable reason; no next-step execution. |
| A7 | Input file is missing, changed, linked or escapes its allowed root. | Stop dependent dispatch; preserve state/evidence; no fabricated step result. |
| A8 | Architect requests clarification and analyst acts again. | New attempt directory; previous accepted result and consumed input hashes preserved. |
| A9 | Loop exhausts a limit. | No extra dispatch; run becomes blocked with reason `attempt-limit`. |
| A10 | Two runs use the same definition. | Separate UUIDs, snapshots, state and artifacts; no filename collisions. |
| A11 | Start a run in an active Activity, then try to mutate it under another ID or after closure. | Reject mutation. Archived runs remain readable. |
| A12 | Host crashes before or after acceptance. | Resume distinguishes unaccepted work from accepted transitions; no blind repeated external effect. |
| A13 | Repeat the same accepted completion request. | Return the same accepted result if identical; conflicting replay rejected. |
| A14 | Definition changes while a run is paused. | Run uses pinned definition bytes; role/config changes are rechecked and incompatible changes block. |
| A15 | Optional manager absent, invalid workflow present. | Core startup and unrelated agents remain usable; only dependent workflow operations fail. |
| A16 | Specification management is disabled. | Definition can validate; documentation step readiness blocks without silently enabling the feature. |
| A17 | Cancel while a worker might be writing. | Stop new scheduling, request stop where possible, retain cancellation-in-progress until writer termination is known. |
| A18 | Product evidence references modified files outside agreed authority. | Reject acceptance; retain partial-work evidence and request resolution, never claim rollback. |
| A19 | Approve this package only. | No installed workflow, manager registration or execution occurs. Implementation needs separate authorization. |
| A20 | Finish a run successfully while another is paused. | Record that run's outcome; Activity stays active; closure gate still sees unfinished work. |

## Success measures and limits

Evaluate a pilot against normal host coordination: missed handoffs, user interventions,
recovery effort, elapsed time, observed token usage and acceptance quality. No measured
improvement is asserted yet. Deterministic validation cannot prove business quality;
agent/host review is required for instruction sufficiency, scope and evidence meaning.
