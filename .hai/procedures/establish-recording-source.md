# Establish a conversation source

Recording is always enabled; no feature toggle is required. Safely resolve only the current host-identified source with `recording discover`. Verify its identity/workspace and obtain the actual first saved work-prompt position for this Activity. Never infer a boundary from the latest prompt, timestamps or matching text.

Each applied `recording synchronize` without explicit sources retries discovery
for an unbound current session. When it reports `needs_boundary`, the host checks
the saved source against the actual Activity start or session handoff and applies
`recording bind` once it has verified the first assigned occurrence. Continue
this check on later turns if the source or boundary is initially unavailable.

Use `recording bind` with activity_id, source identity/path/representation, observed start_position and provenance. The source Activity range is continuously recorded. Unified recording needs no enabled_intervals argument. Bind previews without --apply. Apply persists the source, imports missing occurrences, and refreshes usage from the authorized range. Supply additional usage-only sources separately when available.

If the Activity contains old transcripts, use explicit `recording migrate` first. Unknown boundaries require clarification/evidence; unavailable sources produce warnings while direct chat capture continues. See [recording](../conventions/chronicles_conv.md).
