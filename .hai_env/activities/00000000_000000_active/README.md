# Skill portability investigation

Activity: `88af2e3d-2e2e-4a0b-9ea3-50ba3b194e93`

## Objective

Investigate all source and installed skills, assess HAI-independent reuse and external skill adoption, research best practices, and recommend the responsibility boundary between skills, roles, workflows and HAI integration. The human will decide how to continue before implementation.

## Review result

Start with the [investigation and recommendation](results/skill-portability-review.md). The recommended direction is portable methods with HAI-specific usage supplied by roles and shared operational enforcement retained in the framework. The report covers all 12 distinct skills and identifies compatibility limits.

The initial investigation is complete. The human subsequently accepted the boundaries and authorized a bounded source collection cleanup. Review the [cleanup result](results/source-collection-cleanup.md) for the two source removals, four source renames and preservation checks. The human then authorized matching installed identities: see [installed administration names](results/installed-admin-names.md). Four installed administration packages and their registrations now match the hai- source identities. Unrelated installed content and runtime behavior remain unchanged; broader portability refactoring has not started. The Activity remains open.

## Evidence and limitations

- [Static package audit](evidence/skill-portability-audit.json): 22 packages, 252 non-cache files.
- Source/installed comparison: all 124 corresponding files differ only in Markdown link targets where differences exist.
- Research: five primary documentation sources; links and interpretation in the report.
- No end-to-end portability trials or independent second-agent review were performed.
- Chronicles synchronization previously reported missing explicit source assignments. This remains a recording coverage gap; canonical human message capture is retained separately.

## Navigation

- [Conversation](system/chat.jsonl)
- [Work log](system/log.md)

<!-- hai-navigation:start -->
## Navigation

- [Conversation](system/chat.jsonl)
- [Work log](system/log.md)
- [Reviewable outputs](results)
- [Verification evidence](evidence)
- [Previous versions](history)
<!-- hai-navigation:end -->

## Current result: authoring merged into core

The human subsequently requested complete core consolidation. See [core authoring merge](results/core-authoring-merge.md). Both definition managers and their authoring skills are now core procedures/conventions; their source and installed packages and catalogue registrations have been removed after preservation checks. All 14 resources and 57 checked authoring rules are accounted for, and a core-only fresh-install check passes. Earlier source cleanup and installed-rename reports describe preceding states, not the current installation. The Activity remains open; no commit was made.
