# Activity token cost at published list rates

Price check:2026-11-21. Based on the same saved main-session snapshot reported
previously, through2026-11-21T04:06:37.744Z (80,445,743tokens). This does not refresh
or extend the token cutoff. Related sub-agent usage sources are unavailable and
excluded; no other model totals can be inferred from role configuration.

[OpenAI Work/Codex Standard rate card](https://help.openai.com/en/articles/20001415-chatgpt-rate-card-enterprise-token-based-pricing) lists GPT-6.1 Sol at
USD2.00/million uncached input,0.10/million cached input and10.00/million output.
[The model's API page](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
also lists those base token rates. [Reasoning documentation](https://developers.openai.com/api/docs/guides/reasoning)
identifies reasoning tokens as billed output.

| Recorded model | Type | Tokens | USD per million | Calculated USD |
| --- | --- | --- | --- | --- |
| gpt-6.1-sol | uncached_input | 1,226,619 | 2 | 2.453238 |
| gpt-6.1-sol | cached_input | 78,957,824 | 0.10 | 7.8957824 |
| gpt-6.1-sol | reasoning_output | 95,508 | 10 | 0.95508 |
| gpt-6.1-sol | other_output | 165,792 | 10 | 1.65792 |

Total before rounding:USD12.9620204; approximatelyUSD12.96.

The types are disjoint: cached input is subtracted from total input and reasoning
is subtracted from total output before calculating the other rows. Output is not
charged twice. Formula:sum(tokens_by_type * rate_per_million /1,000,000).

This is a Standard-mode published-rate equivalent, not an invoice, actual
subscription spend or a complete all-agent Activity cost. The recorded data do
not identify billing arrangement or service speed. If every request instead used
Fast mode's2x rates, the equivalent would beUSD25.9240408, approximatelyUSD25.92.
Feature fees, tax and other applicable adjustments are not included.

OpenAI's rate card says Codex signed in through ChatGPT does not have the
long-context multiplier and does not charge cache writes. Codex using an API key
follows API pricing; qualifying long-context and cache-write charges may apply.
The inspected source has large last-input snapshots, so a no-surcharge API bill
must not be inferred. No API cache-write charge is calculated from nonexistent
cache-write counters. Current rate assumptions are not proof of historical billing.

The managed usage.json/usage.md remain token-and-credit records. This USD estimate
is retained separately and does not introduce monetary configuration into HAI.
