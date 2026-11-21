---
name: quality-verification
description: "Verify a supplied deliverable against agreed acceptance criteria using risk-based checks, reproducible defects and explicit coverage limits. Use for developer checks or independent review of software, documents and other work products."
---

# Quality verification

Use this method to establish what a supplied work product actually satisfies.
The caller supplies the subject, current acceptance criteria, authorized scope,
available tools and evidence destinations. No role, project framework or
particular folder layout is required.

Read [Perform verification](procedures/perform-assigned-work.md) for the method,
input requirements and result contract.

## Essential constraints

- Evaluate the current subject against the supplied criteria. Identify missing or
  contradictory criteria; do not manufacture expected behavior or relax criteria
  to make a result pass.
- Keep verification and product repair separate. Use only checks and test-side
  changes covered by the task; report product defects for authorized correction.
- Distinguish observed pass/fail results from blocked, skipped and unrun checks.
  A lack of observed defects is not proof that untested criteria are satisfied.
- If independent review is required, establish the reviewer's relationship to
  the work and disclose conflicts or unavailable independence. Self-checks alone
  do not establish independent acceptance.
- Keep evidence attributable to the tested subject/version and environment.
  Retain uncertainty, partial results and reproduction limits. If relevant inputs
  change during verification, identify which conclusions require a new check.
- Return the requested report or write only to caller-designated destinations.
  Verification results do not grant approval, publication or other authority.
