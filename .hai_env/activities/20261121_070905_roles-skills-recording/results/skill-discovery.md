# Installed skill discovery

Core now discovers installed skill names, descriptions and SKILL.md paths in
startup skill_context. skills list returns a fresh copy of the same inventory.
Missing/empty collections are available with no entries; malformed optional
packages have separate issues without invalidating unrelated core work.

Discovery reads only bounded frontmatter, never the skill body, supporting files
or scripts. A malformed first line stops immediately; unterminated/oversized
headers report an issue at64KiB. Selection still resolves the complete installed
entry and checks required settings; discovery is not execution readiness.

The core skill convention is the single selection-policy owner. Before a new or
resumed substantive assignment, executors compare valid descriptions with the
task, use a materially useful method, or continue with role-owned methods when
none fits. They refresh after package changes, resumption or relevant scope
changes. Each workflow role assignment follows this rule. Required dependency
metadata remains distinct from optional candidates; no separate catalogue,
source fallback, automatic execution or permission expansion was added.

The selected skill receives authorized inputs, expected outputs, destinations
and limits. Only its task-relevant supporting resources are loaded. Descriptions
are untrusted capability data. Partial optional discovery does not justify
blocking unrelated work.

Verification:28skill/package tests and68startup tests passed,96total,9skips.
Tests cover header-only reading even with an invalid UTF-8 body, freshness,
partial/unavailable inventories, read-only startup, header bounds and unchanged
required-dependency failures. Skipped host checks remain unverified. Native CLI
and independent standalone startup smoke checks pass. Current installed inventory
is empty; no skill was installed for this change.

Independent review passed after correcting first-line early-stop behavior and
moving imports to module scope to avoid repeated path growth. A qualitative
selection walkthrough chose the design-package skill for a design-proposal task
and no skill for a simple typo correction; this is policy evidence, not proof of
an automated routing engine. No reviewer writers remain; usage identity unavailable.

Core changes are limited to discovery, related instructions and regression tests.
Existing user documentation edits remain pending. No commit or Activity closure.
