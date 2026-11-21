# Present startup guide

## Description

Present a brief, current overview of HAI and its selectable next actions. Use the
same interaction for startup, repeat Help and selections from the displayed menu.

## Inputs

| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
| [input:request] | Actual human request and relevant conversation intent | Mandatory | Current conversation | Clarify intent before selecting work |
| [input:context] | Current primary runtime startup result, including independent issues | Optional | `.hai/tools/hai.py startup --workspace .` | Attempt the read-only check; report unavailable facts if it cannot run |
| [input:previous_menu] | Last displayed choices and their meanings | Optional | Actual conversation | Do not guess the meaning of a number or other context-dependent choice |

## Prerequisites

Use the [user communication convention](../conventions/user-communication_conv.md).
Translate runtime states into what the user can do now. Keep menu command names
available for selection and explain each choice in everyday language.

The host has applied the safe fixed mandatory instructions and higher-priority
session instructions before dependent work. Independent read-only diagnosis and
reporting of missing prerequisites remain possible under `.hai/start.md`.

## Rules

- **Observed facts.** The host MUST use verified independent startup observations for role and Activity information, and MUST label missing, invalid, partial or unverified information without treating it as absent.
- **Combined choices.** When presenting a menu, the host MUST include supported task choices and every valid registered role as individual choices in the same menu; grouping MAY improve readability without hiding roles in a submenu.
- **Display effects.** The host MUST NOT create, replace, resume, close or advance an Activity, change product settings or registrations, install packages, or invoke an agent solely to display startup or Help. Normal source-backed recording retains its existing obligations.
- **Compact presentation.** The host MUST limit the opening explanation to two sentences and use one compact entry per choice, without a total-length cap that omits registered roles or reproducing full role manuals.
- **Selection identity.** The host MUST NOT reinterpret a stale, ambiguous or unknown choice as a different action; numeric choices require their actual previously displayed mapping.

## Steps

1. Interpret [input:request] using the conversation. Distinguish startup alone,
   startup with a concrete task, an explicit Help/menu request and a selection.
   An ordinary task containing the word “help” remains a task according to its
   intent; an internal startup check does not introduce a menu into unrelated work.
2. Obtain fresh [input:context] for startup and repeat Help. Before dispatching a
   selection, refresh relevant observations and recheck its identity and affected
   prerequisites; an earlier overview is neither a lock nor proof of availability.
   Inspect independent results even when the command fails. If the helper cannot
   run, report that limitation and only facts independently verified safely.
3. Build the summary from those facts:
   - List the names of valid workspace registrations from `roles`, not all source
     packages. With a valid empty/absent registry, say no roles are registered.
     With a partial registry, retain its valid rows and report incomplete discovery;
     an invalid or unverified registry does not prove there are no roles.
   - For a current Activity, show its stable ID, lifecycle and relevant work-step
     state. Show its supplied goal when available from authorized context. Label
     truncated input as an excerpt rather than an agreed goal; state when the goal
     is not supplied. With validated absence, say no Activity is active; with invalid
     discovery, say its state could not be verified and report the actual issue.
   - Identify actual issues that affect available next steps, including separate
     recording readiness. Keep valid independent information useful when another
     component fails. Do not run a blanket audit of role definitions/configurations
     or claim runtime/model availability was checked by startup.
   - Show each unfinished workflow from the Activity's `workflows` summary
     with its name, run ID, status, current step and pending action when supplied.
     Report partial or unverified discovery from that summary. Viewing it does
     not resume, retry or publish a workflow.
4. For startup with a concrete task, include the role/Activity summary in the
   first response and proceed with that task through the existing continuity,
   permission and recording checks. Do not require a menu selection. For startup
   alone or explicit Help/menu, assemble the following combined choices from
   supported operations and current observations:

   | Choice | Inclusion and meaning |
   | --- | --- |
   | `continue` | Current valid Activity: continue its agreed work, asking for direction if the next action is unclear |
   | `new-task` | Describe a task; existing Activity continuity is resolved before any creation or replacement |
   | `backlog` | An established, available backlog workflow: select an item through its existing owner |
   | `role-setup` | Describe an installation, registration, authoring or configuration need; supported operations and their owners are checked before changes |
   | `help` | Refresh this brief overview and menu |
   | `workflows` | List optional single-file workflow definitions through `workflow list`; do not execute them merely to display choices |
   | `role:<name>` | Every valid registered role: select that role for a meaningful assignment |

   Stable text choices avoid renumbering when registrations change. Optional
   numbers refer only to the menu actually displayed in the conversation.
   Use a concise purpose from each role's registered selection guide and say
   “registered; availability checked when selected” where readiness is unknown.
   Label known blocked operations with their actual dependency; do not disable
   independent valid operations of the same role. Describe `new-task` and
   `role-setup` as requests for input, not promises that execution is available.
   Omit unsupported workflow choices; do not create a backend or install a missing
   owner just to populate the menu. Backlog files alone do not establish an owner.
5. Present the summary and menu together. Invite a stable choice, an optional
   displayed number or an unambiguous plain-text request, then wait. Reporting a
   current Activity during startup alone does not resume its work. Explicit Help
   reports the same brief type of overview using refreshed facts, without replaying
   initialization or requiring a new Activity.
6. On a selection, map stable identifiers, displayed numbers or equivalent clear
   prose to their intended action. Compare context-dependent choices with
   [input:previous_menu]. If its mapping is missing, ambiguous, no longer current,
   or the role was removed, clarify or show a refreshed menu and wait; do not
   remap a number to a newly reordered entry. A clear new task does not require
   a previous menu merely because it resembles one of the stable choices.
7. For a valid selection, retrieve the existing action/role instructions and check
   the affected configuration, actual host/model/tool capability, authority,
   Activity continuity and recording prerequisites. Ask only for missing necessary
   inputs; a bare role choice needs an assignment before role work. Route to
   existing core operations or the selected registered role under the shared
   delegation policy. Report an actual dependency before blocked work, preserve
   independent valid capabilities and distinguish selection from successful execution.
   For `workflows`, return the validated list with per-file issues. For an explicit
   `workflow:<name>` or ordinary-language run request, resolve that definition and
   follow [Execute workflow](execute-workflow.md), preserving current Activity,
   authority and readiness checks. An existing run needs its exact identity when
   several runs make a pause/resume/cancel request ambiguous. Listing workflows
   requires no authoring package and does not change definitions or registrations.

### Illustrative presentations

These are examples, not workspace observations or saved human exchanges. Replace
all names/state with current facts, and include every valid registered role.

Valid workspace with one registered role and a current Activity:

```text
HAI helps you choose and carry out work using this workspace's registered roles.
Activity <UUID>: active; clarification completed, planning in progress; goal: <supplied goal>.
- continue — Continue the current Activity.
- new-task — Describe a task.
- role-setup — Describe a role setup need.
- help — Show this overview again.
- role:example — Review requirements (registered; availability checked when selected).
Choose an option or describe what you want to do.
```

Valid workspace with no registrations and no current Activity:

```text
No roles are registered, and no Activity is active.
- new-task — Describe a task.
- role-setup — Describe a role setup need.
- help — Show this overview again.
Choose an option or describe what you want to do.
```

Partial startup with a valid registration and invalid Activity discovery:

```text
Activity state could not be verified: <actual discovery issue>.
- new-task — Describe a task; Activity discovery must be resolved before dependent work.
- role-setup — Describe a setup need; affected prerequisites will be checked.
- help — Refresh this overview.
- role:example — Review requirements (registered; Activity-dependent work blocked).
Choose an option or describe what you want to do.
```

## Outputs

| Output | Meaning | Completion criteria |
| --- | --- | --- |
| [output:overview] | Current summary and, for startup alone or Help, combined menu | Actual registrations/Activity state or explicit uncertainty; compact selectable choices and invitation to choose |
| [output:next_action] | Task continuation, mapped selection, necessary question or dependency | Existing checks respected; no arbitrary dispatch or claim of unperformed work |

## References

- [Startup](../start.md) — entry conditions, instructions and recording obligations; required throughout.
- [Runtime commands](../tools/runtime/README.md) — read-only observations and existing operations; required when calling runtime.
- [Role convention](../conventions/role_conv.md) — registration, operation prerequisites and delegation; required before role work.
- [Activity convention](../conventions/activity_conv.md) — continuity and record ownership; required for Activity-dependent work.
