# Synchronize the Activity conversation

At every turn and before commits/closure, run `recording synchronize` with the current activity_id and actual provenance, adding --apply to append missing messages. Preview is read-only and does not reserve message IDs. Applied chat-post also reconciles registered sources.

Inspect warnings and actual changed paths. All recognized human/delivered assistant occurrences in assigned sources go into system/chat.jsonl; system/recording.json stores references and progress. A source without an observable final reply cannot supply it yet. Do not reconstruct it or claim a background delivery hook. Replay after an interrupted publication uses durable bindings and source-qualified identities.

For old transcript stores, preview/apply `recording migrate` first; preserve predecessor evidence. Then synchronize and run `recording verify`. Never deduplicate equal text or broaden the Activity range silently. See [recording](../conventions/chronicles_conv.md).
