"""Isolated host-executed completion using the installed backlog method."""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import traceback

OUT = Path(__file__).resolve().parent
W = next(p for p in OUT.parents if (p / '.hai/tools/hai.py').is_file())
WORK = OUT / 'test-work'
os.chdir(WORK)
os.environ.update(TMP=str(WORK / 'tmp'), TEMP=str(WORK / 'tmp'), TMPDIR=str(WORK / 'tmp'))
sys.path[:0] = [str(W / '.hai/tools'), str(W / '.hai/tools/runtime/tests')]
from test_configurable_workflows import ConfigurableWorkflowTests
from runtime import skills, workflows, activities
from runtime.storage import write_bytes, fingerprint

METHOD = W / '.hai_env/skills/backlog-management'
# Method instructions/convention/maintain-items/auditor README were read by reviewer before this check.
spec = importlib.util.spec_from_file_location('independent_backlog_auditor', METHOD / 'scripts/audit_backlog.py')
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)
c = ConfigurableWorkflowTests()
c.setUp()
report = {'scenario': 'actual isolated backlog completion and evidence receipt',
          'execution': 'generic reviewer follows installed backlog-management method in assigned Backlog-manager fixture context; no model launch or live backlog mutation'}
try:
    assert c.root.resolve().is_relative_to(OUT)
    installed_skill = c.root / '.hai_env/skills/backlog-management'
    installed_skill.parent.mkdir(parents=True)
    shutil.copytree(METHOD, installed_skill)
    owner = c.root / '.hai_env/roles/backlog-manager'
    (owner / 'configuration/contract.json').write_bytes((W / '.hai_env/roles/backlog-manager/configuration/contract.json').read_bytes())
    role = owner / 'ROLE.md'
    role.write_text(role.read_text().replace('metadata:\n', 'metadata:\n  hai-skills: "backlog-management"\n'), encoding='utf-8')
    resolved = skills.handle('resolve', c.root, {'name': 'backlog-management'}, False)
    assert resolved['ok'], resolved
    assert resolved['result']['configuration']['settings']['location'] == 'backlog'
    backlog = c.root / 'backlog'
    (backlog / 'new').mkdir(parents=True)
    (backlog / 'closed').mkdir()
    stamp = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
    dash = chr(0x2014)
    pending = f"""# BL-0001 {dash} Verified fixture delivery

| Field | Value |
| --- | --- |
| ID | BL-0001 |
| Status | pending |
| Created | {stamp} |
| Updated | {stamp} |
| Closed | {dash} |
| Activities | {c.aid} |
| Source | Explicit isolated review fixture authority |

## What
Write product/result.txt containing verified fixture result, then obtain QA and human acceptance.

## Why
Verify the host-owned backlog completion contract after workflow checkpoints.

## Acceptance Criteria
- product/result.txt equals verified fixture result.
- QA and actual typed fixture human acceptance identify the current result.

## History
- {stamp} {dash} Created by explicitly authorized isolated fixture owner.
"""
    item = backlog / 'new/BL-0001.md'
    item.write_text(pending, encoding='utf-8')
    catalogue = backlog / 'catalogue.md'
    catalogue.write_text('# Fixture backlog\n\n| ID | Title | Status | File |\n| --- | --- | --- | --- |\n| BL-0001 | Verified fixture delivery | pending | [BL-0001](new/BL-0001.md) |\n', encoding='utf-8')
    initial_audit = auditor.audit(c.root)
    assert initial_audit['ok'], initial_audit
    assert c.install(c.locations)['ok']
    c.start()

    def execute(label, name, content, human=False):
        a = c.begin()
        (c.root / a['outputs'][name]['path']).write_text(content, encoding='utf-8')
        approval = c.human('Fixture human approves this current design.' if a['step_id'] == 'approve-design' else 'Fixture human accepts this current verified product result.') if human else None
        completed = c.finish(label, approval)
        assert completed['ok'], completed
        return a, completed['result']['acceptance'], approval

    execute('prepared', 'work-item', 'Selected backlog/new/BL-0001.md; explicit isolated owner authority; current scope is fixture product/result.txt.')
    execute('refined', 'requirements', 'AC: product/result.txt contains exactly verified fixture result; QA and actual typed fixture human acceptance required.')
    execute('designed', 'design', 'Write the declared fixture result file and verify its exact bytes; no publication; preserve backlog evidence.')
    execute('approved', 'approval', 'Current fixture design submitted and actual typed fixture approval retained.', True)
    a = c.begin()
    product = c.root / 'product/result.txt'
    product.parent.mkdir()
    product.write_bytes(b'verified fixture result')
    (c.root / a['outputs']['implementation']['path']).write_text('Implemented canonical fixture product/result.txt; developer exact-byte check passed.', encoding='utf-8')
    assert c.finish('implemented')['ok']
    assert product.read_bytes() == b'verified fixture result'
    _, qa, _ = execute('passed', 'verification', 'Independent reviewer exact-byte check: expected verified fixture result, observed verified fixture result; PASS. Product SHA256 ' + hashlib.sha256(product.read_bytes()).hexdigest())
    _, accepted, human = execute('accepted', 'acceptance', 'Actual typed fixture human accepts the current verified result; bound current QA and implementation identities.', True)
    completion = c.begin()
    assert completion['role'] == 'backlog-manager'
    assert completion['inputs']['qa-pass']['producer_result'] == 'passed'
    assert completion['inputs']['human-acceptance']['producer_result'] == 'accepted'
    assert item.read_text(encoding='utf-8') == pending
    assert auditor.audit(c.root)['ok']
    qa_input = completion['inputs']['qa-pass']
    acceptance_input = completion['inputs']['human-acceptance']
    run_base = workflows.run_base(c.root, c.aid, c.run_id)
    qa_path = run_base + '/' + qa_input['path']
    acceptance_path = run_base + '/' + acceptance_input['path']
    assert hashlib.sha256((c.root / qa_path).read_bytes()).hexdigest() == qa_input['artifact']['sha256']
    receipt = {'backlog_item': 'backlog/closed/BL-0001.md', 'status': 'completed',
               'activity_id': c.aid, 'run_id': c.run_id,
               'qa': {'acceptance_key': qa_input['acceptance_key'], 'path': qa_path, 'sha256': qa_input['artifact']['sha256']},
               'human_acceptance': {'acceptance_key': acceptance_input['acceptance_key'], 'path': acceptance_path,
                   'sha256': acceptance_input['artifact']['sha256'], 'message_id': human['message_id'], 'message_sha256': human['message_sha256']},
               'product': {'path': 'product/result.txt', 'sha256': hashlib.sha256(product.read_bytes()).hexdigest()},
               'authority': 'Explicit isolated fixture owner authorizes backlog completion after actual fixture human acceptance',
               'checks': 'Both authored fixture acceptance criteria verified; Activity lifecycle remains active.'}
    finished_at = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
    closed = pending.replace('| Status | pending |', '| Status | completed |').replace('| Closed | ' + dash + ' |', '| Closed | ' + finished_at + ' |').replace('| Updated | ' + stamp + ' |', '| Updated | ' + finished_at + ' |')
    closed += f"\n## Resolution\nCompleted under explicit isolated fixture owner authority. Both criteria passed; QA {qa_input['acceptance_key']} path {qa_path} SHA256 {qa_input['artifact']['sha256']}; human acceptance message {human['message_id']} hash {human['message_sha256']}. Product result verified. Activity {c.aid} remains active.\n"
    closed = closed.replace('## History\n', '## History\n- ' + finished_at + ' ' + dash + ' Authorized pending-to-completed transition after QA and actual typed fixture human acceptance.\n')
    predecessor = backlog / 'history/BL-0001/before-completion.md'
    predecessor.parent.mkdir(parents=True)
    predecessor.write_bytes(item.read_bytes())
    write_bytes(c.root, 'backlog/new/BL-0001.md', closed.encode('utf-8'), fingerprint(item))
    activities.rename_exclusive(item, backlog / 'closed/BL-0001.md')
    catalogue.write_text(catalogue.read_text().replace('| pending | [BL-0001](new/BL-0001.md)', '| completed | [BL-0001](closed/BL-0001.md)'), encoding='utf-8')
    after_audit = auditor.audit(c.root)
    assert after_audit['ok'], after_audit
    assert after_audit['items'][0]['status'] == 'completed'
    receipt_text = '# Completion receipt\n\n' + json.dumps(receipt, indent=2) + '\n'
    (c.root / completion['outputs']['completion']['path']).write_text(receipt_text, encoding='utf-8')
    final = c.finish('completed')
    assert final['ok'], final
    state = c.show()
    assert state['outcome'] == 'delivered'
    assert json.loads((c.activity / 'system/state.json').read_text())['lifecycle'] == 'active'
    accepted_receipt = final['result']['acceptance']['outputs']['completion']
    assert (c.root / run_base / accepted_receipt['path']).read_text() == receipt_text
    report.update(passed=True, method='.hai_env/skills/backlog-management/SKILL.md',
                  method_sha256=hashlib.sha256((METHOD / 'SKILL.md').read_bytes()).hexdigest(),
                  before_audit=initial_audit, after_audit=after_audit, receipt=receipt,
                  completion_acceptance=final['result']['acceptance'], outcome=state['outcome'], activity_lifecycle='active')
    (OUT / 'isolated-completion-receipt.md').write_text(receipt_text, encoding='utf-8')
    (OUT / 'isolated-completed-item.md').write_text(closed, encoding='utf-8')
except Exception:
    report.update(passed=False, exception=traceback.format_exc())
finally:
    c.doCleanups()
(OUT / 'backlog-completion-results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
raise SystemExit(0 if report.get('passed') else 1)
