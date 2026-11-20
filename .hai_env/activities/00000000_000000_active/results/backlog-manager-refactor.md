# Backlog-manager revision

Backlog-manager is a complete job package. It owns its backlog-specific knowledge
and procedures and has no required skill dependency. It may use independently
useful skills when a concrete task needs them.

## Review entry points

- [Source ROLE.md](../../../../roles/backlog-manager/ROLE.md).
- [Installed ROLE.md](../../../roles/backlog-manager/ROLE.md).
- [Original refactor checks](../evidence/backlog-role-refactor/verification.json).
- [PDF removal receipt](../evidence/backlog-role-refactor/pdf-removal.json).
- [Latest package checks](../evidence/backlog-role-refactor/pdf-removal-tests.json).

## Role contents

The source and installed role each contain ROLE.md, the unchanged configuration
contract, the backlog convention, four procedures (configuration, maintenance,
draft import and Activity handoff), and the auditor with tests and documentation.
All eight former backlog-management resources and shared constraint groups were
transferred before retiring that skill from both live collections. All 22 original
source/installed package files were preserved and byte-verified in Activity history.

The role retains configuration, record format, IDs, decisions, history, catalogue,
import provenance, semantic review and handoff ownership. Core retains lifecycle,
recording, installation and shared path protection. Workflows retain sequencing.

## Independent skills

A selected skill receives authorized sources, expected results, paths and task
limits from the role. Activity-specific scratch and evidence destinations take
precedence over example/default folders. The role remains responsible for reviewing
results and obtaining attributable decisions; a skill grants no acceptance authority.

The initially added PDF skill was removed at the user's request after checking
that no role, workflow or configuration required it. Neither skills/pdf/ nor
.hai_env/skills/pdf/ exists now. Its role-specific examples and collection references
were removed; generic independent-skill installation coverage remains in the tests.
Removed packages and the previous role snapshot are preserved under
history/pdf-skill-removal/. No replacement skill was created.

Earlier PDF installation/readiness evidence describes the superseded implementation
and is retained as history, not as a claim that PDF remains installed.

## Verification

After PDF removal, the package integration suite ran 21 tests: no failures, 1 skip.
Backlog-manager validates and reports an empty mandatory skill list. Resolving PDF
correctly reports it unavailable. Backlog data, settings and contracts retain their
original hashes.

Before removal, the role consolidation passed 122 tests with 8 skips and independent
review. The actual backlog audit passed (11 completed, 1 cancelled, 1 pending).
The focused post-removal results above describe the current package state.

No other role was refactored. No commit or Activity closure was performed.
