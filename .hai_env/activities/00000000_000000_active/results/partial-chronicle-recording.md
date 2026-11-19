# Save recognized chronicles through unsupported records

## Result

HAI's recording runtime now automatically retains recognized messages before and after unsupported records. Unknown content is represented by physical source-position gaps and warnings, rather than blocking the known part or being guessed into chat. It does not require configuration changes.

A safely saved incomplete transcript reports status recorded_with_gaps, coverage partial and warnings identifying source session, source position and reason. The source ledger, checkpoint and transcript metadata retain matching gaps. Known text and physical positions remain exact; replay does not duplicate exchanges. Verified ranges exclude unknown positions and the last complete-success timestamp is preserved until coverage is complete.

Strict standalone reading remains available. Runtime uses read_source(..., allow_partial=True); CLI users can opt in with --allow-partial. The CLI can return success for a usable partial subset while ok/complete remain false; callers must inspect coverage rather than infer completeness from the exit code.

## Boundaries

Unsupported validly framed source records, including unfamiliar outer types and message shapes, no longer suppress supported messages. Unknown records outside assigned enabled ranges do not make that Activity incomplete. Routine usage/world/delegation-control metadata is excluded only in the inspected shapes documented by the source convention.

Source identity conflicts, unsafe paths, unstable reads, invalid JSON framing and corrupted retained evidence retain their protections. A rewrite cannot erase retained unknown history or known messages. Enabled-interval changes cannot hide recorded gaps. Reviewed interpretation upgrades over unchanged source bytes can resolve gaps while retaining predecessor ledger/checkpoint/transcript evidence.

Required-completeness closure saves recognized content and gap evidence before refusing closure. Best-effort closure may finish with recorded_with_gaps, including a trailing unknown record. Reports use the actual applied recording result, avoiding preview/apply false-completeness races. Successful partial storage is distinct from a failed or incomplete write.

## Verification and independent review

The implementation agent /root/partial_recording_implementation used allocated invocation 16c10315-95eb-45e2-b088-1592d9d9fa6d. A separate reviewer /root/compaction_review reused its allocated invocation d6c47fb0-87f3-44e1-9f5c-91b6fa5dcc58. Both completed without further code writers.

Developer runs passed: reader25 (1skip), runtime chronicles33 (1skip), source discovery18 (1skip), source continuity80 (2skips, includes reused chronicle cases), recording policy8 (0skips). Broader runs preceded final metadata exclusions and the gap-enablement guard; final reader/runtime runs cover those changes. Counts overlap and must not be summed as unique tests.

Independent review passed an 81-test baseline (3skips), plus the two final focused metadata/enablement regressions (2passed). It found and verified fixes for erased-gap source rewrites and a preview/apply closure reporting race. No final blockers remain. Existing older complete records remain readable; older runtimes may reject the extended gap-bearing format, as documented.

Twelve changed core Markdown documents had no missing actual local link targets. git diff --check passes. All test files and isolated workspaces remained in Activity-owned disposable work directories.

## Real-session operation

The first tolerant smoke test successfully saved32 recognized messages despite unsupported metadata warnings. After reviewing and recognizing the exact metadata shapes, resynchronization retained the predecessor partial evidence in chronicles/history/ and resolved those gaps without changing native source files. Final preview coverage complete; synchronization verified; message_count32; warnings0; one coverage-update reconciliation; fresh verify and startup both verified. Only the registered current main-session source is covered; no unknown participant-session coverage is claimed.

The earlier archived boundary repair and its historical gap from the preceding task remain unchanged. Independent review also noted an unrelated pre-existing representation issue: some numeric verified spans can cross disabled intervals although actual message filtering respects enablement. That issue was not expanded into this bounded unknown-record-storage change.

No commit or Activity closure was requested or performed.
