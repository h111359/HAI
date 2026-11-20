# Specification-manager revision

Specification-manager is a complete role. It owns the knowledge and tools needed
to maintain the specification and has no mandatory skill dependency.

## Review entry points

- [Source ROLE.md](../../../../roles/specification-manager/ROLE.md).
- [Installed ROLE.md](../../../roles/specification-manager/ROLE.md).
- [Helper instructions](../../../../roles/specification-manager/scripts/README.md).
- [Test results](../evidence/specification-role-refactor/verification.json).
- [Transfer and integrity checks](../evidence/specification-role-refactor/final-integrity.json).

## Resulting ownership

| Owner | Content |
| --- | --- |
| Specification-manager | Specification concepts, registered document-type conventions, tree format, seven procedures, settings and tree contracts, auditor, settings helper, tests and helper documentation. |
| Independent skills | Optional capabilities selected for an actual task; none is required or added by this revision. |
| HAI core | Activity and recording lifecycle, common configuration/path infrastructure and package installation. |
| Workflow | Role assignments, expected outputs, dependencies and human decision points. |

The role now has 48 files. All 46 supporting resources previously in
specification-management were transferred. Its 27 shared constraint groups,
procedure index and required references were transferred from SKILL.md into
ROLE.md alongside the original job responsibilities and authority limits.

The two contracts remain distinct:

- configuration/contract.json defines HAI-owned enablement/location settings.
- contract.json defines the specification-tree compatibility version, still 1.

Existing settings remain disabled at .hai_env/specifications; this revision does
not enable, initialize, adopt or migrate a specification tree. Product formats,
identities, catalogue rules, human migration approvals and acceptance boundaries
remain unchanged.

## Standalone use

The explicit-root tree auditor remains callable outside HAI from a complete copy
of this role package. It does not import HAI core or the settings helper. The
HAI-specific settings helper separately requires compatible core and the installed
role configuration contract. The existing relocated-package test verifies audit
operation without .hai or .hai_env and from unrelated working directories.

A tool's ability to run independently does not require packaging it as a skill:
it implements this role's particular specification contract. No new document,
PDF or other speculative skill was created or installed.

## Installation and preservation

The installed snapshot was replaced through HAI runtime using reviewed differences.
Both old specification-management skill directories were removed only after all
98 original source/installed files were preserved and hash-verified under
history/specification-role-refactor/. The known installer backup is retained there;
the completed empty staging folder was removed.

The source and installed role match after expected core-link rebasing. All 35
protected backlog/configuration/contract files retain their original hashes. Both
production helpers retain their original bytes. Collection guidance and integration
checks now identify the role as the owner.

## Verification

- Installed audit/settings suites: 52 tests, 5 skips, no failures.
- Package integration suite: 22 tests, 1 skip, no failures.
- Total: 74 tests run, 6 skipped. Skipped host-dependent checks remain unverified.
- The new real-package integration test installs the role without any skills,
  removes the source collection, preserves both contracts and checks read-only
  default/custom disabled settings without creating specification trees.
- An existing Windows Unicode fixture failure was corrected by explicit UTF-8
  text IO in the tests; production helper behavior was not changed.
- Independent review found two plain-text references to the former SKILL.md and
  one stale ownership sentence. These were corrected. Final follow-up passed
  with no further findings; no reviewer writers remain.
- Fresh startup and read-only installed settings checks pass.

No commit or Activity closure was performed.
