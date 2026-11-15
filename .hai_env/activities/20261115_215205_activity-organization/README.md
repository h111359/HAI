# Predictable Activity organization

Implementation is verified. The human has explicitly requested Activity closure and a local commit.

## Objective

Apply the agreed file-generation and storage rules, preserve human instructions independently of chronicles, and use this README for navigation and the final report when the Activity is eventually closed.

The actual implementation instruction is retained in system/chat.jsonl as message a5d46b52-69c4-460d-be99-be9960ed31a9. Original legacy context and records remain attributable in the migration history.

## Delivered changes

- README is the sole root document; operational records are under system/.
- Review outputs, verification, predecessors and disposable work use results/, evidence/, history/ and work/ with declared ownership and retention.
- New typed chat preserves human/assistant/agent messages with truthful delivery status, independently of optional chronicles. New Activities create no input.md or outcome.md.
- Runtime supports standard-input requests, explicit migrations, safe work cleanup and README-based closure. Existing legacy archives remain compatible.
- This Activity and the [inspected workflow archive](../20261115_195335_workflow-implementation/README.md) have been migrated without deleting historical evidence or rewriting accepted workflow artifacts.

## Review

- [Verification and limitations](evidence/verification.md)
- [Independent review](evidence/reviews/activity-layout.md)
- [Activity generation and naming contract](../../../.hai/conventions/activity_conv.md)
- [Conversation contract](../../../.hai/conventions/activity-chat_conv.md)
- [Runtime operations](../../../.hai/tools/runtime/README.md)

Closure and a local commit are authorized by the latest human instruction; publication is not requested.

<!-- hai-navigation:start -->
## Navigation

- [Conversation](system/chat.jsonl)
- [Work log](system/log.md)
- [Usage](system/usage.md)
- [Verification evidence](evidence)
- [Previous versions](history)
<!-- hai-navigation:end -->

## Final outcome

Completed predictable Activity organization and persistent conversation changes.

Delivered layout 2: README.md is the entry point and final report; state/log/chat/usage and recording recovery metadata live under system/. Results, retained evidence, predecessors and disposable working material have explicit results/evidence/history/work destinations. Typed conversation records human instructions independently of chronicles and distinguishes prepared assistant text from observed delivery. Standard-input requests avoid permanent request JSON files; exact content and artifact provenance are preserved. Explicit migration and bounded work cleanup are supported.

Migrated this Activity and the specifically inspected historical workflow Activity without reopening or altering the older closure. Original input/state/outcome and historical working evidence remain preserved with mappings. All older workflow-run bytes and final feasible result remain unchanged. All 148 previously tracked archive files have retained nonignored destinations. No other historical Activity was migrated.

Verification: broad runtime251(10 platform skips), startup66(8), activities16, chronicles17(1), configuration13(3), agents75(6), parser23(1), all successful; final focused28 passed without skips. Independent combined79 checks and final targeted reviews found no remaining material defect. Essential failed probes and fixes are retained in evidence/reviews. Final package validation and startup passed after migration. Disposable test work was removed only after review/evidence retention and ended writers.

Limits: Windows/Python3.14.7 verified; other OSes and scale benchmarks unrun. Human/assistant capture is an explicit host protocol, not an automatic UI interception service; historical unrecorded chat was not fabricated. Current source-backed chronicles have no usable assigned checkpoint following the known host-format incompatibility. Best-effort recording retains this coverage gap. Actual final commit identity belongs in Git history and the delivered acknowledgement; no future commit result is fabricated here. No push or publication requested.

Recording: unavailable — Recording interrupted; retained evidence preserved; coverage gap: Enabled chronicles require explicit source assignments before closure/synchronization

Provenance: source: user: close the activity and commit; reason: refresh human entry point and evidence for authorized closure and local commit
