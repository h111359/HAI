# Source coverage

Historical transcript/closure-proof compatibility only. New layout-2 Activities use the [single conversation recording contract](../conventions/chronicles_conv.md). These older formats are retained for validation/migration, not a second active store or recording toggle.

## Definition

[term:Source coverage] is the exact completed-source exchanges verified in a segment, including its assigned start/end boundary and last synchronized message.

## Purpose

State verified synchronization precisely without claiming future, unsaved or excluded messages.

## Explanation

Coverage records what exact saved source has been verified. A cadence cursor means
which prompt occurrences were observed at batch dispatch. It is scheduling progress,
not evidence that the batch succeeded. A newer successful range or timestamp does
not fill an earlier source gap. Pending outcomes and missing retained source remain
separate from the count of new prompts.

Enabled intervals distinguish eligible source from off-period messages. Disabling
preserves existing gaps and files; it does not itself authorize historical backfill.
Successful source verification is a closure prerequisite in required mode or when
independently mandatory. Best-effort closure attempts verification and may retain
a `recorded_with_gaps` outcome for safely stored partial coverage or an explicit
unavailable outcome for source interruptions; it never labels a gap verified. Disabled/no-obligation closure has no transcript
prerequisite, while existing gaps remain part of the historical recording status.

A closure cutoff includes completed saved source through the user's closure
request. The final closure acknowledgement is not yet delivered, so it is outside
that pre-closure cutoff and can later belong to the original closed Activity.
Prepared pre-delivery text is a separate exception, not evidence of future saved
source. This distinction avoids requiring an operation to record its own future
acknowledgement before it can finish.

## Supporting Terms

None

## References

- [term:Transcript segment] → [Transcript segment](transcript-segment.md) — assigned range.
- [term:Durable session source] → [Durable session source](durable-session-source.md) — authoritative completed text.

## Recognized messages and unknown-record gaps

An unsupported source record does not invalidate recognized messages around it.
HAI retains those messages and the exact unknown position as partial coverage,
with a warning. Stored messages and complete coverage are separate facts.

Verified ranges must exclude unknown positions. A later supported message or
updated scheduling cursor does not resolve an earlier gap. Reviewed adapter
support may resolve it using the same source evidence and continuity checks.
Unknown content never becomes an invented prompt or outcome.
