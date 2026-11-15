"""Real workflow run transitions, evidence and bounded filesystem fixtures."""
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

TOOLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS))
from runtime import activities, workflows
from runtime.storage import SafetyError

DEFINITION = '''---
workflow_format: 1
name: sample
revision: 1
entry: first
max_step_attempts: 3
max_run_attempts: 6
---
# Sample

## Purpose
Exercise explicit handoffs and return paths.

## Inputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| request | activity:input.md | text | Fixture request. |

## Outcomes
| Name | Meaning |
| --- | --- |
| delivered | Work complete. |

## Steps
### first
#### Agent
worker
#### Instruction
Read request and produce the chosen evidence.
#### Inputs
| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| request | workflow:request | yes | text | Original request. |
| feedback | incoming:feedback | no | text | Return questions when present. |
#### Outputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| output | attempt:output.bin | arbitrary binary | Actual chosen bytes. |
#### Results
| Name | When | Outputs | Next |
| --- | --- | --- | --- |
| supplied | Binary evidence exists. | output | step:second |

### second
#### Agent
worker
#### Instruction
Check input and finish or return explicit questions.
#### Inputs
| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| previous | incoming:output | yes | arbitrary binary | First output. |
#### Outputs
| Name | Location | Format | Expectation |
| --- | --- | --- | --- |
| final | attempt:final.data | arbitrary binary | Verified bytes or authored empty content. |
| feedback | attempt:feedback.txt | text | Exact questions. |
#### Results
| Name | When | Outputs | Next |
| --- | --- | --- | --- |
| accepted | Checks support delivery. | final | end:delivered |
| reconsider | Questions need another attempt. | feedback | step:first |
'''


class WorkflowRunTests(unittest.TestCase):
    def setUp(self):
        # Caller/test runner owns cwd and redirects all temporary material inside workspace.
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / '.hai_env/config').mkdir(parents=True)
        (self.root / '.hai/templates').mkdir(parents=True)
        shutil.copy(TOOLS.parent / 'templates/state.json', self.root / '.hai/templates/state.json')
        (self.root / '.hai_env/config/agent_instructions.md').write_bytes(b'')
        (self.root / '.hai_env/config/state.json').write_text(json.dumps({'state_format_version': 3,
            'activities': {'location': '.hai_env/activities'},
            'features': {'chronicles': {'enabled': False, 'record_every_prompts': 5}}}), encoding='utf-8')
        self.prov = {'source': 'explicit fixture assignment', 'reason': 'verify workflow behavior'}
        result = activities.handle('create', self.root, {'layout_version': 1, 'initial_input': 'Original request', 'provenance': self.prov}, True)
        self.assertTrue(result['ok'], result)
        self.aid = result['result']['state']['activity_id']
        self.activity = self.root / result['result']['path']
        self.defdir = self.root / '.hai_env/workflows'; self.defdir.mkdir()
        self.defpath = self.defdir / 'sample.md'; self.defpath.write_text(DEFINITION, encoding='utf-8')
        package = self.root / '.hai_env/agents/worker'
        (package / 'configuration').mkdir(parents=True); (package / 'procedures').mkdir()
        (package / 'configuration/contract.json').write_text(json.dumps({'contract_format_version': 1,
            'agent': 'worker', 'current_config_format_version': 1, 'supported_config_format_versions': [1], 'settings': {}}), encoding='utf-8')
        (package / 'SKILL.md').write_text('''---
name: worker
description: "Perform fixture work."
metadata:
  hai-configuration-contract: "configuration/contract.json"
  hai-model-class: "standard"
  hai-reasoning-effort: "high"
---
## Purpose
Perform fixture work.
## Scope
Execute the supplied assignment.
## Out of Scope
Unrelated work.
## Rules
None.
## Procedures
| Procedure | Trigger | File |
| --- | --- | --- |
| Work | Fixture work is requested. | [Work](procedures/work.md) |
## References
None.
''', encoding='utf-8')
        (package / 'procedures/work.md').write_text('''# Work
## Description
Perform the supplied fixture work.
## Inputs
| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
## Prerequisites
None.
## Rules
None.
## Steps
1. Perform supplied work.
## Outputs
| Output | Meaning | Completion criteria |
| --- | --- | --- |
## References
None.
''', encoding='utf-8')
        (self.root / '.hai_env/agents/catalogue.md').write_text('# Agents\n\n| Agent | Selection guide | Definition |\n| --- | --- | --- |\n| `worker` | Perform fixture work. | [SKILL.md](worker/SKILL.md) |\n', encoding='utf-8')
        (self.root / '.hai_env/config/model_profiles.json').write_text(json.dumps({'format_version': 1,
            'models': dict.fromkeys(['light', 'standard', 'advanced'], 'fixture-model')}), encoding='utf-8')
        self.ready = {'runtime': {'models': {'fixture-model': ['high']}}, 'authority': 'explicit fixture user request',
                      'prerequisite_assessment': {'accepted': True, 'author': 'fixture host', 'evidence': 'Required fixture tools and scope verified'}}
        self.assessment = {'accepted': True, 'author': 'fixture host', 'evidence': 'Actual fixture output checked against declared expectation'}
        self.executor = {'handle': 'fixture-live-handle', 'mode': 'direct', 'writers_ended': False, 'evidence': 'Observed fixture worker'}
        self.run_id = None

    def call(self, op, apply=True, **kw):
        request = {'activity_id': self.aid, 'provenance': self.prov}
        if self.run_id:
            request['run_id'] = self.run_id
        request.update(kw)
        return workflows.handle(op, self.root, request, apply)

    def start(self, apply=True):
        r = workflows.handle('start', self.root, {'activity_id': self.aid,
            'definition': '.hai_env/workflows/sample.md', 'provenance': self.prov}, apply)
        self.assertTrue(r['ok'], r)
        if apply:
            self.run_id = r['result']['state']['run_id']
        return r

    def show(self):
        r = workflows.handle('show', self.root, {'activity_id': self.aid, 'run_id': self.run_id}, False)
        self.assertTrue(r['ok'], r)
        return r['result']['state']

    def mutation(self, op, **kw):
        state = self.show()
        return self.call(op, expected_revision=state['revision'], **kw)

    def prepare(self):
        r = self.mutation('prepare-step', **self.ready)
        self.assertTrue(r['ok'], r)
        return r

    def running(self):
        state = self.show()
        r = self.mutation('record-execution', step_id=state['current_step'], attempt_id=state['current_attempt'],
                          status='running', executor=self.executor, details='Actual fixture execution started')
        self.assertTrue(r['ok'], r)
        return r

    def output(self, name, raw=b'\x00\xff evidence'):
        state = self.show()
        path = self.root / workflows.run_base(self.root, self.aid, self.run_id) / 'attempts' / state['current_step'] / state['current_attempt'] / name
        path.write_bytes(raw)
        return path

    def finish(self, result):
        state = self.show()
        return self.mutation('complete-step', step_id=state['current_step'], attempt_id=state['current_attempt'],
            result=result, assessment=self.assessment, executor={**self.executor, 'writers_ended': True})

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def test_preview_has_no_side_effects_and_input_snapshot_is_exact(self):
        before = self.snapshot(); self.start(False); self.assertEqual(before, self.snapshot())
        self.start(); state = self.show()
        copied = self.root / workflows.run_base(self.root, self.aid, self.run_id) / state['inputs']['request']['path']
        self.assertEqual(copied.read_bytes(), (self.activity / 'input.md').read_bytes())
        (self.activity / 'input.md').write_text('Later changed original', encoding='utf-8')
        self.assertNotEqual(copied.read_bytes(), (self.activity / 'input.md').read_bytes())

    def test_binary_handoff_terminal_result_and_activity_stays_open(self):
        self.start(); self.prepare(); self.running(); self.output('output.bin')
        self.assertTrue(self.finish('supplied')['ok'])
        self.prepare(); state = self.show()
        assignment = read_assignment(self.root, self.aid, self.run_id, state)
        self.assertIn('first/attempt-0001/output.bin', assignment['inputs']['previous']['path'])
        self.running(); self.output('final.data', b'')
        r = self.finish('accepted'); self.assertTrue(r['ok'], r)
        self.assertEqual(self.show()['outcome'], 'delivered')
        self.assertEqual(json.loads((self.activity / 'state.json').read_text())['lifecycle'], 'active')
        workflows.assert_activity_closable(self.root, self.aid)

    def test_missing_result_file_rejects_and_corrected_output_can_complete(self):
        self.start(); self.prepare(); self.running()
        r = self.finish('supplied'); self.assertFalse(r['ok'], r)
        self.assertEqual(self.show()['status'], 'blocked')
        self.output('output.bin'); self.assertTrue(self.finish('supplied')['ok'])

    def test_existing_output_rejected_by_host_assessment_can_be_corrected_same_attempt(self):
        self.start(); self.prepare(); self.running(); output = self.output('output.bin', b'Unverified placeholder')
        initial = self.show()
        rejected_assessment = {**self.assessment, 'accepted': False,
            'evidence': 'Output bytes are a placeholder and do not meet the authored expectation for actual chosen evidence'}
        r = self.mutation('complete-step', step_id='first', attempt_id=initial['current_attempt'],
            result='supplied', assessment=rejected_assessment, executor={**self.executor, 'writers_ended': True})
        self.assertFalse(r['ok'], r)
        state = self.show()
        self.assertEqual(state['status'], 'blocked'); self.assertEqual(state['current_step'], 'first')
        self.assertEqual(state['current_attempt'], initial['current_attempt']); self.assertEqual(state['attempt_count'], 1)
        self.assertEqual(state['accepted'], {}); self.assertIsNone(state['last_accepted'])
        self.assertTrue(output.exists())
        base = self.root / workflows.run_base(self.root, self.aid, self.run_id)
        rejections = list((base / 'attempts/first' / initial['current_attempt']).glob('rejection-*.json'))
        self.assertEqual(len(rejections), 1)
        record = json.loads(rejections[0].read_text())
        self.assertEqual(record['assessment'], rejected_assessment)
        self.assertIn('accepted:true', record['reason'])
        self.assertIn('placeholder', record['assessment']['evidence'])
        output.write_bytes(b'Actual chosen evidence verified by host')
        self.assertTrue(self.finish('supplied')['ok'])
        state = self.show()
        self.assertEqual(state['current_step'], 'second'); self.assertEqual(state['attempt_count'], 1)
        self.assertIn('first/' + initial['current_attempt'], state['accepted'])

    def test_exact_replay_before_stale_revision_and_conflicting_result(self):
        self.start(); self.prepare(); self.running(); self.output('output.bin')
        state = self.show(); self.assertTrue(self.finish('supplied')['ok'])
        request = dict(step_id='first', attempt_id='attempt-0001', expected_revision=state['revision'],
            result='supplied', assessment=self.assessment, executor={**self.executor, 'writers_ended': True})
        before = self.snapshot(); r = self.call('complete-step', **request)
        self.assertTrue(r['ok'], r); self.assertTrue(r['result']['replayed']); self.assertEqual(before, self.snapshot())
        request['assessment'] = {**self.assessment, 'evidence': 'changed assertion'}
        self.assertFalse(self.call('complete-step', **request)['ok'])

    def test_multiple_runs_prepare_slot_and_pause_release(self):
        self.start(); first = self.run_id; self.prepare()
        self.start(); second = self.run_id
        self.assertFalse(self.mutation('prepare-step', **self.ready)['ok'])
        self.run_id = first; self.assertTrue(self.mutation('pause')['ok'])
        self.run_id = second; self.prepare()
        self.run_id = first; self.assertFalse(self.mutation('resume', **self.ready)['ok'])

    def test_prepare_replay_does_not_allocate_again(self):
        self.start(); self.prepare(); before = self.snapshot(); r = self.prepare()
        self.assertTrue(r['result']['replayed']); self.assertEqual(before, self.snapshot())
        self.assertEqual(self.show()['attempt_count'], 1)

    def test_orphan_attempt_directory_is_preserved_and_blocks_preview_and_apply(self):
        self.start()
        destination = self.root / workflows.run_base(self.root, self.aid, self.run_id) / 'attempts/first/attempt-0001'
        destination.mkdir(parents=True)
        for content in (None, b'Unexplained partial worker output'):
            with self.subTest(content=content):
                if content is not None:
                    (destination / 'output.bin').write_bytes(content)
                before = self.snapshot()
                before_directories = {p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_dir()}
                for apply in (False, True):
                    r = self.call('prepare-step', apply=apply, expected_revision=self.show()['revision'], **self.ready)
                    self.assertFalse(r['ok'], r)
                    self.assertIn('destination already exists', str(r['issues']))
                    self.assertEqual(before, self.snapshot())
                    self.assertEqual(before_directories, {p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_dir()})
                    self.assertEqual(self.show()['attempt_count'], 0)

    def test_colliding_run_uuid_preserves_existing_destination(self):
        import uuid
        collision = 'f5c87486-c1f4-454c-821c-9903ff197b5f'
        destination = self.root / workflows.run_base(self.root, self.aid, collision)
        destination.mkdir(parents=True); (destination / 'partial.bin').write_bytes(b'Partial prior creation')
        before = self.snapshot()
        for apply in (False, True):
            with mock.patch.object(workflows.uuid, 'uuid4', return_value=uuid.UUID(collision)):
                r = workflows.handle('start', self.root, {'activity_id': self.aid,
                    'definition': '.hai_env/workflows/sample.md', 'provenance': self.prov}, apply)
            self.assertFalse(r['ok'], r)
            self.assertIn('destination already exists', str(r['issues']))
            self.assertEqual(before, self.snapshot())

    def test_cancel_requires_actual_stopped_writer_and_does_not_undo_output(self):
        self.start(); self.prepare(); self.running(); output = self.output('output.bin')
        r = self.mutation('cancel', executor=self.executor); self.assertTrue(r['ok'], r)
        self.assertEqual(self.show()['status'], 'cancelling')
        r = self.mutation('cancel', executor={**self.executor, 'writers_ended': True}); self.assertTrue(r['ok'], r)
        self.assertEqual(self.show()['status'], 'cancelled'); self.assertTrue(output.exists())

    def test_loop_attempts_are_distinct_and_limit_blocks_dispatch(self):
        self.defpath.write_text(DEFINITION.replace('max_step_attempts: 3', 'max_step_attempts: 1'), encoding='utf-8')
        self.start(); self.prepare(); self.running(); old = self.output('output.bin')
        self.assertTrue(self.finish('supplied')['ok']); self.prepare(); self.running(); self.output('feedback.txt', b'Reconsider')
        self.assertTrue(self.finish('reconsider')['ok']); r = self.prepare()
        self.assertEqual(r['result']['state']['block_reason'], 'attempt-limit')
        self.assertEqual(r['result']['state']['reached_limits'], ['max_step_attempts:first'])
        self.assertEqual(old.read_bytes(), b'\x00\xff evidence')
        self.assertEqual(self.show()['attempt_count'], 2)

    def test_total_attempt_limit_identifies_run_limit_independently(self):
        self.defpath.write_text(DEFINITION.replace('max_run_attempts: 6', 'max_run_attempts: 1'), encoding='utf-8')
        self.start(); self.prepare(); self.running(); self.output('output.bin')
        self.assertTrue(self.finish('supplied')['ok'])
        r = self.prepare()
        self.assertEqual(r['result']['state']['block_reason'], 'attempt-limit')
        self.assertEqual(r['result']['state']['reached_limits'], ['max_run_attempts'])
        self.assertEqual(self.show()['attempt_count'], 1)

    def test_changed_predecessor_or_recorded_artifact_blocks(self):
        self.start(); self.prepare(); self.running(); output = self.output('output.bin')
        self.assertTrue(self.finish('supplied')['ok']); output.write_bytes(b'tampered')
        r = workflows.handle('show', self.root, {'activity_id': self.aid, 'run_id': self.run_id}, False)
        self.assertFalse(r['ok']); self.assertIn('artifact changed', str(r['issues']))

    def test_stale_expected_revision_makes_no_changes(self):
        self.start(); before = self.snapshot()
        r = self.call('prepare-step', expected_revision=0, **self.ready)
        self.assertFalse(r['ok']); self.assertEqual(before, self.snapshot())

    def test_edited_definition_does_not_change_existing_run(self):
        self.start(); self.defpath.write_text(DEFINITION.replace('entry: first', 'entry: second'), encoding='utf-8')
        self.assertEqual(self.show()['current_step'], 'first'); self.prepare()

    def test_projection_behind_committed_event_is_recovered_read_only(self):
        self.start(); path = self.root / workflows.run_base(self.root, self.aid, self.run_id) / 'state.json'; old = path.read_bytes()
        self.prepare(); path.write_bytes(old); before = self.snapshot()
        r = workflows.handle('show', self.root, {'activity_id': self.aid, 'run_id': self.run_id}, False)
        self.assertTrue(r['ok'], r); self.assertTrue(r['result']['projection_stale']); self.assertEqual(before, self.snapshot())
        self.assertEqual(r['result']['state']['status'], 'prepared')

    def test_partial_history_and_orphan_result_are_not_repaired_implicitly(self):
        self.start(); self.prepare(); base = self.root / workflows.run_base(self.root, self.aid, self.run_id)
        path = base / 'attempts/first/attempt-0001/result.json'; path.write_text('{}', encoding='utf-8')
        r = workflows.handle('show', self.root, {'activity_id': self.aid, 'run_id': self.run_id}, False)
        self.assertFalse(r['ok']); self.assertTrue(path.exists())
        path.unlink(); events = base / 'events.jsonl'; events.write_bytes(events.read_bytes() + b'{')
        self.assertFalse(workflows.handle('show', self.root, {'activity_id': self.aid, 'run_id': self.run_id}, False)['ok'])

    def test_closure_gate_rejects_unfinished_and_accepts_cancelled(self):
        self.start()
        with self.assertRaises(SafetyError): workflows.assert_activity_closable(self.root, self.aid)
        self.assertTrue(self.mutation('cancel')['ok']); workflows.assert_activity_closable(self.root, self.aid)

    def test_arbitrary_directory_and_empty_artifact_formats(self):
        self.defpath.write_text(DEFINITION.replace('attempt:output.bin', 'attempt:dataset').replace('arbitrary binary', 'directory dataset'), encoding='utf-8')
        self.start(); self.prepare(); self.running(); path = self.output('scratch.tmp')
        path.unlink(); folder = path.parent / 'dataset'; folder.mkdir(); (folder / 'empty').mkdir(); (folder / 'image.png').write_bytes(b'\x89PNG\x00')
        (folder / 'result.json').write_bytes(b'{}'); (folder / 'assignment.json').write_bytes(b'{}')
        self.assertTrue(self.finish('supplied')['ok']); self.prepare()

    def test_ready_after_handoff_can_pause_without_previous_executor(self):
        self.start(); self.prepare(); self.running(); self.output('output.bin')
        self.assertTrue(self.finish('supplied')['ok'])
        self.assertIsNone(self.show()['executor'])
        self.assertTrue(self.mutation('pause')['ok'])
        self.assertTrue(self.mutation('resume')['ok'])
        self.assertTrue(self.mutation('cancel')['ok'])

    def test_read_validate_allows_unregistered_contained_definition_only(self):
        target = self.root / 'sample.md'; target.write_text(DEFINITION, encoding='utf-8')
        before = self.snapshot()
        result = workflows.handle('validate', self.root, {'definition': 'sample.md'}, False)
        self.assertTrue(result['ok'], result); self.assertEqual(before, self.snapshot())
        self.assertFalse(workflows.handle('start', self.root, {'activity_id': self.aid, 'definition': 'sample.md', 'provenance': self.prov}, True)['ok'])

    def test_role_drift_after_prepare_blocks_dispatch_and_retry_refreshes(self):
        self.start(); self.prepare()
        role = self.root / '.hai_env/agents/worker/SKILL.md'
        role.write_text(role.read_text().replace('Execute the supplied assignment.', 'Execute the reviewed assignment.'), encoding='utf-8')
        state = self.show()
        r = self.mutation('record-execution', step_id='first', attempt_id=state['current_attempt'],
                          status='running', executor=self.executor, details='Dispatch requested')
        self.assertFalse(r['ok']); self.assertEqual(self.show()['status'], 'prepared')
        self.assertTrue(self.mutation('pause')['ok'])
        self.assertFalse(self.mutation('resume', **self.ready)['ok'])
        r = self.mutation('retry-step', step_id='first', attempt_id=state['current_attempt'],
                          executor={**self.executor, 'writers_ended': True}, effect_resolution='Previous attempt never dispatched; no effects', **self.ready)
        self.assertTrue(r['ok'], r); self.assertEqual(self.show()['current_attempt'], 'attempt-0002')
        self.assertEqual(self.show()['effect_resolutions'][0]['resolution'], 'Previous attempt never dispatched; no effects')
        self.running()

    def test_running_role_drift_rejects_completion_but_stopped_evidence_is_retained(self):
        self.start(); self.prepare(); self.running(); self.output('output.bin')
        role = self.root / '.hai_env/agents/worker/SKILL.md'
        role.write_text(role.read_text().replace('Execute the supplied assignment.', 'Execute the reviewed assignment.'), encoding='utf-8')
        r = self.finish('supplied'); self.assertFalse(r['ok'], r)
        self.assertEqual(self.show()['status'], 'blocked'); self.assertTrue(self.show()['executor']['writers_ended'])
        self.assertEqual(self.show()['accepted'], {})

    def test_role_registration_models_and_disabled_settings_are_checked(self):
        self.start(); missing = self.root / '.hai_env/agents/catalogue.md'; original = missing.read_bytes(); missing.unlink()
        self.assertFalse(self.mutation('prepare-step', **self.ready)['ok']); missing.write_bytes(original)
        wrong = {**self.ready, 'runtime': {'models': {'other': ['high']}}}
        self.assertFalse(self.mutation('prepare-step', **wrong)['ok'])
        contract = self.root / '.hai_env/agents/worker/configuration/contract.json'
        data = json.loads(contract.read_text())
        data['settings'] = {'enabled': {'type': 'boolean', 'default': True}}
        contract.write_text(json.dumps(data), encoding='utf-8')
        settings = self.root / '.hai_env/config/agents'; settings.mkdir()
        override = settings / 'worker.json'
        override.write_text(json.dumps({'config_format_version': 1, 'settings': {'enabled': False}}), encoding='utf-8')
        before = self.snapshot(); disabled = self.mutation('prepare-step', **self.ready)
        self.assertFalse(disabled['ok'], disabled)
        self.assertIn('owned feature is disabled', str(disabled['issues']))
        self.assertEqual(before, self.snapshot()); self.assertEqual(self.show()['attempt_count'], 0)
        override.write_text(json.dumps({'config_format_version': 1, 'settings': {'enabled': True}}), encoding='utf-8')
        self.assertTrue(self.prepare()['ok'])

    def test_input_secret_and_other_activity_paths_are_rejected(self):
        secret = self.root / '.env'; secret.write_text('SECRET', encoding='utf-8')
        self.defpath.write_text(DEFINITION.replace('activity:input.md', 'workspace:.env'), encoding='utf-8')
        r = workflows.handle('start', self.root, {'activity_id': self.aid, 'definition': '.hai_env/workflows/sample.md', 'provenance': self.prov}, True)
        self.assertFalse(r['ok']); self.assertFalse((self.activity / 'workflow-runs').exists())

    def test_activity_local_prior_run_inputs_require_exact_accepted_output(self):
        self.start(); self.prepare(); self.running(); self.output('output.bin')
        self.assertTrue(self.finish('supplied')['ok'])
        relative = 'workflow-runs/' + self.run_id + '/attempts/first/attempt-0001/'
        activity_path = self.activity.relative_to(self.root).as_posix()
        for prefix in ('activity:', 'workspace:' + activity_path + '/'):
            self.defpath.write_text(DEFINITION.replace('activity:input.md', prefix + relative + 'output.bin'), encoding='utf-8')
            result = workflows.handle('start', self.root, {'activity_id': self.aid,
                'definition': '.hai_env/workflows/sample.md', 'provenance': self.prov}, True)
            self.assertTrue(result['ok'], result)
            for tail in ('assignment.json', 'unaccepted.bin'):
                if tail == 'unaccepted.bin':
                    (self.activity / relative / tail).write_bytes(b'Not accepted evidence')
                self.defpath.write_text(DEFINITION.replace('activity:input.md', prefix + relative + tail), encoding='utf-8')
                result = workflows.handle('start', self.root, {'activity_id': self.aid,
                    'definition': '.hai_env/workflows/sample.md', 'provenance': self.prov}, True)
                self.assertFalse(result['ok'], result)
                self.assertIn('accepted output', str(result))

    def test_input_directory_must_not_enclose_own_run_store(self):
        location = 'workspace:' + self.activity.relative_to(self.root).as_posix()
        self.defpath.write_text(DEFINITION.replace('activity:input.md', location), encoding='utf-8')
        result = workflows.handle('start', self.root, {'activity_id': self.aid,
            'definition': '.hai_env/workflows/sample.md', 'provenance': self.prov}, True)
        self.assertFalse(result['ok'], result)
        self.assertIn('encloses protected content', str(result))
        self.assertFalse((self.activity / 'workflow-runs').exists())

    def test_prior_output_changed_after_lineage_verification_is_not_resnapshotted(self):
        self.start(); self.prepare(); self.running(); output = self.output('output.bin')
        self.assertTrue(self.finish('supplied')['ok'])
        location = 'activity:workflow-runs/' + self.run_id + '/attempts/first/attempt-0001/output.bin'
        self.defpath.write_text(DEFINITION.replace('activity:input.md', location), encoding='utf-8')
        original = workflows.load_run

        def changed_after_verified(*args):
            result = original(*args)
            output.write_bytes(b'Changed after accepted predecessor was checked')
            return result

        before_dirs = {p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_dir()}
        with mock.patch.object(workflows, 'load_run', side_effect=changed_after_verified):
            result = workflows.handle('start', self.root, {'activity_id': self.aid,
                'definition': '.hai_env/workflows/sample.md', 'provenance': self.prov}, True)
        self.assertFalse(result['ok'], result)
        self.assertIn('changed before snapshot', str(result))
        self.assertEqual(result['changed_files'], [])
        self.assertEqual(before_dirs, {p.relative_to(self.root).as_posix()
                                      for p in self.root.rglob('*') if p.is_dir()})

    def test_inputs_from_another_activity_are_rejected_with_local_storage(self):
        other = self.activity.parent / '20261115_170000_other'
        other.mkdir()
        state = json.loads((self.activity / 'state.json').read_text(encoding='utf-8'))
        state.update(activity_id='11111111-1111-4111-8111-111111111111',
                     lifecycle='closed', closed_at='2026-11-15T17:00:00Z', outcome='completed')
        (other / 'state.json').write_text(json.dumps(state), encoding='utf-8')
        for name in ('input.md', 'log.md', 'outcome.md'):
            (other / name).write_text('Other retained Activity', encoding='utf-8')
        (other / 'request.md').write_text('Another Activity', encoding='utf-8')
        location = 'workspace:' + other.relative_to(self.root).as_posix() + '/request.md'
        self.defpath.write_text(DEFINITION.replace('activity:input.md', location), encoding='utf-8')
        result = workflows.handle('start', self.root, {'activity_id': self.aid,
            'definition': '.hai_env/workflows/sample.md', 'provenance': self.prov}, True)
        self.assertFalse(result['ok'], result)
        self.assertIn('another Activity', str(result))
        self.assertFalse((self.activity / 'workflow-runs').exists())


def read_assignment(root, aid, rid, state):
    return json.loads((root / workflows.run_base(root, aid, rid) / 'attempts' / state['current_step'] / state['current_attempt'] / 'assignment.json').read_text())


if __name__ == '__main__':
    unittest.main()
