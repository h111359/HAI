# Requirements and acceptance scenarios

Source: only the supplied brief. A borrower requests or holds equipment. The two coordinators handle bookings and handovers. The organizer reviews policy and is proposed as the policy decision maker. A pending request is not a promise; a confirmed reservation specifies an item and collection/return Saturdays.

U identifies brief constraints or their explicitly derived needs. P identifies unapproved service requirements. The instruction not to launch during this trial is assignment scope, not a permanent service feature.

| ID | Requirement and authority | Specification section | Example | Planned verification |
| --- | --- | --- | --- | --- |
| U01 | The service must account for its 20 items. Brief quantity; tracking is a derived need. | 2 | E01 item entry | V01 |
| U02 | The two volunteer coordinators must be able to manage bookings using shared current information. Brief staffing; sharing is a derived need. | 1, 6 | E01 handoff | V02 |
| U03 | Coordinators must arrange every pickup and return for a Saturday. Explicit brief constraint. | 4 | E01, E02 | V03 |
| U04 | The service must not accept online payments. Explicit brief constraint. | 5 | E02 | V04 |
| P01 | Coordinators should apply the approved eligibility rule before confirming reservations. Proposal. | 2, 3 | E01 | V05 |
| P02 | Coordinators should avoid overlapping confirmed bookings for an individual item. Proposal. | 3 | E02 | V06 |
| P03 | Coordinators should record condition, accessories and possession at collection and return. Proposal. | 4 | E01, E02 | V07 |
| P04 | Coordinators should record incidents, notify affected borrowers and refer disputed responsibility to the organizer. Proposal. | 5 | E02 | V08 |
| P05 | The designated records owner should control access, retention, corrections and succession under an approved policy. Proposal. | 6 | E01 handoff, E02 correction | V09 |

See the [specification](02-specification.md), [examples](03-examples.md) and [verification plan](05-delivery-plan.md) for the referenced coverage. Each mapping was inspected for the behavior described, rather than treated as sufficient merely because a reference exists.

## Acceptance scenarios

These describe future observable checks, not performed evidence. Proposed responses depend on approval of the relevant P requirements and D choices. The organizer observes each rehearsal.

- A01: Given the actual inventory, a coordinator lists 20 distinct item identifiers and statuses. The organizer compares the physical items and entries to find omissions or duplicates (U01).
- A02: Given one coordinator's absence, the other finds borrower contact, terms, item, condition, dates and next action in shared records without needing a private conversation. The organizer checks that handoff (U02, P05).
- A03: Given a Tuesday handover request, a coordinator offers a Saturday instead and records no Tuesday handover arrangement. The organizer checks the reply and register (U03).
- A04: Given a proposed charge, a coordinator offers no online payment route. While D04 is unresolved, the coordinator records the question without demanding money. The organizer checks communications (U04).
- A05: Given unclear eligibility under the chosen policy, a coordinator leaves the request pending and asks the organizer to resolve the ambiguity. The organizer checks the reason against approved terms (P01).
- A06: Given overlapping requests for one item, a coordinator confirms at most one under the approved allocation rule and informs the other borrower of the outcome. The organizer checks both records (P02).
- A07: Given missing accessories or damage on return, a coordinator records observations and the borrower's account, marks the item unavailable pending assessment and informs the next affected borrower. The organizer checks records and notices (P03, P04).
- A08: Given a departing coordinator or borrower correction request, the records owner follows the chosen transfer/access-removal or correction procedure. The organizer checks that current records remain available to the successor and that the request reaches the named owner (P05).
