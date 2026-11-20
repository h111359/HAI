# Verify and hand off

## Description

Verify the delivered changes and return accurate completion evidence and remaining dependencies.

## Inputs

| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
| [input:workspace_root] | Explicit validated workspace root. | Mandatory | Host coordinator. | Retrieve before dependent work. |
| [input:instructions] | Fixed and applicable workspace/session instructions. | Mandatory | Caller and readable fixed instructions. | Empty readable file is valid; missing instructions block dependent work. |
| [input:authority] | Actual human task, scope, constraints and permissions. | Mandatory | Human request relayed by host. | Retrieve existing authority; never invent permission. |
| [input:activity_context] | Validated core state, stable active Activity and relevant current records. | Mandatory | Host and runtime evidence. | Return missing dependency; no standalone bypass. |
| [input:implementation_result] | Actual directive identity, task results, changed paths and observed checks. | Mandatory | Implement assigned work result relayed by host. | Retrieve actual evidence; never infer completion. |

## Prerequisites

Validated selected configuration, mandatory instructions, compatible environment, stable active Activity and meaningful authorized assignment. Current implementation evidence and applicable verification obligations.

## Rules

None.

## Steps

1. Establish [input:workspace_root], [input:instructions], [input:authority] and [input:activity_context]; retrieve authorized missing context and stop dependent work on unresolved prerequisites.

2. Compare [input:implementation_result] with the current directive and acceptance criteria. Inspect each artifact/operation, baseline attribution and direct/indirect effects, including generated/untracked/deleted/moved paths; do not charge unchanged pre-existing edits to this run. Review the actual delivery/inclusion scope under the shared artifact placement contract, resolve misplaced working material/evidence within authorization, and retain requested reports/logs as deliverables where designated.

3. Perform developer verification against the current directive and acceptance criteria. Report missing or contradictory criteria rather than inventing a pass. Select meaningful automatic/manual, boundary, negative and regression checks by changed behavior and failure risk, following required conventions. Confirm available tools, authorized test-side effects and assigned evidence destinations before execution. Record the tested version, environment, inputs, expected and actual behavior; map criteria to passed, failed, blocked, skipped or unrun checks. Retain reproducible defects and coverage limits, distinguish observations from suspected causes, and identify human/external acceptance methods. Investigate and correct authorized failures and rerun affected checks only, preserving earlier evidence and identifying changed inputs. These developer checks do not establish independent QA or product acceptance.

4. Return agreed managed knowledge/history updates and required independent review through host. Keep required owner work pending until actual validated evidence returns; disabled specification is not permission to enable or silently omit required work. Record why no knowledge update was needed where applicable.

5. Inspect protected paths against baseline and exact covering authority using the existing protection contract. Report unauthorized paths in stable order and stop affected success handoff without reverting them. Check workspace boundaries and outside-write provenance, including indirect tool effects.

6. Prepare execution evidence and run execution_contract.py with the current directive/context/evidence. Verify all required tasks, checks and owner dependencies are represented, not merely a convenient subset. A failed mandatory history operation remains a blocker under existing no-automatic-retry safeguards.

7. Return verified, blocked or partial result with exact artifacts, task outcomes, actual checks, decision provenance, limitations and known usage-source availability. Host owns runtime persistence, recording synchronization, independent acceptance and any separately authorized closure; no future outcome is fabricated.

## Outputs

| Output | Meaning | Completion criteria |
| --- | --- | --- |
| [output:work_result] | Delivery evidence with verified/blocked/partial status, current artifacts and unresolved acceptance risks. | Actual results, evidence, current identity and unresolved dependencies are distinct; host persists canonical records. |

## References

- [Role instructions](../ROLE.md) — inherited safeguards and conditional references; required throughout.
