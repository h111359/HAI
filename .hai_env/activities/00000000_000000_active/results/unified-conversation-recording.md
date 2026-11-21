# Unified, always-enabled conversation recording

Implemented the approved single-conversation design and migrated the current Activity. New layout-2 recording stores human entries, delivered assistant replies and visible commentary/progress in system/chat.jsonl. Participant coordination remains explicitly typed in that file. system/recording.json contains bindings, occurrence references/hashes, warnings and recovery state, with no repeated message bodies.

## Current behavior

- Recording cannot be enabled/disabled or scheduled by a prompt threshold. New environment defaults have empty features. The old current-environment chronicles settings were preserved then retired. Configuration rejects the former toggle/mode/cadence controls; archived compatibility data remains readable.
- Applied chat-post captures its message and automatically checks registered sources for missing saved messages. Host instructions also require synchronization on every new/resumed turn, after source work, and before commits/closure. Startup performs read-only missing-message checks and reports required action.
- Synchronization rechecks retained occurrences and the whole assigned Activity range, including earlier newly recognized messages, rather than only a tail cursor. Source-qualified identities and durable coordinate epochs distinguish repeated text, separate sessions and position reuse after format changes. Observed original source timestamps/positions remain separate from append/capture order.
- Source registration is durable before imports; normal retry resumes interrupted append-before-state publication without resupplying the source. Retained chat is append-only, with exact old-prefix/readback checks. Session-start identity, source freshness and Activity/environment ownership are checked.
- Missing sources and unsupported valid records produce explicit coverage warnings without suppressing recognized content from available sources. Internal analysis, tools and system/developer messages are excluded. Visible clarification questions presented through host UI tools must be captured by the host when observed; native tool plumbing alone is not assumed to expose their visible text.
- Closure flushes chat and rechecks the live assignment through archival, catching replies arriving during closure. Independent mandatory completeness obligations remain enforced after supported messages are saved. A registered source with an unknown end prevents archival rather than silently dropping its tail or consuming the next Activity's range.

## Live preservation results

The pre-migration chat was 24,346 bytes. Its complete byte prefix is unchanged. All112 previously indexed source messages are represented with their exact text and source-qualified identity. All7 old transcript/checkpoint/ledger/reconciliation files have byte-for-byte verified backups, including the prior recovery history.

Current operational locations:

```text
system/chat.jsonl
system/recording.json
history/recording/before-unified-v1/
```

The old active chronicles/ and system/chronicles/ folders were retired only after publication/readback and backup verification. Their original trees, the original chat snapshot and old environment settings remain under the history location. Backup references are Activity-relative and remain valid after archival. New migration manifests cannot retire chat or unrelated operational files.

The first post-migration source check retained117 native messages. Checking the actual host format exposed a second historical commentary filter in completed-item normalization; the unified adapter now includes those visible replies. The subsequent catch-up retained227 native messages, with no missing messages or source warnings at that checkpoint. A final fresh verification accompanies this report; later counts can increase as messages become available.

Existing source-less human posts remain intact alongside source-backed occurrences where their identity could not be proved. No equal-text deletion or guessed historical association was performed. Import order is capture order; native positions/timestamps preserve original conversation order.

## Verification and review

The latest consolidated evidence covers32 shipped modules and607 tests, including38 skips, with every executed test passing. This combines the broad run and targeted reruns, not a claim of a new simultaneous whole-suite run. Initial failures from intentional defaults/API changes remain in evidence alongside passing reruns. The28 dedicated recording regressions cover exact preservation, repeated text, cross-session IDs, source-coordinate reuse, source-format identity changes, missing-middle backfill, prepared/delivered distinction, visible commentary in completed-item/auto formats, unavailable sources, late closure replies, ownership changes, interrupted migration, safe retirement and archival verification.

A standalone CLI installation initialized from only .hai/, created only .hai_env/ at its root, recorded native human/progress/final replies, verified them and closed its fixture Activity successfully. The separate core boundary regression also passes. Current real workspace startup is valid.

Independent reviewer /root/unified_recording_review used allocation26df9bc7-08ce-483e-af08-d4183096ec86. It reviewed requirements, code and retained evidence and passed the final candidate, including preservation hardening. It did not rerun the tests, modify files or leave outstanding writers/background work. An attributable reviewer usage source was unavailable; none was invented.

## Practical limits

Always enabled means capture/reconciliation is always attempted while HAI is running. There is no assumed background service or post-delivery host hook. This turn's final reply can be imported once saved, normally at the next interaction. Missing/inaccessible sources, unknown formats and unknown session assignments remain visible limitations; HAI cannot truthfully guarantee capture of messages the host has not exposed. Existing archived Activities are preserved and readable rather than silently rewritten. Layout-1 Activities require explicit Activity-layout migration before recording migration. Older runtimes may reject new records; downgrades require reviewed restoration from preserved predecessors.

## Evidence

- [Latest test results](../evidence/unified-conversation/verification-summary.json)
- [Dedicated preservation regressions](../evidence/unified-conversation/final-preservation-tests.json)
- [Standalone CLI installation](../evidence/unified-conversation/clean-install.json)
- [Pre-migration hashes and preview](../evidence/unified-conversation/live-baseline.json)
- [Applied migration](../evidence/unified-conversation/live-migration.json)
- [Initial preservation audit](../evidence/unified-conversation/live-preservation-audit.json)
- [Completed-commentary backfill](../evidence/unified-conversation/completed-commentary-live.json)
- [Final source verification](../evidence/unified-conversation/final-verification.json)
- [Preserved original files](../history/recording/before-unified-v1)

The Activity remains open. No commit was requested for this implementation.
