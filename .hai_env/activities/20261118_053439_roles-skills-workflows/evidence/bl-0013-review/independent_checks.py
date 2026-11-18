"""Independent integration scenarios; all writes confined to this allocation."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import traceback
from unittest import mock

OUT = Path(__file__).resolve().parent
WORKSPACE = next(p for p in OUT.parents if (p / '.hai/tools/hai.py').is_file())
WORK = OUT / 'test-work'
WORK.mkdir(exist_ok=True)
TEMP = WORK / 'tmp'
TEMP.mkdir(exist_ok=True)
os.environ.update(TMP=str(TEMP), TEMP=str(TEMP), TMPDIR=str(TEMP), PYTHONDONTWRITEBYTECODE='1')
os.chdir(WORK)
sys.path[:0] = [str(WORKSPACE / '.hai/tools'), str(WORKSPACE / '.hai/tools/runtime/tests')]
from test_configurable_workflows import ConfigurableWorkflowTests
from runtime import workflows, workflow_config, workflow_lineage
from runtime.storage import SafetyError

RESULTS = []

def scenario(name, run):
    started = time.monotonic()
    case = ConfigurableWorkflowTests()
    case.setUp()
    try:
        detail = run(case)
        result = {'scenario': name, 'passed': True, 'details': detail}
    except Exception:
        result = {'scenario': name, 'passed': False, 'error': traceback.format_exc()}
    finally:
        case.doCleanups()
    result['seconds'] = round(time.monotonic() - started, 3)
    RESULTS.append(result)
    (OUT / 'independent-check-results.json').write_text(json.dumps(RESULTS, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result), flush=True)

def scope_return(c):
    assert c.install(c.locations)['ok']
    c.start()
    trace = []
    for label, human in [('prepared', False), ('refined', False), ('designed', False),
                         ('approved', True), ('implemented', False), ('defects', False),
                         ('scope-change', False), ('refined', False), ('designed', False), ('approved', True)]:
        assignment, record = c.accepted(label, human)
        trace.append({'step': assignment['step_id'], 'execution': assignment['execution_number'], 'result': label})
    current = c.begin()
    assert current['step_id'] == 'implement'
    assert current['execution_number'] == 3
    assert current['inputs']['defects'] is None
    assert current['inputs']['requirements']['acceptance_key'] == 'clarify/attempt-0002'
    assert current['inputs']['design']['acceptance_key'] == 'design/attempt-0002'
    assert current['inputs']['design-approval']['acceptance_key'] == 'approve-design/attempt-0002'
    assert c.finish('implemented')['ok']
    c.accepted('passed')
    acceptance_assignment = c.begin()
    assert not c.finish('accepted')['ok']
    approval = c.human('I accept the renewed scope and this verified result.')
    assert c.finish('accepted', approval)['ok']
    final_assignment, final_record = c.accepted('completed')
    assert final_assignment['role'] == 'backlog-manager'
    assert final_record['inputs']['human-acceptance']['producer_result'] == 'accepted'
    assert c.show()['outcome'] == 'delivered'
    assert json.loads((c.activity / 'system/state.json').read_text())['lifecycle'] == 'active'
    return {'trace': trace, 'fresh_implementation_execution': current['execution_number'],
            'defects_after_scope_restart': None, 'final_outcome': 'delivered', 'activity': 'active'}

def env_locations(c):
    bases = {'handoffs': '.hai_env/workflow-outputs/handoffs', 'completion': '.hai_env/workflow-outputs/final'}
    result = c.install(bases)
    assert result['ok'], result
    assert not (c.activity / 'workflow-runs').exists()
    protected = ['.hai_env', '.hai_env/config', '.hai_env/roles', '.hai_env/skills', '.hai_env/workflows',
                 '.hai_env/activities', '.hai_env/config/workflows', '.hai', 'roles', 'skills', 'workflows', '../escape']
    blocked = []
    for value in protected:
        try:
            workflow_config.validate_locations(c.root, c.parsed, {'handoffs': value, 'completion': 'elsewhere'})
        except SafetyError:
            blocked.append(value)
        else:
            raise AssertionError('Unsafe location accepted: ' + value)
    return {'accepted': bases, 'blocked': blocked, 'installation_started_run': False}

def partial_install(c):
    original = workflow_config.write_json
    def fail(root, relative, *args, **kwargs):
        if relative == workflow_config.config_path('software-development'):
            raise OSError('Independent injected configuration write failure')
        return original(root, relative, *args, **kwargs)
    with mock.patch.object(workflow_config, 'write_json', side_effect=fail):
        result = c.install(c.locations)
    assert result['status'] == 'partial', result
    installed = c.root / '.hai_env/workflows/software-development.md'
    retained = installed.read_bytes()
    assert retained == c.source.read_bytes()
    started = workflows.handle('start', c.root, {'activity_id': c.aid,
        'definition': '.hai_env/workflows/software-development.md', 'provenance': c.prov}, True)
    assert not started['ok']
    retry = c.install(c.locations)
    assert not retry['ok']
    assert installed.read_bytes() == retained
    assert not (c.activity / 'workflow-runs').exists()
    return {'partial_paths': result['changed_files'], 'start_blocked': started['issues'],
            'retry_blocked': retry['issues'], 'retained_definition_sha256': hashlib.sha256(retained).hexdigest()}

def partial_multi_output(c):
    assert c.install(c.locations)['ok']; c.start(); c.approved_design(); c.accepted('implemented'); c.begin()
    before = c.show()
    base = c.root / workflows.run_base(c.root, c.aid, c.run_id)
    event_bytes = (base / 'events.jsonl').read_bytes()
    original = workflows.copy_snapshot
    copied = []
    def fail_second(root, source, destination, changed):
        if copied:
            raise SafetyError('Independent injected second accepted-output copy failure', changed)
        evidence = original(root, source, destination, changed)
        copied.append(destination)
        return evidence
    with mock.patch.object(workflows, 'copy_snapshot', side_effect=fail_second):
        result = c.finish('defects')
    assert result['status'] == 'partial', result
    assert len(copied) == 1
    assert (base / 'events.jsonl').read_bytes() == event_bytes
    shown = workflows.handle('show', c.root, {'activity_id': c.aid, 'run_id': c.run_id}, False)
    assert not shown['ok'] and 'Uncommitted' in str(shown), shown
    retried = workflows.handle('complete-step', c.root, {'activity_id': c.aid, 'run_id': c.run_id,
        'expected_revision': before['revision'], 'step_id': before['current_step'],
        'attempt_id': before['current_attempt'], 'result': 'defects', 'assessment': c.assessment,
        'executor': {**c.executor, 'writers_ended': True}, 'provenance': c.prov}, True)
    assert not retried['ok']
    assert all((c.root / row['path']).is_file() for row in c.assignment['outputs'].values())
    return {'partial_paths': result['changed_files'], 'uncommitted_copy': copied,
            'show_blocked': shown['issues'], 'retry_blocked': retried['issues'], 'configured_outputs_preserved': True}

for name, run in [('material scope return and renewed approval', scope_return),
                  ('dedicated environment output roots and protected overlap', env_locations),
                  ('partial installation preserves definition and refuses automatic retry', partial_install),
                  ('partial second output copy preserves evidence and blocks replay', partial_multi_output)]:
    scenario(name, run)

sample = {'accepted': {'x/attempt-9999': {'step_id': 'x', 'execution_number': 9999, 'attempt_id': 'attempt-9999'},
                       'x/attempt-10000': {'step_id': 'x', 'execution_number': 10000, 'attempt_id': 'attempt-10000'}}}
roundtripped = json.loads(json.dumps(sample, sort_keys=True))
key, record = workflow_lineage.latest(roundtripped, 'x')
RESULTS.append({'scenario': 'numeric accepted execution after canonical serialization',
                'passed': key == 'x/attempt-10000', 'actual_key': key})
(OUT / 'independent-check-results.json').write_text(json.dumps(RESULTS, indent=2) + '\n', encoding='utf-8')
raise SystemExit(0 if all(row['passed'] for row in RESULTS) else 1)
