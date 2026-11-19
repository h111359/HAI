# Workspace role catalogue

This catalogue lists the installed optional workspace roles.
Entries follow the [state convention](../../.hai/conventions/state_conv.md).

| Role | Selection guide | Definition |
| --- | --- | --- |
| `hai-framework-advisor` | Call to review this repository's HAI framework and recommend the top three logical next actions in chat without changing files. | [ROLE.md](hai-framework-advisor/ROLE.md) |
| `release-manager` | Call to prepare a HAI bundle release, recommend an evidence-based SemVer bump, and verify release readiness and publication evidence. Returns release assets, readiness findings, publication status, and unresolved dependencies. | [ROLE.md](release-manager/ROLE.md) |
| `git-manager` | Call to configure this workspace's optional Git/GitHub integrations or inspect and operate repositories, commits, branches, merges, pushes, pull requests, issues, tags, releases, and checks. Returns validated settings, verified changes, repository and remote status, and unresolved dependencies. | [ROLE.md](git-manager/ROLE.md) |
| `specification-manager` | Call to configure HAI specification enablement and location, or enter, update, organize, or validate durable product specification information. Returns validated settings, changes, verification evidence, and unresolved decisions. | [ROLE.md](specification-manager/ROLE.md) |
| `business-analyst` | Call to clarify business intent, analyze requirements and define scope and acceptance criteria. Returns attributable requirements, decisions, ambiguities and evidence for host coordinator and the Activity record owner. | [ROLE.md](business-analyst/ROLE.md) |
| `solution-architect` | Call to analyze technical options, design a solution and plan implementation and verification against agreed requirements. Returns justified architecture, tradeoffs, dependencies, risks and an actionable plan. | [ROLE.md](solution-architect/ROLE.md) |
| `software-developer` | Call to implement authorized product changes and run appropriate developer checks against agreed requirements and technical decisions. Returns actual changes, verification evidence, failures and unresolved dependencies. | [ROLE.md](software-developer/ROLE.md) |
| `quality-assurance` | Call to verify product behavior against agreed requirements and acceptance criteria, assess regressions and report evidence-based defects and coverage limits. Returns actual test results and unresolved acceptance risks. | [ROLE.md](quality-assurance/ROLE.md) |
| `backlog-manager` | Call to configure a workspace backlog location, capture or import backlog items, maintain their catalogue, prepare an item for Activity work, and record evidence-backed completion, cancellation or rejection. Returns item paths, status changes, catalogue checks and unresolved decisions. | [ROLE.md](backlog-manager/ROLE.md) |
