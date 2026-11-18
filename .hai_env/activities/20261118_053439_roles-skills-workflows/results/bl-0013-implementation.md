# BL-0013 implementation

Implemented the role/skill/workflow responsibility model throughout the maintained
framework, source collections, installed environment, concepts, README and installation
instructions. No product publication, Git commit or Activity closure was performed.

## Delivered behavior

- Source role packages live directly under root roles/. The old hai_roles_library
  container is retained as exact migration history and is absent from the live source.
- Root skills/ contains the existing design-package skill plus ten extracted reusable
  capabilities. Installed .hai_env/skills/ contains the domain capabilities and the
  workspace-only advisor skill. There are 10 source roles and 11 installed roles.
- Roles retain responsibilities, constraints and model policy, reference skills and
  select the method for workflow assignments. Native SKILL.md bodies remain free-form;
  direct skill use needs no role adoption. Unnecessary empty role contracts are gone,
  while real service/role settings remain owned once with their original chosen bytes.
- Real installers adapt cross-package/core Markdown references at the final installed
  depth, preserve source bytes and literal examples, and validate staged content.
  A complete installed distribution works with source collections removed.
- The source workflow workflows/software-development.md provides prepare, clarify,
  design, design approval, implementation, QA, human acceptance and backlog completion.
  It uses all five requested roles; Backlog-manager participates again at the end.
- Workflow format3 supports environment location configuration, separate run folders,
  runtime-numbered step filenames, result-specific accepted inputs and historical
  feedback. Full input lineage survives partial returns; stale inputs/approvals block
  dependent acceptance. Actual typed human instructions plus checkpoint-bound host
  semantic assessment govern the two human gates. This is not cryptographic authentication.
- Authoritative accepted evidence stays with the Activity. Configured destinations
  hold run-specific artifacts; canonical product files keep their owners. Runtime never
  automatically publishes stable names, closes an Activity or invents human acceptance.

## Installation and use

Use the normal HAI startup, then request a role or installed skill. Skills can be
installed before their dependent roles through skills install / roles install previews.
The core installation guide and runtime README document exact request fields.

The new development workflow is ready to install from its source definition. A
workflow install preview asks for two workspace-relative base destinations, handoffs
and completion, with their purposes and expected contents. HAI must obtain the human's
actual choices before apply; no destination was invented during implementation.
Installation alone starts no run. Existing reusable workflows and historical runs stay
compatible; the retained finished format1 pilot still opens after this change.

## Verification

The final full sweep covered 527 core tests across runtime, startup, Activity,
chronicles, configuration, role, skill and workflow parser suites, with30 platform
skips. Its only failure was an invalid test fixture copying installed-role bytes into
an incompatible source layout. The fixture was corrected to canonical source; its
focused6-test suite passes (1 skip). Every other test in the full sweep passed.
The strengthened real distribution/portable-reference suite also passes16 tests.
No fresh all-green527 rerun is claimed; the complete sweep plus the relevant focused
correction close the checks without repeating unrelated passing tests.

Source and installed helper suites passed308 tests (24 documented OS/link skips).
Latest focused skill suite passed19 (1 skip). Independent tests exercised direct and
two-role use of one installed verification method against conforming and defective
fixtures, full QA/scope-change/reapproval loops, missing/stale approval blocks,
configuration/install/output-copy partial failures, target/candidate/marker races,
safe environment destinations, real source-absent bootstrap and host-owned backlog
completion with an actual fixture receipt while the Activity stays active.

Independent review assessed AC1-13 as delivered. All1,732 preserved original files
are retained byte-for-byte, including histories, settings, profiles, fixed instructions,
existing skill files and package predecessors. Source/installed customizations and the
installed-only advisor remain accounted for. Independent final link scan found1,414
local references valid; root parsed113 Python files and found no missing actual links.
The original failed checks and their resolutions remain in evidence.

Five preexisting bytecode caches were mistakenly removed during final cleanup after
an incorrect reviewer baseline attribution. Every file was restored to its exact
precleanup hash and independently verified. The correction and provenance are retained;
no source, chosen setting or historical record was lost. Existing cache paths remain.

## Review and limits

Read [independent final review](../evidence/bl-0013-review/final-review.md),
[core results](../evidence/bl-0013-tests/core-regressions.txt) and
[focused correction](../evidence/bl-0013-tests/package-install-final.txt).
Detailed package, preservation, capability inventory and workflow evidence is grouped
under evidence/bl-0013-roles-skills/, evidence/bl-0013-review/ and evidence/bl-0013-workflows/.

Checks ran on Windows/Python3.14. Skipped OS/link checks and Linux/macOS execution
remain unverified. Fixtures do not claim actual user acceptance or a production run.
Chronicle coverage remains unverified because Activity source assignments are missing;
best-effort synchronization was attempted and human messages persist in typed chat.
BL-0013 remains pending human acceptance. The Activity remains open and changes are
uncommitted, as neither closure nor a commit was requested.
