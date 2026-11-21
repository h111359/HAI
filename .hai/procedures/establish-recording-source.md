# Establish a conversation source

Recording is always enabled; no feature toggle is required. Safely resolve only the current host-identified source with `recording discover`. Verify its identity/workspace and obtain the actual first saved work-prompt position for this Activity. Never infer a boundary from the latest prompt, timestamps or matching text.

Use `recording bind` with activity_id, source identity/path/representation, observed start_position and provenance. The source Activity range is continuously recorded; no enabled_intervals argument is needed for unified recording. Bind previews without --apply; apply persists the source before importing missing occurrences. Supply usage attribution separately when available.

If the Activity contains old transcripts, use explicit `recording migrate` first. Unknown boundaries require clarification/evidence; unavailable sources produce warnings while direct chat capture continues. See [recording](../conventions/chronicles_conv.md).
