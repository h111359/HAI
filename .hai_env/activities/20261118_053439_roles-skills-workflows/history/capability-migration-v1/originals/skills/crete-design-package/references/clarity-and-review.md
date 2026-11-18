# Clarity and reviewer confidence

Use this reference when drafting or revising language the reviewer must understand.
Improve wording and definitions without changing agreed meaning.

## Requirements name a subject and an action

Avoid a fragment such as "Have one responsible owner." Write "Each request must
have one responsible owner" or "The service coordinator must assign one responsible
owner to each request," depending on the intended responsibility. The actor matters:
the second version assigns work that the first version does not.

Do not mechanically replace every can, may or preference with must. Preserve whether
the statement expresses an obligation, capability, permitted option, default or
recommendation. Separate multiple independently reviewable obligations when that
helps the reader discuss them.

Use stable IDs so comments survive revisions. Removing an irrelevant requirement
does not justify silently reusing its ID for a different requirement.

## Define actors and terms before using them

A reviewer, designer, coordinator, checking tool and record-keeping program are
different responsibilities. Name the actual participant or mechanism. If the proposal
introduces a new role, explain it locally; do not make the user guess whether it is
a person, software tool, AI agent or organization.

Use the project's existing concepts when they fit. Introduce only distinctions the
solution needs, and put their definitions before examples or acceptance scenarios
that depend on them. Prefer a familiar phrase over a glossary entry when the phrase
alone removes the ambiguity.

## Write scenarios as observable behavior

A scenario has an explicit situation or actor and a response with a responsible
subject. A reader should be able to explain what must happen without understanding
the implementation's request schema or storage algorithm.

Avoid "The output fails a semantic criterion." State the actual condition, for
example: "The report exists, but it omits a finding the written report requirements
require. The coordinator rejects the report and identifies the missing finding."
Identify where those report requirements are defined; do not create hidden acceptance
conditions or a new authority to invent them.

Avoid "The system handles a stale revision" when the intended behavior is "The
coordinator sends the same completion report twice because the first confirmation
was lost. The program confirms the previously recorded completion without performing
the work again." Keep any necessary counter/edition explanation in the specification,
where each kind of number is defined separately. This example is a writing pattern,
not a requirement that every design include retries or version counters.

Keep permanent acceptance criteria tied to the designed solution. A statement such
as "Do not implement during this review" normally belongs to this assignment's
scope/authority record, not the product's permanent feature list or regression suite.
An actual product requirement about approval behavior can still need its own tests.

## Separate precise design from accessible explanation

Do not discard a rigorous specification because it is hard to read. Keep it and
provide a faithful section-by-section companion. Each companion section explains
meaning, purpose, a concrete example and the decision the reviewer needs to make,
then links to the exact technical section.

Use a compact diagram to explain relationships or a sequence; use a table for
comparisons and mappings; use a location tree only when ownership or placement
matters. Avoid adding a visualization that merely repeats a simple sentence.

Surface consequences of internal choices. For example, saving an initial input copy
may improve repeatability but prevent later edits from automatically affecting work
already started. A restrictive document syntax may simplify checking but forbid
authoring features a user expects. Present the consequence where the reviewer sees
the choice rather than burying it in parser rules.

The companion must preserve restrictions and uncertainty. If its example contradicts
the specification, resolve the discrepancy before reporting the package ready for
review. Neither text silently overrides the other.

## Maintain a decision record with accurate scope

Distinguish:

- User requirements and facts established from available evidence.
- Proposals the designer recommends but the user has not accepted.
- Assumptions used to make progress and the consequences if they are wrong.
- Accepted decisions, their source and the specific principle or detail accepted.
- Open questions and unavailable evidence that still affect the design.
- Technical mechanisms that support behavior, including any user-visible restrictions.

If the user accepts a general structure, do not mark all detailed fields and limits
approved. If the user asks for simpler language, do not record a design acceptance.
If a user rejects a restriction, revise dependent examples and plans instead of
leaving the old restriction hidden elsewhere.

Ask for only the decisions needed at that point. A reviewer can work through one
section at a time. Do not force them to approve every implementation field, and do
not interpret silence or a successful consistency check as user approval.

## Respond to review through the documents

1. Answer the user's immediate question in plain language.
2. Locate the ambiguous wording and establish its intended meaning from accepted
   requirements; return a genuine unresolved choice to the user.
3. Preserve the predecessor under the project's revision practice before material changes.
4. Repair the wording, definitions and affected references without expanding scope.
5. Preserve IDs and record retired items. Refresh checks or clearly limit prior review claims.
6. Report what changed and leave unrelated sections available for the user's continued review.

Do not respond to every confusion by adding another large appendix. Replace jargon
and duplicated explanations when that is enough. The goal is informed review, not
document volume or the appearance of certainty.
