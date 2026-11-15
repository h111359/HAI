# Independent workflow design review

Date: 2026-11-14. Activity 1b440d51-819b-4299-862b-0182f0f4fca5; invocation 54114a86-cc14-4e53-ac1a-5aaa7e673328. Design review only; no installed workflow, agent or runtime changed by reviewer.

## Coverage

Reviewed all six design documents and both complete illustrative definitions, plus shared workspace/artifact/agent contracts. Manually walked all example result edges and file bindings; a read-only check confirmed defined step targets for both examples (customer-request 5 steps/11 results, change-assessment 1 step/3 results). No workflow runtime exists yet, so this is not execution or parser verification.

## Findings

1. **High, corrected during review:** clarification return initially carried only questions plus a requirements reference/hash, losing earlier clarified answers under the immediate-predecessor-only input contract. Parent now explicitly requires complete prior clarified requirements and attributable answers verbatim inside the questions handoff, updates analyst expectations/instructions and the worked trace. Reviewed that correction; it addresses the handoff gap without implicit history lookup.
2. **Medium, clarification requested:** execution ownership must include an allocated-but-not-started attempt. prepare-step should reserve ownership and repeated preparation must not allocate multiple live attempts before record-execution. Specify its run status and reservation rule.
3. **Medium, clarification requested:** pause/resume for an unfinished stopped attempt needs a precise transition. Resume must retain unaccepted partial effects and require explicit reconciliation/retry, never automatically replay a former running attempt.
4. **Medium, clarification requested:** identical accepted completion replay with an old expected_revision should return retained acceptance before stale-revision rejection; specify precedence and operation-id behavior.
5. **Low, scope visibility:** md/json/txt evidence-only contracts and nonempty JSON-object validation are additional first-version restrictions rather than user requirements. Highlight as review choices. Agent registration should consistently be execution readiness, distinct from role-name syntax/structural validity.

## Assessment

The package accurately separates agreed requirements from recommendations and implementation from review. Single-file definitions, one entry, unlimited named results, explicit result artifacts, serial coordination, single-Activity identity and manager/host/core ownership are clear. Custom Activity-store location versus literal .hai_env status placement is exposed as an explicit user decision, not silently assumed. The runtime proposal is substantial; the first-version scope choices should be reviewed before implementation approval.

No additional demonstrated graph/file-contract issue found after the clarification baseline correction. Remaining administrative clarifications above should be settled before treating the design as an implementation baseline. This report records review-time findings; parent revisions may resolve them afterward.

## Follow-up review

Parent incorporated all requested corrections. Verified prepared run status reserves ownership at allocation; repeat prepare returns the retained assignment; previously started unaccepted work requires effect reconciliation/retry on resume; identical accepted completion is checked before stale-revision rejection; artifact-format restrictions are explicit review choices; role syntax is separate from execution readiness. Acceptance A21-A23 and implementation trace are present. Clarification baseline fix remains intact. Reviewed predecessor folder exists at files/revisions/workflow-design/20261114_191919_reviewed-draft. No remaining material internal inconsistency found in those corrections. This is clearance to present the design for user review, not implementation approval or runtime verification.
