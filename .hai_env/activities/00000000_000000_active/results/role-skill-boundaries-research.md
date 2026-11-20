# Roles and skills: research and application to Backlog-manager

Research date: 19 November 2026. Status: advice for review; no package refactor or new skill split is authorized by this report.

## Conclusion

A role may legitimately own conventions, procedures, templates and scripts. Skills should be independently usable capabilities; extracting them should follow coherent ownership and useful reuse. The examined evidence does not establish a rule that every procedure or script must become a skill, or that all useful skills must be domain-neutral.

For HAI, I recommend a role package containing its job definition and job-specific operating knowledge, with optional references to independent skills. Keep a concise ROLE.md and load its supporting resources when needed. A reusable role package is itself a valid unit of sharing between workspaces. Sharing a procedure across installations of one role does not automatically make it an independent skill.

My earlier six-skill proposal was a decomposition hypothesis. The research does not justify adopting it as a best practice.

## Method and limits

I used Exa to screen 85 search results from 17 searches across six workstreams: standards/product architecture, concrete GitHub implementations, empirical AI research, practitioners/social discussion, workforce design, and modularity/organizational routines. There were 79 distinct result URLs; relevant accessible material from 30 distinct source pages was examined. The source register records exact URLs, evidence types and access limits.

Technical claims rely on primary specifications, product documentation, repositories, authors' work and original research. Social comments are treated as opinions. Vendor evaluations are useful bounded observations, not independent universal proof. The HBR item was accessible only as an introduction/summary; no conclusions were inferred from its paywalled text. Published talk materials were examined without claiming to have watched the video.

I found no controlled study establishing the optimal role/skill file boundary for HAI. No HAI performance experiment was run. Findings about skill retrieval and context are relevant, but cannot determine a particular folder layout by themselves. SkillsBench's current preprint revision was kept separate from its older launch-blog figures.

## What the sources show

### Roles and skills have overlapping forms but different ownership

GitHub describes custom agents as specialist profiles with instructions and tools, and skills as task-specific instructions/resources. Its guidance also separates broadly applicable project instructions from occasional task guidance. These categories distinguish purpose and use; they do not prohibit procedural instructions inside a specialist profile. [GitHub customization comparison](https://docs.github.com/en/copilot/concepts/customizations/comparing-customizations)

A concrete counterexample to compulsory extraction is wshobson/agents. The repository distributes agents alongside skills; its backend architect profile retains domain knowledge, behavioral guidance and a ten-step response approach. This demonstrates a hybrid implementation, not proof that its long profile is optimal. [Architecture](https://github.com/wshobson/agents/blob/main/docs/architecture.md), [backend architect source](https://github.com/wshobson/agents/blob/main/plugins/backend-development/agents/backend-architect.md)

### Portable does not mean universally generic

The Agent Skills specification allows instructions, scripts, reference material and assets, with documented environmental dependencies. It defines a packaging contract rather than a universal architecture for roles. [Specification](https://agentskills.io/specification)

Anthropic publishes both internal-communications and its own brand-guidelines skills. These are specific to a business practice or organization while still being reusable packages. Domain specialization is compatible with reuse. HAI can deliberately require its shared skills to work without HAI; that does not require removing all useful domain knowledge. [Internal communications](https://github.com/anthropics/skills/blob/main/skills/internal-comms/SKILL.md), [brand guidelines](https://github.com/anthropics/skills/blob/main/skills/brand-guidelines/SKILL.md)

Zhang and Murag's published talk materials advocate a general agent/runtime equipped with procedural expertise. This supports portable expertise without rebuilding execution infrastructure for every domain. It does not establish that every job-specific procedure needs independent discovery as a skill. [AI Engineer talk materials](https://ai.engineer/talks/CEvIs9y1uog-agent-skills)

### Working designs differ

Jesse Vincent's Superpowers organizes a software-development methodology around composable skills and bootstrap instructions. That is a skill-centered design; wshobson's specialist profiles are a different design. Their coexistence argues against treating either layout as a universal prescription. [Superpowers](https://github.com/obra/superpowers)

Simon Willison's firsthand experiments emphasize ordinary files, optional executable helpers and selective loading. O'Reilly's interview with Vincent discusses both process discipline and ongoing jobs. These are practical design perspectives, with no controlled comparison of a thin role versus a richer role package. [Willison](https://simonwillison.net/2025/Oct/16/claude-skills/), [O'Reilly interview](https://www.oreilly.com/radar/superpowers-for-humans/)

### Granularity and activation have measurable costs

Robert Xu reports that LangChain sometimes selected the wrong skill among roughly 20 similar skills and selected consistently after consolidation to 12 in that setup. The lesson is to test overlap and selection; twelve is not a recommended global count. [LangChain evaluation](https://www.langchain.com/blog/evaluating-skills)

Jude Gao's Vercel evaluation found 100% on its Next.js suite with a compact always-available documentation index, versus 79% with explicitly prompted skill use. This does not prove skills are inferior generally. It warns against making essential context depend on optional activation. [Vercel evaluation](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)

SkillsBench reports gains from curated procedural skills and weaker results from oversized/exhaustive bundles. Its current arXiv version is a preprint, and its authors acknowledge incomplete causal controls. It supplies evidence for evaluation and focused content, not a universal number of skill packages. [SkillsBench](https://arxiv.org/abs/2602.12670)

### Clarity and verification matter more than a persona label

The peer-reviewed MAST work analyzes failures in multi-agent systems and groups them into system design, inter-agent misalignment and verification problems. It does not directly evaluate HAI's role/skill split. Its relevance is the need to test responsibilities, information handoffs and verification instead of relying on labels. [NeurIPS paper](https://proceedings.nips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html)

The public Hacker News discussion explicitly disagrees about whether skills and subagents overlap confusingly. Willison argues they are complementary. These comments are useful usability signals; they are not representative performance data. Logical role ownership and separate execution/context windows are different decisions. [Discussion](https://news.ycombinator.com/item?id=45615271), [Willison's explanation](https://news.ycombinator.com/item?id=45622765)

## The real-company analogy

O*NET separates worker skills/knowledge from job tasks and occupational context. NIST NICE defines work roles through responsibility and associated tasks, knowledge and skills; a work role is not necessarily an entire job. CIPD role design combines impact, core behavior/knowledge and specialist requirements. These frameworks support several related dimensions rather than reducing a job to a list of skills. [O*NET](https://www.onetcenter.org/content.html), [NIST NICE](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/resources/occupations-jobs-and-work), [CIPD role design](https://www.cipd.org/en/the-people-profession/the-profession-map/how-it-works/role-design/)

Illustrative analogy, not a researched company case:

| Company element | Meaning | HAI analogue |
| --- | --- | --- |
| Finance manager's job | Accountability, decision authority, standards and escalation | Role definition |
| Department's month-end manual | Job-specific procedures and local rules | Role-owned procedures/conventions |
| Reconciliation expertise/toolkit | A capability usable by several professionals | Independent skill |
| Company-wide financial policy | Rules with a shared organizational owner | Shared project/core convention |
| Month-end approval process | Ordered handoffs between people | Workflow |

A human skill is an ability, not a directory. An AI skill package is closer to a reusable practice guide/toolkit that supplies procedural knowledge. This limits the analogy: copying a taxonomy of human skills directly into software packages can produce the wrong granularity.

Jesuthasan and Boudreau advocate decomposing jobs where it opens useful staffing and automation options. That is a positive case for selective decomposition, not compulsory atomization. [MIT Sloan Management Review](https://sloanreview.mit.edu/article/cant-fill-jobs-deconstruct-them/)

Pentland and Feldman's peer-reviewed work warns that designing documents, forms and software is not the same as producing the desired organizational routine. Their qualitative example is not an AI benchmark, but it reinforces testing actual patterns of work rather than counting well-organized files. [Designing routines](https://socialecology.uci.edu/sites/socialecology.uci.edu/files/users/feldmanm/Pentland_and_Feldman_2008_-_Information_and_Organization.pdf)

## Practical ownership rule

Place each resource with the responsibility or capability whose contract it implements and whose changes it follows. A filename such as convention, procedure or script does not decide ownership.

| Content | Recommended home |
| --- | --- |
| Role responsibility, decisions, authority, escalation and job-specific conduct | Role |
| A procedure or helper meaningful only within that job and its data model | Role supporting resources |
| A capability with a useful independent invocation and clear contract | Skill, including its own necessary procedures/conventions/scripts |
| Rules applicable across several roles and skills | One shared core/project owner, referenced rather than copied |
| Cross-role sequencing and handoff/approval conditions | Workflow |
| Environment lifecycle, recording and common enforced runtime behavior | HAI core |

Parnas's classic modularity argument groups difficult or changeable design decisions rather than merely turning processing steps into modules. Applying that principle to HAI is my architectural inference: keep shared invariants together and extract at stable boundaries. It is not experimental evidence about LLM skills. [Parnas, 1972](https://dl.acm.org/doi/pdf/10.1145/361598.361623)

A script may simply remain a script. Skill packaging is useful when an agent needs a separately discoverable capability with its own instructions. A shared code function does not automatically need another SKILL.md.

## Application to the actual Backlog-manager package

Local inspection found the following:

- The role owns backlog settings and evidence-based terminal decisions, but most methods were moved into backlog-management.
- The skill declares hai-settings-owner and reads an installed role contract/settings.
- audit_backlog.py discovers .hai/tools at import time, reads backlog-manager configuration and consults specification-manager location assurance. Even an explicit --location does not remove those dependencies.
- The format fixes IDs, status folders, item sections and catalogue rules. Import and Activity-handoff procedures depend on that same model.
- The role still refers to the older Activity files/ audit destination. A future authorized refactor should resolve the current evidence destination, rather than copy that literal path into an independent skill.

These are facts about current coupling, not evidence that all these methods belong in separate skills. The current HAI role convention already permits genuinely role-local procedures and supporting scripts; a mandatory thin-role interpretation is stronger than the framework's written rule.

My provisional recommendation is to treat Backlog-manager as a complete job package, with its backlog model, job-specific operations and HAI integration. Do not retain a compulsory mirrored skill merely to house the methods removed from that job.

| Existing responsibility/resource | Provisional treatment |
| --- | --- |
| Configuration and location selection | Role procedure using core configuration tools |
| Backlog field/ID/status model | One backlog-owned convention; initially in the role package |
| Import into this exact backlog and preserve its evidence | Role procedure |
| Completion/rejection/reopening and catalogue consistency | Cohesive backlog operations under one owner |
| Prepare and record HAI Activity linkage | Role procedure using core runtime |
| Auditor tied to the backlog schema and HAI settings | Role helper; separate pure checks from integration only if a real independent use justifies it |
| General document extraction, normalization or another already useful external capability | Optional independent skill, called with explicit inputs |

The dangerous split is item writing in one generic skill, index updating in another, and history in a third while all share one backlog invariant. That increases coordination and partial-failure handling. Conversely, a genuine standalone Markdown-backlog toolkit could be a useful domain-specific skill if it carries a coherent contract and does not require HAI. These are alternative ownership choices; we should select one, not duplicate both implementations.

## Usability, scale and maintainability

- Usability: prefer task names a user and model can distinguish. A short ROLE.md can navigate role-owned methods on demand; moving files into skills is not the only way to reduce loaded context.
- Scale: optimize selection accuracy, explicit prerequisites and stable interfaces. More packages create more descriptions, dependencies and compatibility work.
- Reliability: keep essential authority and acceptance rules in reliably loaded instructions and enforceable tools where applicable. An optional skill or a role label alone is not an access-control mechanism.
- Maintenance: give each format/invariant one owner. Parameterize meaningful variation; avoid replacing domain expertise with a large generic configuration language.
- Evidence: measure task outcomes and recovery, not only validator success. Anthropic recommends concise, specific descriptions and evaluation-led iteration; its context guidance warns against both brittle detail and vague instructions. [Authoring guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [context guidance](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)

## Decision test before extracting a skill

Treat these as practical heuristics, not external standard requirements:

1. Can a caller describe a useful independent outcome without selecting Backlog-manager?
2. Can the method receive sufficient explicit inputs and return understandable outputs without reading HAI internals?
3. Can its owner change it without coordinated changes across the entire backlog lifecycle?
4. Is there a credible independent use that justifies separate discovery, testing and dependency management?
5. Does evaluation show better reuse, clarity or reliability than keeping the method with the role?

One current consumer does not disqualify a useful standalone skill. Conversely, reuse across workspaces of the same job does not automatically justify extraction.

Before choosing packages, compare the current setup, a cohesive role-owned setup and a small extracted-capability setup on real import, duplicate/conflict, revision, accepted closure, audit and handoff tasks. Check meaning preservation, authorization, record/catalogue consistency, interruption recovery, correct method selection, time/tokens and reviewer understanding. Do not implement a six-skill taxonomy before this comparison.

## Relevant expert voices

- Barry Zhang and Mahesh Murag: skill creators/presenters; reusable procedural expertise and separation from custom runtimes. Their talk is architecture advocacy, not a controlled ownership experiment.
- Simon Willison: firsthand demonstrations and practical explanation of lightweight skill packages.
- Jesse Vincent: Superpowers maintainer; a skill-centered methodology with explicit process guidance.
- Robert Xu and Jude Gao: concrete LangChain/Vercel evaluation lessons about granularity and activation.
- David Parnas: foundational modular decomposition principles.
- Martha Feldman and Brian Pentland: organizational routines and the limits of designing artifacts alone.
- Ravin Jesuthasan, John Boudreau and Andy Lancaster: workforce/job design and the distinction between roles, tasks and capabilities.

These are selected relevant authorities and practitioners, not a claimed global ranking of experts.

## Evidence register

The [source evidence](../evidence/role-skill-research-sources.json) lists all screened URLs, the six workstreams, all examined sources and access limits. Public social posts were used as qualitative evidence only. No source code, role, skill, runtime configuration or workflow was changed for this research.

### Examined source pages

1. [Specification](https://agentskills.io/specification) — Official/product guidance. Relevant accessible sections; no claim of exhaustive full-document reading.
2. [Create custom subagents](https://code.claude.com/docs/en/sub-agents) — Official/product guidance. Relevant accessible sections; no claim of exhaustive full-document reading.
3. [Comparing Copilot customization features](https://docs.github.com/en/copilot/concepts/customizations/comparing-customizations) — Official product guidance. Relevant accessible sections; no claim of exhaustive full-document reading.
4. [Equipping agents with Agent Skills \ Anthropic](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills) — Official/product guidance. Relevant accessible sections; no claim of exhaustive full-document reading.
5. [Evaluating Skills](https://www.langchain.com/blog/evaluating-skills) — Vendor-run evaluation; scope-specific, not independent validation. Relevant accessible sections; no claim of exhaustive full-document reading.
6. [skills/internal-comms/SKILL.md](https://github.com/anthropics/skills/blob/main/skills/internal-comms/SKILL.md) — Primary implementation. Relevant accessible sections; no claim of exhaustive full-document reading.
7. [skills/brand-guidelines/SKILL.md](https://github.com/anthropics/skills/blob/main/skills/brand-guidelines/SKILL.md) — Primary implementation. Relevant accessible sections; no claim of exhaustive full-document reading.
8. [obra/superpowers](https://github.com/obra/superpowers) — Primary implementation. Relevant accessible sections; no claim of exhaustive full-document reading.
9. [Claude Skills are awesome, maybe a bigger deal than MCP](https://simonwillison.net/2025/Oct/16/claude-skills/) — First-hand practitioner. Relevant accessible sections; no claim of exhaustive full-document reading.
10. [Superpowers for Humans – O’Reilly](https://www.oreilly.com/radar/superpowers-for-humans/) — Expert interview / professional publication. Relevant accessible sections; no claim of exhaustive full-document reading.
11. [The O*NET® Content Model at O*NET Resource Center](https://www.onetcenter.org/content.html) — Workforce/organization professional framework. Relevant accessible sections; no claim of exhaustive full-document reading.
12. [Occupations, Jobs, and Work Roles — NIST](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/resources/occupations-jobs-and-work) — Workforce/organization professional framework. Relevant accessible sections; no claim of exhaustive full-document reading.
13. [How to use the Profession Map for role design](https://www.cipd.org/en/the-people-profession/the-profession-map/how-it-works/role-design/) — Workforce/organization professional framework. Relevant accessible sections; no claim of exhaustive full-document reading.
14. [Analysis — How L&D can create value: Focusing on skills development](https://www.cipd.org/en/views-and-insights/thought-leadership/insight/learning-value-skills-development/) — Workforce/organization professional framework. Relevant accessible sections; no claim of exhaustive full-document reading.
15. [Can’t Fill Jobs? Deconstruct Them](https://sloanreview.mit.edu/article/cant-fill-jobs-deconstruct-them/) — Management publication. Relevant accessible sections; no claim of exhaustive full-document reading.
16. [Designing routines: On the folly of designing artifacts, while hoping for patterns of action](https://socialecology.uci.edu/sites/socialecology.uci.edu/files/users/feldmanm/Pentland_and_Feldman_2008_-_Information_and_Organization.pdf) — Peer-reviewed research / conceptual or qualitative evidence. Relevant accessible sections; no claim of exhaustive full-document reading.
17. [SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks](https://arxiv.org/abs/2602.12670) — Research preprint. Relevant accessible sections; no claim of exhaustive full-document reading.
18. [Why Do Multi-Agent LLM Systems Fail?](https://proceedings.nips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html) — Peer-reviewed conference paper. Publisher abstract; used only for reported dataset and failure categories.
19. [On the criteria to be used in decomposing systems into modules](https://dl.acm.org/doi/pdf/10.1145/361598.361623) — Peer-reviewed research / conceptual or qualitative evidence. Relevant accessible sections; no claim of exhaustive full-document reading.
20. [How is it different from subagents? — Hacker News](https://news.ycombinator.com/item?id=45622765) — Community opinion. Relevant accessible sections; no claim of exhaustive full-document reading.
21. [This is interesting, and I think there are use cases where this feature may make... — Hacker News](https://news.ycombinator.com/item?id=45615271) — Community opinion. Relevant accessible sections; no claim of exhaustive full-document reading.
22. [AGENTS.md outperforms skills in our agent evals](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) — Vendor-run evaluation; scope-specific, not independent validation. Relevant accessible sections; no claim of exhaustive full-document reading.
23. [Building effective AI agents \ Anthropic](https://www.anthropic.com/research/building-effective-agents) — Official/product guidance. Relevant accessible sections; no claim of exhaustive full-document reading.
24. [docs/architecture.md](https://github.com/wshobson/agents/blob/main/docs/architecture.md) — Primary implementation. Relevant accessible sections; no claim of exhaustive full-document reading.
25. [How Deconstructing Jobs Can Change Your Organization](https://hbr.org/2025/01/how-deconstructing-jobs-can-change-your-organization) — Management publication. Accessible introduction/summary only; no paywall bypass.
26. [plugins/backend-development/agents/backend-architect.md](https://github.com/wshobson/agents/blob/main/plugins/backend-development/agents/backend-architect.md) — Primary implementation. Relevant accessible sections; no claim of exhaustive full-document reading.
27. [Effective context engineering for AI agents \ Anthropic](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) — Official/product guidance. Relevant accessible sections; no claim of exhaustive full-document reading.
28. [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — Official/product guidance. Relevant accessible sections; no claim of exhaustive full-document reading.
29. [Let me pitch you Skills, something I’ve been working on with Mahesh Murag and Keith Lazuka the past few months: — Barry Zhang](https://www.linkedin.com/posts/barry-z_let-me-pitch-you-skills-something-ive-been-activity-7384630968948563968-novo) — Creator social post / promotional opinion. Relevant accessible sections; no claim of exhaustive full-document reading.
30. [Don't Build Agents, Build Skills Instead](https://ai.engineer/talks/CEvIs9y1uog-agent-skills) — Conference talk materials / presenter-summary evidence. Published talk materials; no claim to have watched the video.
