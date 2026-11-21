# Shipping report assessment

The supplied report fails its policy: four of six assessed criteria pass and two fail. All six criteria were checked against all applicable supplied rows; no report criterion was blocked, skipped, or unrun. ORD-101 and ORD-102 are correct. ORD-103 has incorrect shipping and ORD-104 has an incorrect grand total. These are observations of this report, not conclusions about any generating software.

## Subject and method

Read-only inputs: `fixture/shipping-report.csv` and `fixture/shipping-policy.md`. The supplied quality-verification skill and its `procedures/perform-assigned-work.md` were followed using only these explicit inputs; no HAI role or environment setup was needed. Checks ran on 2026-11-20 at 21:37:44 UTC with Python 3.14.7 on Windows 11, using standard-library CSV parsing, Decimal arithmetic, format checks, and supplied-order comparison. No installs, external services, product edits, or operational Activity mutations occurred.

Input SHA-256 values, unchanged across the check:

- Policy: `9d51635672b8518d16570357a24ecdabbf3e45fd19f8e25aa3927ce79d48258a`
- Report: `c0de585014db1d9937d271620a319edb80dd0b2a8e18aa509caab3a1aef33fa6`

## Actual criterion coverage

| ID | Supplied criterion | Result | Observed evidence |
| --- | --- | --- | --- |
| C1 | Nonnegative subtotal; status paid or pending | Pass | All four subtotals are nonnegative and all statuses are allowed. |
| C2 | Paid orders at or above 100.00 receive shipping 0.00 | Pass | ORD-101, CSV line 2: paid, 120.00, shipping 0.00. |
| C3 | All other orders receive shipping 5.00 | Fail | ORD-102 and ORD-104 pass; ORD-103, CSV line 4, is pending but shipping is 0.00. This also violates the policy's restriction on when zero shipping is allowed. |
| C4 | Grand total equals subtotal plus shipping | Fail | ORD-104, CSV line 5: 50.00 + 5.00 = 55.00, but grand_total is 54.00. Other rows satisfy addition using their reported shipping. |
| C5 | Decimal currency amounts rounded to two places | Pass for this report | All 12 amount fields have exactly two decimal places; all supplied values and expected arithmetic are exact at this precision. No fractional-cent rounding case exists. |
| C6 | Preserve IDs; one row per supplied order | Pass | Exactly four rows, each supplied ID appears exactly once, and there are no extra IDs. Subtotals and statuses also match the supplied orders. |

These are six assessment criteria derived directly from the supplied policy; C2 and C3 together cover both directions of the free-shipping condition. The 4/6 count describes this mapping, not a statistical confidence score or general software test coverage.

## Reproducible findings

1. **ORD-103 has incorrect shipping (C3).** At CSV line 4, `ORD-103,150.00,pending,0.00,150.00` reports free shipping. The policy requires both paid status and subtotal at least 100.00 for free shipping; pending requires 5.00. Expected shipping is 5.00 and the policy-consistent total is 155.00. The reported total of 150.00 adds its own fields correctly, but is 5.00 below the policy-consistent amount. Cause in any generating implementation is unknown.
2. **ORD-104 has an incorrect grand total (C4).** At CSV line 5, `ORD-104,50.00,paid,5.00,54.00` reports grand_total 54.00. Shipping 5.00 is correct, so expected total is 55.00. The total is understated by 1.00. Cause in any generating implementation is unknown.

Together, the reported grand totals sum to 409.00, whereas policy-consistent totals sum to 415.00, a 6.00 understatement. This is a report discrepancy; no actual billing or financial loss was established.

Reproduce from `C:\Users\hmhri\Desktop\repos\HAI` in PowerShell:

```powershell
& 'C:\Users\hmhri\AppData\Local\Python\pythoncore-3.14-64\python.exe' -B 'C:\Users\hmhri\Desktop\repos\HAI\.hai_env\activities\00000000_000000_active\work\agents\skill-evaluator\6e5bd9e3-6ea1-41f9-a876-ef4c6da6c492\verify_shipping.py'
```

The script reads the inputs, compares all four orders with the supplied order list and policy, prints per-row results, and writes only `verification-evidence.json` beside itself. Expected reproduction: `shipping_pass=false` for ORD-103 and `addition_pass=false` for ORD-104. Compare input hashes before applying these findings to another version. Detailed evidence is in [verification-evidence.json](verification-evidence.json); the executable check is [verify_shipping.py](verify_shipping.py). Expected orders are transcribed from the supplied policy in the script, rather than inferred from the report.

## Limits and attribution

No supplied criteria were missing or contradictory. The current report covers paid above threshold, paid below threshold, and pending above threshold. It contains no subtotal exactly 100.00, pending below threshold, zero subtotal, invalid-input cases, or fractional-cent values. General boundary behavior, rounding tie rules, invalid-input handling, generating code, and regressions were not tested; they are outside the supplied static-report scope. No product fixes or rechecks of corrected inputs were performed. Changed report or policy bytes require a new assessment.

Independent acceptance was not requested. This assessment was produced by the evaluator from supplied artifacts; the original report author's identity and any author/reviewer relationship were not established, so independent-review status is unverified. This result does not grant approval or publication authority.

Skill usability: no method or prerequisite issue encountered. The skill worked from explicit inputs without HAI setup. The host's renamed workspace required scoped escalated writes into the authorized invocation directory; those writes were allowed. This was an environment constraint, not a skill failure.

Caller-supplied host attribution: Activity `88af2e3d-2e2e-4a0b-9ea3-50ba3b194e93`; invocation `6e5bd9e3-6ea1-41f9-a876-ef4c6da6c492`. These labels were supplied by the caller, not independently verified from operational records. No token/usage account identity or measurements were available from these checks. All invoked processes were synchronous and completed; no background writers were started.
