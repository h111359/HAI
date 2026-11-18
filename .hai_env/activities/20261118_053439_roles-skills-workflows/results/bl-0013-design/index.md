# BL-0013 implementation design

[Roles and skills](roles-skills.md) covers foundations, extraction and migration. [Workflows](workflows.md) covers configured destinations, retained evidence, result-specific lineage and the initial development process. Independent review approved these bounded designs before core edits, with safety/preservation conditions sent to workers.

Roles select native skills; workflows assign roles and expected results. Existing source/installed differences, settings and historical bytes are preserved independently. HAI keeps authoritative accepted evidence in the Activity while configured destinations contain run-specific artifacts. Human approvals use actual recorded natural-language messages and host semantic assessment bound to the current checkpoint; no cryptographic authentication is implied.

AC1-3/9/11 map to capability inventory, direct/two-role reuse and safe package migration; AC4-9/12-13 map to workflow graph, two-environment install, two-run/attempt isolation, partial-loop lineage, stale/missing approval blocks and final backlog handoff. Root integrates shared documentation and full regressions; separate reviewer checks baselines and negative scenarios.

The source workflow will not be silently installed with invented output choices. No commit, Activity closure or publication is authorized.