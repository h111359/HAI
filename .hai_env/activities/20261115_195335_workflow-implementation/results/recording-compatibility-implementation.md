# Recording compatibility implementation

Implemented 2026-11-14 under explicit user authorization. Scope: chronicle compatibility repair; workflow definitions/manager remain a separate pending implementation.

- Reviewed adapters: legacy event messages, completed nested UserMessage/AgentMessage, response messages. Automatic selection never merges views or ignores interpretation errors. Known tools, reasoning, progress and inter-agent assignments are excluded.
- Bounded location lookup: exact host session identity, checked workspace and canonical source; missing/foreign locators can resolve to a validated local candidate. No newest-file or unrelated-content lookup.
- Exact continuity: indexed text/role plus turn or message identities and order; conservative unambiguous legacy rendering; live continuously enabled assignments only. Unknown/off-period/closed boundaries require explicit resolution.
- Hashed predecessor history and reconciliation provenance; unknown formats follow the maintained adapter procedure and independent review. No executable source-provided adapters.
- Missing recording mode defaults best_effort. Ordinary work can continue with explicit unverified coverage; required mode and independently mandatory operations retain gates. Optional closure can report source unavailability before writes; integrity/security/partial-write errors stay strict.

## Verification

Windows, Python 3.14.7. Workspace-contained regression runner: runtime 194 tests (10 skips), chronicles 17 (1 skip), startup 66 (8 skips), activities 16 (0 skips). Total 293 run, 19 platform skips, no failures in final run. Independent reviewer separately reproduced and verified fixes for identity-conflict downgrade, shifted archived overlap and silent unknown messages, then approved final reader/recovery changes. No Linux/macOS execution available; foreign-locator behavior was fixture-tested.

## Actual Activity recovery

Preview and apply succeeded for this Activity: 19 eligible messages, one exact source reconciliation. Predecessor core ledger, checkpoint and segment were independently compared byte-for-byte against history/fda37473-6b3f-43f6-98c6-19e0aac3d167. Fresh recording verify passed. Current final response is not yet saved and is not claimed recorded. Activity stays active; no commit, push or closure performed.

## Limits

Unknown formats require reviewed code support, not speculative extraction. Arbitrary file locations need an authoritative supplied path/configured session store. Ambiguous legacy framing, changed/missing messages, closed/discontinuous ranges and stale archived coordinates are not automatically rebased. Unavailable sources leave visible gaps rather than invented coverage. Related participant usage/recording attribution remains unavailable without verified native assignment positions; no child source boundaries were guessed.
