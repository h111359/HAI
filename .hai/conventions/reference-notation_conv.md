# Reference notation

## Meaning and namespaces

HAI uses literal, human-readable references:

| Reference | Meaning | Resolution |
| --- | --- | --- |
| `[term:Activity]` | A concept or supporting term. | An explicitly declared concept reference. |
| `[input:task]` | A procedure input. | That procedure's Inputs table. |
| `[output:result]` | A procedure output. | That procedure's Outputs table. |

These markers are references, not automatic substitution, execution, or authority.
Plain or inline-code rendering has the same meaning. Ordinary Markdown links,
regex character classes, data fields, and fenced examples retain their own syntax.
Do not replace bracketed text indiscriminately.

Input/output names use lower-case `snake_case`: a letter followed by letters or
digits, with single underscores separating nonempty words. Names are unique
within their input or output table; an input and output may share a name because
their namespaces differ. There is no rule-ID namespace.

Term names preserve their declared spelling and case, including meaningful spaces
or underscores. Names must be nonblank and contain no brackets, colons, or line
breaks. A namespace does not rename the underlying concept.

## Declarations and scope

Each input or output table's first cell declares its reference, for example
`[input:task]`. Uses elsewhere in that procedure resolve only to its own tables.
An external procedure file is one scope; the single inline procedure is another.
Shared role/skill rules and procedure indexes have no procedure-local input/output scope.

A procedure call explicitly identifies the source value or evidence and the
destination procedure's input name. Use a plain code name such as `task` for a
foreign destination; writing `[input:task]` denotes the current procedure's input.
Matching names across files never imply passing or inheritance.

Declare each external term mapping on one References bullet with one concept
Markdown link, for example:

```markdown
- [term:Activity] → [Activity concept](concepts/activity.md).
```

The concept link must resolve to an actual readable `concepts/` Markdown file
inside the workspace. Fragments may identify a section. Declare a term once per
References section. Mappings declared by a procedure's owning package apply to its procedures;
procedure-local additions are allowed. A procedure must not remap an inherited
name to another source. Identical repeated mappings are permitted but unnecessary.

Concept files declare their own concept through their title and Definition section.
Supporting terms use the declaration format in [concept_conv.md](concept_conv.md).
External terms identify their canonical concept sources in References.

## Verification boundary

The shared role tools check local parameter declarations/uses and explicit term
mapping paths in their documented Markdown subset. They do not prove that prose
uses a concept correctly, that a mapped source defines the intended meaning, or
that a value passed to a procedure satisfies its semantic requirements. Those
checks remain part of authoring and execution review.

## Skills and role-local procedures

Reusable task methods belong in skills. A skill may contain procedures, scripts,
templates, task knowledge and conventions without adopting the ROLE.md format.
The structured procedure contract applies to HAI procedure resources that declare
that contract; it does not force every external SKILL.md into a role template.
A role may retain genuinely role-specific procedures and helpers. Applicable role,
skill and workspace rules all remain in force; referencing a skill does not copy
its implementation or grant authority. Inputs/outputs retain explicit local
bindings, and shared conventions have one owner rather than competing copies.
