# Activity-local workflow runs

The user requested that runs belong inside the current Activity without repeating
its UUID as another folder level. The runtime and current design now use:

```text
<configured-activity-store>/
  <current-or-archived-activity>/
    workflow-runs/
      <run-id>/
        definition.md
        state.json
        events.jsonl
        inputs/
        attempts/
```

Reusable definitions remain in `.hai_env/workflows/`. The runtime resolves the
owner's stable Activity ID before locating a run. Archival moves the entire
Activity, including its runs; inspection resolves the new path, and closed-owner
mutations remain prohibited. Existing run-relative artifact bindings need no rewrite.

## Existing pilot relocation

The finished pilot `e1e8a718-d108-49ea-bec5-24572793827b` moved from the old external
root into this Activity's `workflow-runs/` folder. Its seven files and complete
directory manifest match the pre-move evidence exactly. Runtime readback reports
the same `finished` state, `feasible` outcome and revision 4. All pinned definitions,
inputs, assignments, accepted result, assessment and transition events retain their
original bytes. Recorded old source paths remain historical provenance.

Migration evidence is retained under `files/workflow-storage-refactor/` as
`migration-before.json` and `migration-complete.json`. The empty old Activity-ID
parent and external root were removed without recursive deletion. There is no
remaining `.hai_env/workflow-runs/` folder in this workspace.

Other workspaces with legacy external runs require explicit relocation. The runtime
preserves and reports that evidence instead of silently ignoring it, reading an
external fallback or writing to both layouts. No automatic migration was added.

## Verification

Storage regression fixtures cover configured Activity stores, one run-ID folder
level, archived inspection with unchanged run bytes, closed-owner mutation refusal,
optional storage absence, UUID collisions and external legacy evidence refusal.
Input checks cover both Activity-relative and workspace-relative accepted outputs,
cross-Activity refusal, metadata/unaccepted-output refusal, containing-directory
rejection and predecessor content changing between verification and snapshot.

Initial focused verification exposed two test-fixture problems: an expected error
was masked by a same-Activity directory classification, and the simulated other
Activity lacked required lifecycle records. The guard and fixture were corrected;
the three affected input tests pass. Broad and independent final checks are recorded
in the completion entry below.

Independent review passed: 42 focused tests, with one unavailable Windows symlink
capability skip. The reviewer confirmed the relocated pilot's seven files and
four directories against the original manifest, unchanged runtime identity and
state, absent external root, and agreement between current code and design docs.
No remaining material finding was reported. Review evidence remains with invocation
`f0caac64-10c5-4980-9012-9fe5f61eb93a`.

Final developer regression run on Windows/Python 3.14.7:

| Suite | Result |
| --- | --- |
| runtime/tests | 230 tests successful, including 10 platform capability skips. |
| activities | 16 tests passed. |
| startup | 66 tests successful, including 8 platform capability skips. |
| configuration | 13 tests successful, including 3 platform capability skips. |

All suites returned exit code 0. Fixtures and temporary files stayed in the
Activity's `files/test-work/workflow-local-full/` area. Other platforms remain
unverified. `git diff --check` found no whitespace errors.

Maintained conventions, runtime documentation, startup instructions and the current
seven-file design package were updated. Predecessor design documents and the earlier
delivery report are preserved under `files/revisions/workflow-storage-activity-local/`.
No accepted run evidence was edited to update historical paths.

The Activity remains open. No commit or publication was requested. Chronicle
synchronization still reports the existing unsupported host `ContextCompaction`
record under best-effort policy; no missing transcript coverage is claimed.
