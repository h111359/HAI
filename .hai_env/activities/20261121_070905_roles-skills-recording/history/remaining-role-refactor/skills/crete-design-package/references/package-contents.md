# Design-package contents

Use this reference to organize a complete proposal. These are document
responsibilities, not a mandatory directory layout for every project. Respect a
requested location or established document standard. Markdown is a useful default
for linked review documents; use another requested format when appropriate.

## Review entry point

Suggested name: `00-review-guide.md`.

Include the draft identity/date, review status, objective, short solution overview
and a reading order with descriptive links. Explain what exists today and what is
only proposed. A diagram may help show the main parts or sequence.

Provide a decision overview with the subject, current choice or recommendation,
reason/consequences and actual status. Separate the user's accepted principles
from unsettled details. Alternatives should help the reviewer make a real choice;
do not treat a recommendation as approved or an explanation request as acceptance.

State the review/implementation boundary for this assignment here. That boundary
is project working context; it is not automatically a requirement of the designed
product, process or service. Record review coverage and limits accurately.

## Requirements and acceptance scenarios

Suggested name: `01-requirements.md`.

Separate attributed user requirements, derived needs, recommendations, assumptions
and open questions. Give durable requirements stable IDs and an explicit subject,
action and object. Identify the required capability or constraint, not a mechanism
chosen without justification. A coverage column may point to the proposed solution;
its sentences should also identify their subject and action.

Explain new domain/design terms before the scenarios. Introduce actors by their
actual responsibilities rather than interchangeable labels such as reviewer,
validator, manager and system. Link existing project concepts when they provide
the intended definition, but make the main review text understandable on its own.

For each scenario, give a concrete situation and observable required response.
Identify who performs the action and who or what checks it. Keep internal algorithms
out of scenario wording unless they are themselves a user requirement. Include
failure or exceptional conditions that affect the promised result, not a speculative
list of every possible incident.

Distinguish artifact presence, format validity, content adequacy and real-world
outcomes. Identify the authored expectation or agreed requirement being checked.
Describe evaluation measures and limits without presenting proposed checks or
illustrative measurements as performed evidence.

## Solution specification

Suggested name: `02-solution-specification.md`.

Explain how the proposal satisfies the requirements, rather than repeating the
requirements in longer language. Define the decisions needed to implement or apply
the solution without consequential guesswork. Organize the specification by the
actual topic; useful subjects include:

- Participants, concepts, responsibilities and boundaries.
- Major components, physical arrangement, process stages or service interactions.
- Inputs, outputs, documents, records, resource ownership and locations.
- Naming, structure or exchange formats when consistent interpretation requires them.
- Decision rules, result conditions, handoffs and completion expectations.
- Changes over time, exceptions, interruption/recovery and repeat work where relevant.
- Interfaces or operating actions; integration with what already exists.
- Compatibility, constraints, risks, safeguards and limits of the proposed guarantees.

Give each concept and rule one authoritative home and link to it elsewhere. Keep
mechanism detail beside the behavior it supports but distinguish the two. A proposed
restriction on formats, naming, sequencing or flexibility is a decision the reviewer
must see, not an unnoticed implementation default.

Explain separate identity/version concepts individually if the design uses them;
do not use one unexplained word such as version for unrelated counters, editions
and compatibility markers. Do not introduce such mechanisms where they are unnecessary.

## Plain-language specification companion

Suggested name: `02a-solution-reading-guide.md`.

Identify the specification revision the companion explains. Preserve its section
order and give every section a direct link to the corresponding technical heading.
Start with a short glossary of unfamiliar terms and, when helpful, a relationship
diagram or a concrete location/layout example.

For each section answer:

1. What does this part mean?
2. Why is it needed?
3. What would happen in a concrete example?
4. Which decisions are accepted, which are proposals, and which details merely
   explain the mechanism?

Use ordinary words before specialist terms. Retain the important restrictions,
tradeoffs and exceptional behavior; easier reading must not hide consequences.
The companion explains the same proposal, not a simplified alternative with different
rules. State that understanding a section does not itself approve it.

## Complete worked examples

Suggested name: `03-worked-examples.md`, with purposeful files under `examples/`
when a complete example is easier to inspect separately.

Provide a realistic initial situation, explicit assumptions and concrete names,
inputs, outputs and representative contents. Walk the normal path and an important
exception, correction or handoff when applicable. Show how the next participant
receives all needed information under the proposal's own rules.

Include complete representative definitions, forms, specifications, layouts or
records as appropriate to the domain. Do not substitute a high-level diagram for
an example that is needed to verify precise behavior. Distinguish conceptual
placeholders from valid, actionable examples and keep their interpretation explicit.

Show locations and ownership where the design depends on them. Describe actual
business/product destinations separately from working copies, evidence or receipts.
Mark every fictional trace and invented result as illustrative. Do not operate a
real service, apply a configuration or create an external effect just to illustrate it.

## Component and responsibility design

Suggested name: `04-components-and-responsibilities.md`; choose a more specific
title when the design introduces one substantial component or role.

Describe the responsibilities, inputs, outputs, exclusions, relevant rules and
procedures of the parts that need their own detailed contract. Examples include
an organizational role, staffed desk, service component, policy owner, document
custodian or software module. Do not force an AI-agent structure into every topic.

Explain who owns shared knowledge and which tool or participant applies it. Avoid
conflicting copies of the same rule. Separate defining or checking a component from
activating or operating it. Where the domain uses reusable source material and local
deployments, distinguish source maintenance from installation, configuration and use.

If this subject is genuinely small, cover it in the specification rather than
generating an empty separate document. Keep the full responsibility information
accessible through the review entry point either way.

## Delivery and verification plan

Suggested name: `05-delivery-and-verification-plan.md`.

Map the proposed changes to their continuing owners and canonical locations. Identify
what will be added, changed, preserved, migrated or retired. Describe practical stages,
dependencies, prerequisites, checks, review points and remaining risks. Keep current
task working material out of the proposed maintained deliverable by default.

Trace planned verification to the durable requirements and scenarios. Use checks
appropriate to the domain: trials, inspections, rehearsals, simulations, document
reviews, measurements or software tests as needed. Distinguish planned, performed,
unavailable and unverified checks. Do not turn this particular design assignment's
approval instructions into permanent product tests.

Make limits and uncertainties visible. If later execution would need a consequential
design change, explain how that change returns to review rather than assuming it
is covered by the earlier approval. A delivery plan describes possible future work;
it does not itself authorize that work.
