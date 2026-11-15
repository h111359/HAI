---
name: crete-design-package
description: "Create or revise a human-reviewable design package before implementation. Use when the user needs a complete proposal with clear requirements, a precise solution specification, worked examples, responsibilities, a delivery plan, and a linked plain-language reading guide. Applies to technical and nontechnical projects."
---

# Create a design package

Produce a proposal that a reviewer can understand, question and approve without
having to infer important behavior from implementation details. Preserve technical
precision while providing an equally faithful human reading path. The subject may
be a product, service, process, organization, policy, physical arrangement or system.

## Establish the assignment

Obtain the following from the request and authorized project context. Ask only for
missing information that materially affects the design; do not make the user repeat
known facts or complete an exhaustive questionnaire before useful work can begin.

| Input | How to use it | When it is missing |
| --- | --- | --- |
| Problem and desired result | Establish the objective and what success means. | Ask a focused question before inventing the objective. |
| Users, participants and reviewer | Choose understandable terms, responsibilities and review depth. | State a provisional audience and ask if the choice affects the solution. |
| Requirements and accepted decisions | Preserve stated intent and distinguish it from recommendations. | Draft explicit proposals; do not label them as agreed. |
| Constraints and existing environment | Account for budget, ownership, technology, facilities, people, policies and dependencies as applicable. | List consequential unknowns and continue independent design work. |
| Scope and authority | Establish what may be designed, inspected, edited or implemented. | Default to the requested design deliverables, not operational changes. |
| Evidence and existing material | Ground descriptions of present conditions and compare options. | Label assumptions and illustrative examples; do not invent inspection or research results. |
| Output location and conventions | Place the review package and its supporting work appropriately. | Use the project's established document location; clarify a consequential ownership conflict before writing. |

For a revision, read the existing package and the user's actual review comments
first. Change only the requested subject and the dependent text needed to keep the
proposal consistent. Do not change unrelated project settings.

## Plan the review package

Read [package contents](references/package-contents.md) before drafting a new package
or materially changing its organization. Use its document responsibilities as the
baseline, adapting names and splitting depth to the actual topic and project rules.

The package provides:

1. A review entry point and decision/status overview.
2. Requirements and observable acceptance scenarios.
3. A precise solution specification.
4. A plain-language companion linked to the specification section by section.
5. Complete worked examples and representative outputs or records.
6. Responsibilities and component/role design where the solution needs that detail.
7. An implementation or delivery plan, verification approach, risks and limitations.

Use meaningful documents rather than empty scaffolds. A small package may combine
closely related subjects, but preserve the distinction between explanation,
requirements, solution decisions, examples and delivery instructions. Do not force
software components, agents, APIs or code tests into a nontechnical design.

## Write for a reviewer

Read [clarity and review guidance](references/clarity-and-review.md) when drafting
requirements, acceptance scenarios, explanations or responses to review comments.

- Write requirements with an explicit subject, action and object. Name who or what
  must provide the behavior; do not rely on a table heading to supply the subject.
- Give each requirement and scenario a stable identifier. State observable outcomes
  and identify the responsible participant or mechanism.
- Define unfamiliar terms and named actors before using them. Distinguish a person
  or decision-making agent from a checking tool or record-keeping mechanism.
- Replace vague quality labels with the actual written condition and where it is
  defined. An output's existence does not prove that its contents meet expectations.
- Keep the detailed specification precise. Do not turn it into another requirements
  list or bury user-visible decisions in technical descriptions.
- Give the companion the same section order as the specification. Explain meaning,
  purpose, an example and review decisions, with a link to the exact technical section.
- Mark accepted decisions, unapproved proposals, assumptions, open questions and
  technical mechanisms distinctly. A request for explanation is not acceptance.

## Develop the complete proposal

Start with the intended result and define the boundaries, participants, major parts
and normal operation. Explain how the parts exchange information, resources or
responsibility. Define necessary inputs, outputs, locations, naming and completion
conditions at a level that another person could apply without guessing.

Describe alternatives where a real choice exists. Recommend one and explain its
consequences, including limitations the reviewer might otherwise regret discovering
later. Avoid inventing elaborate alternatives solely to fill a comparison table.

Cover interruptions, exceptional outcomes, revisions and recovery when they matter.
State what remains unchanged, what may be repeated, what needs a decision and which
effects cannot simply be undone. Explain internal mechanisms separately from the
behavior they support. Do not prescribe databases, counters, retries, approval gates
or distributed execution unless the particular design needs them.

Work a realistic example through the proposed rules, including a normal path and
at least one meaningful exception or correction when applicable. Use actual example
names and representative contents, not only abstract arrows. Clearly label invented
examples and measurements. Demonstrate how earlier decisions and context survive a
handoff; a reference alone does not supply information that the next participant
cannot access under the design's own rules.

## Check and revise

Review the package against the inputs before delivery:

- Map requirements to relevant design sections, examples and planned verification.
  Inspect what the mapping actually covers; a link alone is not evidence of coverage.
- Walk the examples against the design. Check definitions, references, information
  availability, decision rules, outputs and exceptional paths for contradictions.
- Check local links, anchors, identifiers, diagrams, tables and structured examples.
  State what checks were performed. Do not claim a production validator or executed
  process exists because a document consistency check passed.
- Separate permanent solution requirements from this assignment's workflow or
  authorization instructions. Do not convert a one-off review condition into a
  product feature, core mechanism or permanent regression test.
- Use independent critique when the task or applicable rules require it, or when a
  substantial proposal benefits from it and delegation is authorized. Report whether
  the review was independent and what it actually covered; do not invent consensus.

When the user flags confusing wording, answer the immediate question in plain
language, then repair the wording and related terminology rather than merely adding
more jargon. When the user approves a principle, record that approval at its actual
scope; do not treat it as approval of every mechanism or example value beneath it.

Preserve earlier material versions using the project's revision practice. Keep
identifiers stable; if an item is removed, mark it retired rather than silently
renumbering unrelated items. Update affected examples and explanations, and identify
which checks or earlier reviews need refreshing. Do not describe an older review as
covering new changes.

## Deliver for review

Provide one clear starting link, identify the current draft, summarize substantive
choices and point out unresolved decisions. Let the reviewer inspect one section at
a time without implying that reading or silence grants approval.

Treat the detailed specification as the authoritative design proposal and its
companion as a faithful explanation, not a competing proposal. Resolve discrepancies
or surface them explicitly before asking the user to approve the package. State
that approval of a design and authorization to implement are separate unless the
user explicitly combines them.

Keep supporting check results, review notes and drafting material in their assigned
project/task locations. Review actual deliverable inclusion. Do not add unrelated
implementation, installations, operational configuration, publication or commits
merely because the design describes them.
