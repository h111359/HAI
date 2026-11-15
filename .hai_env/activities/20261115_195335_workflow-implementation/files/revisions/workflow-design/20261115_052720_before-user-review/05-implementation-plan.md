# Implementation and verification plan — draft 0.1

This is a proposed plan, not implementation authorization. The design package is
the only deliverable authorized in this phase.

## Proposed maintained changes

| Resource | Responsibility and reason |
| --- | --- |
| `.hai/concepts/workflow.md` | Explain definition, run, step, attempt, result and relation to Activity/agent/procedure. |
| `.hai/conventions/workflow_conv.md` | Canonical single-file grammar, file bindings, evidence and transitions. |
| `.hai/conventions/workflow-run_conv.md` | Run records, events, revisions, writer checks, lineage and recovery semantics. |
| `.hai/tools/workflows/definition.py` | Pure deterministic parser/validator, no source execution or writes. |
| `.hai/tools/workflows/README.md` | CLI/API, supported subset, dependencies, diagnostics and limits. |
| `.hai/tools/workflows/tests/test_definition.py` | Reusable synthetic grammar/graph/path fixtures and negative cases. |
| `.hai/tools/runtime/workflows.py` | Scoped operations for definition discovery, run allocation, assignment and transitions. |
| `.hai/tools/runtime/tests/test_workflow_runs.py` | Persistence, paths, transitions, recovery, limits and Activity ownership tests. |
| `.hai/tools/runtime/cli.py` | Add optional workflow command group. |
| `.hai/tools/runtime/activities.py` | Closure checks for unfinished runs/writers, including safe legacy absence handling. |
| `.hai/tools/runtime/README.md` | New commands and result shapes, preserving existing envelope conventions. |
| `.hai/tools/run_tests.py` | Register maintained workflow parser suite and keep fixtures Activity-local. |
| `.hai/procedures/execute-workflow.md` | Host coordination, capability checks, dispatch, semantic acceptance and recovery. |
| `.hai/procedures/present-startup-guide.md` and `.hai/start.md` | Optional workflow selection/discovery and explicit execution routing without blanket audits. |
| `.hai/conventions/activity_conv.md` and framework layout documentation | Optional run folder ownership and closure integration. |
| `.hai/templates/workflow.md` | A single useful authored template conforming to the exact grammar. |
| `.hai_env/agents/workflow-definition-manager/` | Proposed role/resources from manager design, authored and checked through existing agent-management contracts. |
| `.hai_env/workflows/` | Only explicitly selected example definitions, after implementation approval and semantic review. |
| `README.md` | User-facing selection and boundaries; no claims about unimplemented execution. |

This list is a change map, not permission to create unused scaffolds. Shared contracts
remain in core; per-task design, check output, reviews and scratch remain with their
Activity/invocation. Source library packaging, release versions and publication are
separate scopes. New manager authoring does not install a golden package or mutate
the catalogue directly; registration is an explicitly tracked runtime operation.

## Delivery stages

1. **Approve specification:** resolve the review choices, finish consistency review
   and identify approved version plus any exclusions. Preserve this draft when revised.
2. **Format and validator:** implement the standard-library parser and structural
   checks first. Use approved examples as fixtures, preserving user intent. No run
   execution until validation has meaningful negative tests.
3. **Manager:** author its workspace package, configuration contract and exact
   procedures. Validate structurally and semantically. Register through existing
   runtime only under implementation scope explicitly covering that step.
4. **Run records:** implement snapshots, identities, attempts, events, result
   acceptance, preview/apply, recovery and limits, using existing safe storage and
   cooperative locks rather than inventing another global current pointer.
5. **Host integration:** document dispatch, liveness, independent verification,
   input/output assessment and run selection. Keep direct tasks and core startup
   independent of optional manager availability.
6. **Verification and pilot:** independent review, developer tests, acceptance
   coverage and controlled observed host execution. Pilot a read-only assessment
   before authorizing a product-editing customer-request run.
7. **Delivery review:** compare actual changes against approved scope, explain
   unrun checks and limitations, review included artifacts. Commit/release/push and
   Activity closure only under their actual authority.

No stage converts a later approval requirement into assumed approval. If implementation
discovers a material contract change, return a concrete revised design for review.

## Verification plan

| Area | Cases and required evidence |
| --- | --- |
| Parser | Both examples, CRLF/LF/Unicode, missing/duplicate keys/sections/rows, unknown fields/versions, embedded fake headings and unsupported table escapes. |
| Graph | Missing/duplicate entry, unknown/unreachable step/outcome, cycles with exit paths, cycles with no terminal path, arbitrary result labels, missing criteria or outputs. |
| File binding | Required input absent on one incoming edge, optional absent, mismatched formats, missing file, changed hash, two outputs aliasing one path, source file modified during acceptance. |
| Paths | Traversal, absolute/drive/UNC references, junctions/symlinks, case aliases, reserved files, cross-Activity references, canonical product ownership and configured Activity roots. |
| Run isolation | Multiple executions with same definition, attempt numbering, paused runs, no concurrent ownership, no implicit previous-result lookup across runs. |
| Acceptance | Unknown/multiple labels, missing output, valid syntax but failed semantic criteria, invalid host assessment, output correction before acceptance, immutable accepted results, identical and conflicting replay. |
| Recovery | Crash before allocation, after assignment, after product effect, after result write, during event append, after committed event/before state update; no automatic replay of external effects. |
| Rework | Clarification back-edge, exhausted limits, retained old attempts, changed input lineage, downstream checks repeated on the newly traversed path. |
| Dependencies | Missing role, unavailable model/effort/tool, disabled specification feature, unauthorized tree migration, no implicit setup or substitution. |
| Compatibility | Existing Activity without run folder, unsupported run version, changed definition pinned, role/config changes detected, archived inspection and unfinished-run closure gate. |
| Actual host handoff | Assigned executor gets readable inputs, correct Activity/run/attempt/invocation IDs and output area; actual returned handle and liveness recorded. Fixture success alone is insufficient. |
| Recording/usage | Existing best-effort/required policy honored; no invented source ranges, transcripts, zero costs or automatic background continuation. |

Trace checks to A1–A23 in requirements. Use Python 3.11+ and standard library unless
an approved design revision establishes a necessary dependency. All caches, temporary
fixtures and reports stay within the workspace under Activity-owned test-work.
Run relevant existing startup, Activity, recording and agent-definition regressions
after integration, reporting actual OS/Python and platform skips. Test other OSes
when available; Windows success alone does not prove Linux/macOS behavior.

## Risks and mitigations

| Risk | Mitigation and remaining limit |
| --- | --- |
| Too much runtime for a simple process | Keep serial control flow, finite scalar/table grammar, manual host dispatch and no expression language. Durable state still has real maintenance cost. |
| Manager and runtime interpret definitions differently | One core parser, shared canonical contract, same approved examples; semantic review clearly separate. |
| Every role adds latency without value | Workflows optional; role sequence chosen for the process, not enforced universally. Pilot measures value. |
| Process gets stuck on ambiguous criteria | Semantic review before selection; host blocks ambiguity rather than row-order guesses. |
| Interrupted edits repeat effects | Retain attempts, reconcile liveness/actual effects, no automatic external rollback or replay. |
| Documentation step cannot run in this workspace | Report current disabled specification setting as readiness dependency; no implicit enablement. |
| Old snapshots are treated as current proof | Pin provenance and input hashes; recheck product and role compatibility; preserve historical evidence without reusing stale acceptance. |
| Custom Activity store conflicts with `.hai_env/` requirement | Resolve the explicit storage choice during design approval. |

## Design-only delivery status

This package specifies proposed behavior and examples. It does not claim a working
validator, manager, command group or workflow engine exists. The prior recording
repair and its commits are independent completed work and are not workflow tests.
Implementation should begin only after the user approves a specific revised package.
