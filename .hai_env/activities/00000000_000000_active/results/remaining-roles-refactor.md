# Remaining roles: complete job packages

All roles now own their job-specific methods. No installed role has a mandatory
skill dependency. The shared and installed packages match.

## Review entry points

- [Role collection guide](../../../../roles/README.md).
- [Skill collection guide](../../../../skills/README.md).
- [Developer verification procedure](../../../../roles/software-developer/procedures/verify-and-handoff.md).
- [QA assessment procedure](../../../../roles/quality-assurance/procedures/perform-assigned-work.md).
- [Current dependency check](../evidence/quality-skill-removal/dependency-check.json).
- [Post-removal tests](../evidence/quality-skill-removal/verification.json).

## What each role owns

| Role | Owned methods |
| --- | --- |
| Business-analyst | Context acquisition, clarification ledger, readiness/protection conventions, proposals and helpers. |
| Solution-architect | Technical assessment, decisions, implementation-plan format and checker. |
| Software-developer | Directive validation, implementation, developer checks, execution evidence and delivery. |
| Quality-assurance | Independent product assessment, risk-based checks, reproducible defects, criterion coverage and host handoff. |
| Git-manager | Integration configuration, repository operation procedures, commit/recording/publication safeguards and helpers. |
| Release-manager | HAI release/versioning/readiness/publication methods; environment-only. |
| HAI framework advisor | Read-only complete framework review and recommendations; environment-only. |

Backlog-manager and Specification-manager retain their previously revised packages.
Role identities, catalogue descriptions, model declarations, settings, workflows
and product records remain unchanged.

## Verification belongs to its job

At the user's request, quality-verification was removed from both skills/ and
.hai_env/skills/. The earlier independent-skill experiment remains in historical
evidence; it is not a current dependency or installed capability.

Software-developer now directly checks the current implementation against its
directive and acceptance criteria, selects relevant boundary/regression checks,
records actual results and limits, and corrects authorized failures. These checks
do not establish independent product acceptance.

QA directly establishes subject/version, criteria, scope and actual independence;
selects risk-based checks; preserves observed results; reports reproducible defects;
and returns criterion coverage and limitations through the host. QA does not
silently repair the product or invent approval. Both roles preserve the Activity,
record ownership and authority safeguards already established.

The root skills collection now contains only the unchanged crete-design-package.
It remains an uninstalled source package. The environment's installed skill list
is empty. Independently useful skills can still be selected for concrete tasks;
no placeholder capability was created to replace the removed abstraction.

## Preservation and checks

The original all-role consolidation preserved 238 predecessor files and 155
protected files. All source-backed roles were replaced through reviewed runtime
installation; workspace-only roles were authored in place. Production helper
changes were limited to the developer's installed architect-helper lookup path.

For this follow-up, 24 affected role/skill files were preserved under
history/quality-skill-removal/ before replacement/removal. All 242 unrelated
package/configuration/workflow/backlog files remain byte-identical. Known installer
backups are retained there and completed empty staging folders were removed.

The latest checks ran 44 tests: 23 package/integration tests and 21 developer
tests, with 2 total skips and no failures. The new integration test installs every
shared role with no source or installed skills folder, then removes the source
role collection and validates each installed role with an empty dependency list.
All nine actual installed roles also validate with empty skill dependencies;
resolving the retired skill fails as expected and startup succeeds.

The broader pre-removal consolidation ran 131 tests with 7 skips and independent
review. Its earlier reports and skill trial are retained as historical evidence;
the dependency check linked above describes the current state. Existing Windows
fixture encoding fixes remain test-only. The registry CLI's documented -X utf8
mode is required for reliable non-ASCII stream handling. Skipped checks and the
unavailable PyYAML-dependent optional validator are not claimed as verified.

No commit, push or Activity closure was performed.
