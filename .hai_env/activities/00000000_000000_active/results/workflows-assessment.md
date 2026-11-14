# Should HAI add workflows?

Date: 2026-11-12. Activity: `1b440d51-819b-4299-862b-0182f0f4fca5`.
Status: research and recommendation; proposed design, not an accepted specification.
Author: host coordinator, direct research. No separate specialist or independent reviewer was invoked.

## Recommendation

Yes, conditionally: introduce optional reusable workflow definitions and Activity-local run records, coordinated by the host. Start with sequential execution and explicit handoffs. Do not initially build an autonomous orchestration service, general programming language, or requirement to use multiple agents.

The useful product promise is: **choose a repeatable process, understand what will happen, and resume with trustworthy evidence of what has already happened.** Merely telling several agents to work in order is already possible in HAI; packaging that instruction alone is a modest convenience, not a major new execution capability.

Validate demand with two recurring processes before adopting a durable public format. If normal procedures plus an Activity plan solve them with comparable reliability and effort, defer a new first-class entity.

## Research scope and limits

Exa returned 27 search results across three angles: agent orchestration frameworks, developer-facing workflow tools, and engineering guidance on simplicity/recovery. Results were filtered for official documentation and original engineering guidance; selected pages were fetched for detail. The count is search results, includes duplicates, and does not mean 27 independent products or full-page reviews.

Repository inspection covered startup, Activity/procedure concepts and conventions, agent delegation and ownership rules, runtime command documentation, host capability implementation and command routing. This is a targeted architectural assessment, not a complete repository audit. Product documentation establishes documented behavior, not benchmarked reliability. No competitors were executed and no speed, cost, or quality advantage was measured.

## What comparable systems actually provide

| System | Documented realization | Lesson for HAI | Limit of the analogy |
| --- | --- | --- | --- |
| Windsurf/Cascade | Markdown step sequences stored with the workspace and invoked by slash command; workflows may reference other workflows. | Low-friction authoring, discoverability and sharing can be valuable before building a runtime. | The cited page describes guidance through steps; it does not establish durable, transactional dependency enforcement. |
| Claude Code dynamic workflows | JavaScript scripts hold orchestration, branching and intermediate results; a host runtime coordinates many subagents and exposes progress controls. | Repeatability of orchestration is different from repeatability of role instructions. | Its background execution and session resumption depend on a host feature HAI cannot assume exists everywhere. |
| CrewAI Flows | Python methods use start/listen/router decorators; structured state and optional persistence connect tasks and crews. | Separate process coordination from specialist teamwork and make handoff state explicit. | A Python application runtime is a larger commitment than portable HAI instruction packages; persisting state alone does not prove safe replay of external writes. |
| LangGraph | Graph state, nodes, edges, conditional routing, checkpoints and interrupts. | Dependencies, state transitions and pauses need defined semantics; interrupted nodes can re-execute. | General graph machinery and state merging create responsibilities HAI may not yet need. |
| GitHub Agentic Workflows | Markdown plus frontmatter is compiled to Actions workflows; controlled downstream jobs execute declared safe outputs. | Separate an agent's proposed action from the authority and mechanism that executes it. | GitHub supplies runners, credentials, isolation and triggers; a local HAI convention does not provide those controls. |
| Temporal | A durable execution platform coordinates work and recovery; retryable operations require attention to idempotency. | Design recovery around the interval between an external effect and recording its result. | Infrastructure for distributed durable execution would be excessive for HAI's initial single-workspace scope. Temporal's “Activity” is not HAI's Activity concept. |

Sources: [Windsurf workflows](https://docs.devin.ai/windsurf/plugins/cascade/workflows), [Claude Code workflows](https://code.claude.com/docs/en/workflows), [CrewAI Flows](https://docs.crewai.com/en/concepts/flows), [LangGraph graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [GitHub overview](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-github-agentic-workflows), [GitHub safe outputs](https://github.github.com/gh-aw/reference/safe-outputs/), [Temporal operation definitions](https://docs.temporal.io/activity-definition).

These examples show that the concept is established, but the shared label covers substantially different products. Their existence supports considering the capability; it does not prove HAI users need a full orchestration engine.

## Assessment from the four requested perspectives

### User experience

**Potential benefit:** users can request an outcome such as “assess this change for release” without choosing every role and remembering each handoff. A preview can expose inputs, agents, writes, missing prerequisites and completion criteria. Status can explain why the next step is waiting.

**Main risk:** a workflow becomes a rigid ceremony. Requiring analyst, architect, developer and QA for every small change can increase latency and token consumption without improving results. Exploratory work should remain conversational; routine work should remain executable by one capable host when the role contracts allow it.

Recommendation: optional selection, ordinary-language entry, meaningful defaults, and an explicit way to revise the instantiated plan. Do not require users to edit YAML or repeat permission already granted. Ask for a decision only when authority or a necessary input is missing, or a chosen process explicitly requires a review gate.

### HAI integrity

**Potential benefit:** explicit coordination would turn some host memory into inspectable contracts and evidence.

**Main risk:** introducing another authority for lifecycle, permission, role behavior or completion. Current HAI already owns those concerns in distinct places:

- Agent definitions own role responsibilities; procedures own role-local execution and input/output contracts.
- The host owns coordination and chooses direct execution or actual delegation.
- Core runtime owns Activity lifecycle, managed records, allocations and recording.
- Activity chat communicates findings; it is not evidence that a step was accepted or executed.

The procedure concept already calls a procedure an agent-owned workflow. A new concept therefore needs a precise boundary: a workflow composes calls and handoffs; a procedure describes work inside a role. Avoid copying procedure bodies into workflow files.

Preserve the existing single active Activity and its independent lifecycle/phase metadata. A workflow run can finish while its Activity stays open. Its fine-grained steps should not be stuffed into the Activity's fixed clarification/analysis/planning/implementation/verification fields. Mapping those fields requires actual work evidence, not automatic equivalence.

Repository evidence: [procedure concept](../../../../.hai/concepts/procedure.md), [agent convention](../../../../.hai/conventions/agent_conv.md), [Activity convention](../../../../.hai/conventions/activity_conv.md), [runtime documentation](../../../../.hai/tools/runtime/README.md), [host implementation](../../../../.hai/tools/runtime/host.py).

### Future scalability

Distinguish reuse across teams from execution at scale. HAI can support versioned reusable definitions without immediately supporting hundreds of workers.

Its present contracts support one current Activity. Its host helper checks caller-supplied capability evidence and explicitly does not integrate invocation. Consequently, an initial workflow should expose the next eligible assignment to the host; claiming unattended execution or scheduling would exceed current capability.

Preserve an adapter boundary for future host integrations. Introduce parallelism only when ownership, join behavior, cancellation and concurrent writes have credible enforcement. Logical independence in a graph does not imply that two agents can safely edit the same repository.

Multi-Activity execution, remote workers, timers, schedules and long-lived background runs should be separate architectural decisions. If durable service execution becomes necessary, evaluate an existing engine against a concrete workload before recreating its infrastructure.

### Maintainability

**Potential benefit:** one reusable process replaces repeated handoff instructions across conversations.

**Main risk:** workflow definitions drift from role procedures, model capabilities and configurations. A large custom language adds validation, tooling, compatibility and debugging work.

Use one small canonical definition format with a schema version and stable step IDs. Reference stable procedure identifiers rather than relying only on descriptions or physical file paths; HAI would need to introduce or formalize those identifiers. Validate references and declared input/output bindings. Keep explanatory text readable, and keep consequential dependency logic machine-checkable.

Pin a run's definition snapshot and relevant role/procedure revisions or hashes. On resume, detect changed inputs, output artifacts and contracts. Either continue against compatible pinned resources or require an explicit migration decision. Hashes establish identity, not semantic correctness or compatibility.

## Proposed minimum architecture

This is a design direction to test, not a finalized schema or existing command set.

1. **Definition:** reusable process with purpose, owner, version, inputs, outputs and ordered steps. Each step identifies a registered role/procedure, explicit argument bindings, prerequisites and observable acceptance evidence. The same role can perform several steps.
2. **Run:** one execution of a pinned definition within an existing Activity, with a stable run ID, step attempts, evidence references and recorded transitions. Initially permit one executing workflow run in the current Activity; ordinary ad hoc work remains possible.
3. **Coordinator:** the host validates readiness and dispatches the next eligible step using existing role contracts, capability checks, invocation allocation and recording requirements. Sequential steps may run directly; required independence still requires a separate executor.
4. **Runtime support:** a small core validates definitions and transitions and persists run records through controlled operations. It does not become another specialist or bypass the host's actual tools.

For an early manually coordinated pilot, an Activity plan can hold the run checklist without new runtime semantics. If that pilot proves the need for enforced progress, add runtime-managed records. Do not advertise a checklist as an execution guarantee.

Proposed storage ownership: reusable workspace definitions in a separately approved workflow location; execution snapshots, attempts and evidence below the owning Activity. Keep canonical run state in a designated runtime-owned Activity extension. The paths and schema should be approved as part of design rather than created as scaffolding during this research.

### Small initial feature set

- Manual start, preview and readiness check; sequence of role/procedure calls; explicit handoffs.
- Inspectable step state, stop/pause/resume, and failure reasons. For example: pending, ready, running, waiting, succeeded, failed, skipped and cancelled, with stale evidence represented explicitly.
- Clear distinction between missing information, denied authority, unavailable capability and failed work.
- Verified output acceptance before a dependent step becomes eligible. Completion claims from a worker are inputs to validation, not automatic proof.
- Safe recovery with retained attempts; no automatic retry of uncertain external writes.

Defer arbitrary scripting, general expression evaluation, nested workflows, dynamic agent spawning rules, event triggers, cycles, rollback promises and parallel writers. Add simple conditional branches and dependency graphs only after pilots demonstrate the need and define skipped-path/join behavior. Bounded rework can initially be an explicit new attempt that marks affected downstream evidence stale rather than an implicit endless loop.

## Failure semantics are the hard part

| Situation | Required behavior in a credible implementation |
| --- | --- |
| A predecessor fails or has missing evidence | Keep dependent work blocked; independent work may continue only if its dependencies and authority permit it. |
| An optional step is skipped | State which path was selected; a skipped producer cannot satisfy an input required by its consumer. |
| Two workers could edit the same resource | Serialize or isolate and integrate explicitly; a dependency graph is not a write lock. |
| A tool changes an external system, then the host crashes | Reconcile the external result before retrying; use a stable idempotency key where the external service supports it. |
| A worker disappears after launch | Preserve the attempt and handle; unknown liveness is not success or proof that it stopped writing. |
| Inputs or implementation change after review | Retain prior evidence and mark affected downstream results stale; rerun the necessary checks. |
| A user stops a run | Stop scheduling new work, request cancellation where supported, and verify remaining writers; stopping does not undo completed effects. |
| A definition or installed procedure changes mid-run | Detect the change and resolve compatibility explicitly rather than silently using a new process. |

LangGraph documents that interrupted nodes restart from their beginning; Temporal documents the crash window in which an operation may have completed but its completion was not recorded. Both make safe repeated execution a design concern. A checkpoint is not a guarantee that an external action happened exactly once. [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [Temporal idempotency](https://docs.temporal.io/activity-definition).

## Example worth piloting

An implementation workflow could connect:

```text
Clarify scope -> Design -> Implement + developer checks
                              -> Independent verification -> Synthesis
```

The arrows mean accepted outputs are supplied to named inputs. They do not require five different live agents or force every small task through all five stages. A verification failure returns specific findings for a bounded repair attempt; repaired output invalidates the affected verification evidence. Publication remains a separate action governed by actual authority.

For the first experiments, prefer a read-only change assessment and a release-readiness assessment. Both have observable handoffs and can measure coordination value without starting with external publication. Do not make unattended deployment the demonstration case.

## How to decide whether to proceed

Run representative tasks both with normal host coordination and with a manually followed workflow draft. Use the same acceptance criteria, and record differences rather than assuming more agents means better work.

Measure missed handoffs, user interventions, recovery after interruption, total latency, observed token usage, duplicated work and final acceptance quality. Test at least: missing required input, unavailable role, failed check, interruption after a side effect, changed definition, skipped producer, cancelled worker and stale review after repair.

Advance to runtime enforcement only if the pilots reduce coordination errors or user effort enough to justify maintenance and runtime overhead. If they merely restate an Activity plan, retain them as lightweight reusable instructions. If long-lived distributed execution is the actual demand, reconsider the single-Activity/host model explicitly and evaluate external orchestration infrastructure.

This cautious approach agrees with Anthropic's guidance to start with simple patterns and justify additional coordination through evaluation. CrewAI's recommendation to start production applications with a Flow reflects its own application-runtime setting; it is not a universal rule for an instruction-oriented framework. [Anthropic engineering guidance](https://www.anthropic.com/research/building-effective-agents), [CrewAI production architecture](https://docs.crewai.com/v1.15.32/en/concepts/production-architecture).

## Proposed next decision

Agree whether HAI's first workflow promise is reusable guidance or validated, resumable coordination. I recommend the latter as the eventual differentiator, tested first through a lightweight pilot. Preserve an optional route for simple guidance and ordinary ad hoc work. No framework implementation or public contract change was performed in this Activity.
