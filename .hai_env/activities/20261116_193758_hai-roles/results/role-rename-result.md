# HAI roles: implemented

A HAI role is the reusable instructions an AI agent follows. AI agent continues
to mean the executing tool or running worker.

## Result

- Installed roles: .hai_env/roles/; saved settings: .hai_env/config/roles/.
- Golden source: hai_roles_library/roles/. Every HAI role starts with ROLE.md;
  actual skills retain SKILL.md. The manager is role-definition-manager.
- Runtime commands use roles and role identity fields. The neutral packages
  command remains. Legacy live agent names require explicit migration.
- Role contracts use format 3, reusable workflows format 2 with Role sections,
  and new invocation manifests format 2. Saved configuration/profile versions
  and actual executor/chat conventions retain their meanings.
- Startup reports role readiness separately. The migration previews exact inputs,
  validates candidates, retains originals and blocks mixed/partial state. It also
  supports older core2/Activity1 projects without an upgrade-order deadlock.

This workspace migration completed: 0bd5b865-72ce-4f6f-8da0-7a400bb8a490.
The marker is .hai_env/config/role-migration.json; originals are retained under
this Activity's history/role-migration/. These are deliberate recovery records.

## Preservation and checks

The independent reviewer verified 992 archived Activity files, three actual skill
files, global instructions, model profiles and two saved settings files unchanged.
All 11 installed roles remain, including the workspace-only advisor; the library
contains 10 roles. The definition manager retains the same five local differences
between installed and source copies. All original packages and workflows have
exact recovery copies. The retained finished format-1 workflow run still opens.

The core regression run passed 495 tests with 30 platform skips. Focused final
checks passed 16 migration tests and 81 role-tool tests after the last fixes.
All 12 installed/source package suites passed 308 tests with 24 OS skips using
UTF8 mode. Package fixture updates address older Activity-layout assumptions,
Windows newline translation and unavailable symlink privileges. Shared/runtime
code, configuration and workflow behavior were checked independently.

See [core output](../evidence/verification/role-rename-tests.txt) and
[package output](../evidence/verification/role-package-tests.txt). Initial failed
checks remain in verification evidence rather than being reported as passes.

## Operational state

Startup and the installed-role audit pass. Both reusable workflows validate.
Git remains enabled, automatic push remains disabled, and specification management
remains disabled. The Activity stays open; no commit or publication was performed.

Recording is incomplete: startup observed an unsupported ContextCompaction source
item; explicit synchronization also reports missing Activity source assignments.
Best-effort recording permits independent work, and received human instructions
are retained in system/chat.jsonl. No transcript coverage was invented.

For other projects, follow the [explicit migration procedure](../../../../.hai/procedures/migrate-roles.md).
