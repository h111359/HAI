"""Configurable workflow behavior with isolated environment choices and typed chat."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import unittest
from unittest import mock
import test_workflow_runs as fixtures
from runtime import activities, workflows, workflow_config, workflow_lineage
from runtime.storage import SafetyError
from workflows.definition import parse_definition, DefinitionError

SOURCE = fixtures.TOOLS.parents[1] / 'workflows/software-development.md'


class ConfigurableWorkflowTests(unittest.TestCase):
    call = fixtures.WorkflowRunTests.call
    show = fixtures.WorkflowRunTests.show
    mutation = fixtures.WorkflowRunTests.mutation
    prepare = fixtures.WorkflowRunTests.prepare
    running = fixtures.WorkflowRunTests.running
    snapshot = fixtures.WorkflowRunTests.snapshot

    def setUp(self):
        original = activities.handle
        def create_layout2(op, root, request, apply):
            if op == 'create':
                request = {**request, 'layout_version': 2}
            return original(op, root, request, apply)
        with mock.patch.object(activities, 'handle', side_effect=create_layout2):
            fixtures.WorkflowRunTests.setUp(self)
        self.source = self.root / 'workflows/software-development.md'
        self.source.parent.mkdir()
        self.source.write_bytes(SOURCE.read_bytes())
        self.parsed = parse_definition(self.source.read_bytes())
        roles = sorted({step['role'] for step in self.parsed['steps'].values()})
        for role in roles:
            package = self.root / '.hai_env/roles' / role
            shutil.copytree(self.root / '.hai_env/roles/worker', package)
            text = (package / 'ROLE.md').read_text().replace('name: worker', 'name: ' + role)
            (package / 'ROLE.md').write_text(text, encoding='utf-8')
            contract = json.loads((package / 'configuration/contract.json').read_text())
            contract['role'] = role
            (package / 'configuration/contract.json').write_text(json.dumps(contract), encoding='utf-8')
        (self.root / '.hai_env/roles/catalogue.md').write_text('# Roles\n\n| Role | Selection guide | Definition |\n| --- | --- | --- |\n' + ''.join('| `' + role + '` | Perform fixture work. | [ROLE.md](' + role + '/ROLE.md) |\n' for role in roles), encoding='utf-8')
        self.locations = {'handoffs': 'delivery/handoffs', 'completion': 'delivery/completed'}
        self.assignment = None

    def install(self, values=None, apply=True, **kw):
        return workflows.handle('install', self.root, {'definition': 'workflows/software-development.md',
            'provenance': self.prov, **({'locations': values} if values is not None else {}), **kw}, apply)

    def start(self):
        result = workflows.handle('start', self.root, {'activity_id': self.aid,
            'definition': '.hai_env/workflows/software-development.md', 'provenance': self.prov}, True)
        self.assertTrue(result['ok'], result)
        self.run_id = result['result']['state']['run_id']
        return result

    def begin(self):
        self.assignment = self.prepare()['result']['assignment']
        self.running()
        for name, row in self.assignment['outputs'].items():
            (self.root / row['path']).write_text(self.assignment['step_id'] + ' evidence ' + name, encoding='utf-8')
        return self.assignment

    def human(self, text='I approve the presented current result.', role='human'):
        result = activities.handle('chat-post', self.root, {'activity_id': self.aid, 'author': 'fixture-human' if role == 'human' else 'fixture-agent',
            'role': role, 'message_type': 'instruction', 'text': text, 'provenance': self.prov}, True)
        self.assertTrue(result['ok'], result)
        msg = result['result']['message']
        return {'message_id': msg['message_id'], 'message_sha256': hashlib.sha256(workflow_lineage.canonical(msg)).hexdigest(),
                'checkpoint_sha256': self.assignment['checkpoint_sha256'], 'accepted': True,
                'author': 'fixture-host', 'evidence': 'Observed fixture human approval in the presented checkpoint context.'}

    def finish(self, result, approval=None):
        state = self.show()
        return self.mutation('complete-step', step_id=state['current_step'], attempt_id=state['current_attempt'],
            result=result, assessment=self.assessment, executor={**self.executor, 'writers_ended': True},
            **({'human_approval': approval} if approval is not None else {}))

    def accepted(self, label, human=False):
        assignment = self.begin()
        result = self.finish(label, self.human() if human else None)
        self.assertTrue(result['ok'], result)
        return assignment, result['result']['acceptance']

    def approved_design(self):
        self.accepted('prepared'); self.accepted('refined'); self.accepted('designed'); self.accepted('approved', True)

    def test_install_preview_missing_guard_and_two_environment_values_preserved(self):
        before = self.snapshot()
        preview = self.install(apply=False)
        self.assertTrue(preview['ok'], preview)
        self.assertFalse(preview['result']['ready'])
        self.assertEqual({q['name'] for q in preview['result']['questions']}, set(self.locations))
        self.assertTrue(all(q['purpose'] and q['contents'] for q in preview['result']['questions']))
        self.assertEqual(before, self.snapshot())
        self.assertFalse(self.install()['ok'])
        # A source definition copied without environment settings cannot start.
        installed = self.root / '.hai_env/workflows/software-development.md'
        installed.write_bytes(self.source.read_bytes())
        missing = workflows.handle('start', self.root, {'activity_id': self.aid, 'definition': '.hai_env/workflows/software-development.md', 'provenance': self.prov}, True)
        self.assertFalse(missing['ok'], missing)
        installed.unlink()
        self.assertTrue(self.install(self.locations)['ok'])
        self.assertFalse((self.activity / 'workflow-runs').exists())
        saved = (self.root / workflow_config.config_path('software-development')).read_bytes()
        self.assertTrue(self.install()['ok'])
        self.assertEqual(saved, (self.root / workflow_config.config_path('software-development')).read_bytes())
        # A second independently initialized environment chooses different fixture bases.
        other = ConfigurableWorkflowTests('test_unsafe_locations_block_without_writes')
        other.setUp()
        try:
            values = {'handoffs': 'reports/work', 'completion': 'reports/final'}
            result = other.install(values)
            self.assertTrue(result['ok'], result)
            self.assertEqual(workflow_config.load(other.root, other.parsed)['locations'], values)
            self.assertNotEqual(values, workflow_config.load(self.root, self.parsed)['locations'])
            self.assertFalse((other.activity / 'workflow-runs').exists())
        finally:
            other.doCleanups()

    def test_unsafe_locations_block_without_writes(self):
        for unsafe in ('../escape', '/absolute', 'C:/absolute', '.hai_env/config', '.git/x', 'roles/x', 'skills/x', 'workflows/x', '.hai', '.hai_env/roles', '.hai_env/skills', '.hai_env/workflows', 'delivery/../x', 'NUL', '.hai_env/activities'):
            before = self.snapshot()
            result = self.install({**self.locations, 'handoffs': unsafe})
            self.assertFalse(result['ok'], (unsafe, result))
            self.assertEqual(before, self.snapshot())
        for values in ({'handoffs': 'x', 'completion': 'x/nested'}, {'handoffs': 'Case', 'completion': 'case'}):
            self.assertFalse(self.install(values)['ok'])
        self.assertTrue(self.install({'handoffs': '.hai_env/workflow-outputs', 'completion': '.hai_env/workflow-outputs'})['ok'])

    def test_install_case_alias_and_unstable_existing_settings_preserve_bytes(self):
        self.assertTrue(self.install(self.locations)['ok'])
        installed = self.root / '.hai_env/workflows/software-development.md'
        alias = installed.with_name('Software-Development.md')
        installed.rename(alias)
        before = self.snapshot()
        self.assertFalse(self.install()['ok'])
        self.assertEqual(before, self.snapshot())
        alias.rename(installed)
        original = workflow_config.read_json
        path = self.root / workflow_config.config_path('software-development')
        def concurrent_change(target):
            result = original(target)
            if Path(target) == path:
                path.write_bytes(path.read_bytes() + b' ')
            return result
        with mock.patch.object(workflow_config, 'read_json', side_effect=concurrent_change):
            result = self.install()
        self.assertFalse(result['ok'], result)
        self.assertIn('changed while reading', str(result))
        self.assertEqual(installed.read_bytes(), self.source.read_bytes())

    def test_update_preserves_settings_and_exact_predecessors(self):
        self.assertTrue(self.install(self.locations)['ok'])
        installed = self.root / '.hai_env/workflows/software-development.md'
        old = installed.read_bytes()
        saved = (self.root / workflow_config.config_path('software-development')).read_bytes()
        self.source.write_bytes(old.replace(b'revision: 1', b'revision: 2'))
        self.assertFalse(self.install()['ok'])
        result = self.install(expected_installed_sha256=hashlib.sha256(old).hexdigest())
        self.assertTrue(result['ok'], result)
        self.assertEqual(workflow_config.load(self.root, parse_definition(self.source.read_bytes()))['locations'], self.locations)
        backups = self.root / '.hai_env/config/workflows/history/software-development'
        self.assertEqual([p.read_bytes() for p in backups.glob('*/definition.md')], [old])
        self.assertEqual([p.read_bytes() for p in backups.glob('*/configuration.json')], [saved])
        current = self.snapshot()
        self.source.write_bytes(self.source.read_bytes().replace(b'| completion |', b'| changed |').replace(b'configured:completion/', b'configured:changed/'))
        result = self.install(expected_installed_sha256=hashlib.sha256(installed.read_bytes()).hexdigest())
        self.assertFalse(result['ok'], result)
        self.assertEqual(installed.read_bytes(), current['.hai_env/workflows/software-development.md'])

    def test_partial_qa_loop_exact_lineage_two_executions_and_acceptance(self):
        self.assertTrue(self.install(self.locations)['ok']); self.start(); self.approved_design()
        first, first_record = self.accepted('implemented')
        _, defects = self.accepted('defects')
        again = self.begin()
        self.assertEqual(again['step_id'], 'implement'); self.assertEqual(again['execution_number'], 2)
        self.assertIn('implement-001-', first['outputs']['implementation']['path'])
        self.assertIn('implement-002-', again['outputs']['implementation']['path'])
        self.assertNotEqual(first['outputs']['implementation']['path'], again['outputs']['implementation']['path'])
        self.assertEqual(again['inputs']['requirements']['acceptance_key'], 'clarify/attempt-0001')
        self.assertEqual(again['inputs']['design']['acceptance_key'], 'design/attempt-0001')
        self.assertEqual(again['inputs']['design-approval']['acceptance_key'], 'approve-design/attempt-0001')
        self.assertEqual(again['inputs']['defects']['acceptance_key'], 'verify/attempt-0001')
        self.assertEqual(again['inputs']['defects']['artifact'], defects['outputs']['defects']['artifact'])
        self.assertTrue((self.root / first['outputs']['implementation']['path']).exists())
        self.assertTrue(self.finish('implemented')['ok'])
        self.accepted('passed'); self.accepted('accepted', True)
        assignment, final = self.accepted('completed')
        self.assertEqual(assignment['role'], 'backlog-manager')
        self.assertEqual(final['inputs']['qa-pass']['producer_result'], 'passed')
        self.assertEqual(final['inputs']['human-acceptance']['producer_result'], 'accepted')
        self.assertEqual(self.show()['outcome'], 'delivered')
        self.assertEqual(json.loads((self.activity / 'system/state.json').read_text())['lifecycle'], 'active')
        self.assertEqual(len(self.show()['accepted']), 10)

    def test_failed_qa_missing_changed_and_unaccepted_inputs_block(self):
        self.assertTrue(self.install(self.locations)['ok']); self.start(); self.approved_design()
        self.accepted('implemented'); self.accepted('defects')
        state = self.show(); base = workflows.run_base(self.root, self.aid, self.run_id)
        with self.assertRaisesRegex(SafetyError, 'qa-pass'):
            workflow_lineage.inputs(self.root, base, state, self.parsed['steps']['accept-result'])
        altered = copy.deepcopy(state)
        del altered['accepted']['design/attempt-0001']
        with self.assertRaises(SafetyError):
            workflow_lineage.inputs(self.root, base, altered, self.parsed['steps']['implement'])
        # Changing an accepted ancestor invalidates approval transitively even with identical bytes.
        altered = copy.deepcopy(state)
        new_req = copy.deepcopy(altered['accepted']['clarify/attempt-0001'])
        new_req['attempt_id'] = 'attempt-0002'
        new_req['execution_number'] = 2
        altered['accepted']['clarify/attempt-0002'] = new_req
        with self.assertRaisesRegex(SafetyError, 'superseded'):
            workflow_lineage.inputs(self.root, base, altered, self.parsed['steps']['implement'])
        row = state['accepted']['design/attempt-0001']['outputs']['design']
        external = self.root / row['configured_path']; original = external.read_bytes()
        external.write_bytes(b'Changed design')
        self.assertFalse(self.mutation('prepare-step', **self.ready)['ok'])
        external.write_bytes(original); external.unlink()
        self.assertFalse(self.mutation('prepare-step', **self.ready)['ok'])

    def test_human_gates_reject_missing_fabricated_agent_stale_and_precheckpoint_messages(self):
        self.assertTrue(self.install(self.locations)['ok']); self.start()
        self.accepted('prepared'); self.accepted('refined'); self.accepted('designed')
        self.begin()
        self.assertFalse(self.finish('approved')['ok'])
        fake = {'accepted': True, 'author': 'AI', 'evidence': 'Human approved'}
        self.assertFalse(self.finish('approved', fake)['ok'])
        agent = self.human(role='agent')
        self.assertFalse(self.finish('approved', agent)['ok'])
        real = self.human('Approved, implement the presented design.')
        stale = {**real, 'checkpoint_sha256': '0' * 64}
        self.assertFalse(self.finish('approved', stale)['ok'])
        self.assertTrue(self.finish('approved', real)['ok'])
        self.accepted('implemented'); self.accepted('passed'); self.begin()
        self.assertFalse(self.finish('accepted')['ok'])
        self.assertFalse(self.finish('accepted', real)['ok'])
        earlier = {**real, 'checkpoint_sha256': self.assignment['checkpoint_sha256']}
        self.assertFalse(self.finish('accepted', earlier)['ok'])
        self.assertTrue(self.finish('accepted', self.human('I accept the verified result.'))['ok'])
        self.assertEqual(self.show()['current_step'], 'complete')

    def test_two_runs_archive_keeps_internal_evidence_independent_of_external_files(self):
        self.assertTrue(self.install(self.locations)['ok']); self.start()
        first_assignment, record = self.accepted('prepared')
        first_id = self.run_id
        initial = self.show()
        self.assertTrue(self.mutation('cancel')['ok'])
        first_base = self.root / workflows.run_base(self.root, self.aid, first_id)
        retained = {p.relative_to(first_base).as_posix(): p.read_bytes() for p in first_base.rglob('*') if p.is_file()}
        self.start(); second, _ = self.accepted('prepared')
        self.assertNotEqual(first_id, self.run_id)
        self.assertIn(first_id, first_assignment['outputs']['work-item']['path'])
        self.assertIn(self.run_id, second['outputs']['work-item']['path'])
        self.assertTrue(self.mutation('cancel')['ok'])
        # Removing configured fixture copies cannot erase authoritative accepted evidence.
        shutil.rmtree(self.root / 'delivery')
        closed = activities.handle('close', self.root, {'activity_id': self.aid, 'outcome': 'completed',
            'archive_label': 'configured-workflow-fixture', 'outcome_text': 'Explicit fixture-only archive.',
            'recording': {'status': 'disabled', 'details': 'Fixture recording disabled'}, 'provenance': self.prov}, True)
        self.assertTrue(closed['ok'], closed)
        shown = workflows.handle('show', self.root, {'activity_id': self.aid, 'run_id': first_id}, False)
        self.assertTrue(shown['ok'], shown)
        archived = self.root / workflows.run_base(self.root, self.aid, first_id)
        self.assertNotEqual(first_base, archived)
        self.assertEqual(retained, {p.relative_to(archived).as_posix(): p.read_bytes() for p in archived.rglob('*') if p.is_file()})
        self.assertEqual(shown['result']['state']['inputs'], initial['inputs'])

    def test_new_output_conflicts_and_partial_staging_are_preserved(self):
        self.assertTrue(self.install(self.locations)['ok']); self.start()
        collision = self.root / self.locations['handoffs'] / self.run_id / 'prepare-001-work-item.md'
        collision.parent.mkdir(parents=True); collision.write_bytes(b'Existing unrelated bytes')
        before = self.snapshot()
        result = self.mutation('prepare-step', **self.ready)
        self.assertFalse(result['ok'], result); self.assertEqual(before, self.snapshot())
        collision.unlink(); self.begin()
        original = workflows.copy_snapshot
        def failure(root, src, dest, changed):
            original(root, src, dest, changed)
            raise SafetyError('Injected post-copy failure', changed)
        with mock.patch.object(workflows, 'copy_snapshot', side_effect=failure):
            result = self.finish('prepared')
        self.assertEqual(result['status'], 'partial', result)
        self.assertTrue(any('/accepted/' in p for p in result['changed_files']))
        shown = workflows.handle('show', self.root, {'activity_id': self.aid, 'run_id': self.run_id}, False)
        self.assertFalse(shown['ok'], shown)
        self.assertIn('Uncommitted', str(shown))

    def test_scope_return_reapproves_and_discards_only_historical_defect_feedback(self):
        self.assertTrue(self.install(self.locations)['ok']); self.start(); self.approved_design()
        self.accepted('implemented'); self.accepted('defects'); self.accepted('scope-change')
        clarification, _ = self.accepted('refined')
        self.assertTrue(clarification['inputs']['questions']['historical_feedback'])
        self.accepted('designed'); approval_assignment = self.begin()
        self.assertEqual(approval_assignment['inputs']['requirements']['acceptance_key'], 'clarify/attempt-0002')
        self.assertEqual(approval_assignment['inputs']['design']['acceptance_key'], 'design/attempt-0002')
        self.assertFalse(self.finish('approved')['ok'])
        self.assertTrue(self.finish('approved', self.human('I approve this revised scope and design.'))['ok'])
        implementation = self.begin()
        self.assertEqual(implementation['execution_number'], 3)
        self.assertIsNone(implementation['inputs']['defects'])
        self.assertEqual(implementation['inputs']['design-approval']['acceptance_key'], 'approve-design/attempt-0002')
        self.assertTrue(self.finish('implemented')['ok'])
        self.accepted('passed'); self.accepted('accepted', True); self.accepted('completed')
        self.assertEqual(self.show()['outcome'], 'delivered')

    def test_historical_format_one_and_two_show_preserve_exact_bytes(self):
        for version in (1, 2):
            raw = fixtures.DEFINITION.replace('activity:input.md', 'activity:README.md').encode()
            if version == 1:
                raw = raw.replace(b'workflow_format: 2', b'workflow_format: 1').replace(b'#### Role', b'#### Agent')
            contract = parse_definition(raw, allow_legacy=True)
            # Seed a retained-format fixture through the persistence path, without conversion.
            with mock.patch.object(workflows, 'definition', return_value=(contract, raw)):
                result = workflows.handle('start', self.root, {'activity_id': self.aid,
                    'definition': '.hai_env/workflows/sample.md', 'provenance': self.prov}, True)
            self.assertTrue(result['ok'], result)
            self.run_id = result['result']['state']['run_id']
            before = self.snapshot()
            state = self.show()
            self.assertEqual(state['workflow_run_format'], 1)
            self.assertEqual(before, self.snapshot())
            run = self.root / workflows.run_base(self.root, self.aid, self.run_id)
            self.assertEqual((run / 'definition.md').read_bytes(), raw)
            self.assertTrue(self.mutation('cancel')['ok'])

    def test_new_format_parser_rejects_unbound_names_tokens_and_result_mismatch(self):
        raw = self.source.read_text()
        for old, new in [('prepare-{execution}-work-item.md', 'work-item.md'), ('configured:handoffs/', 'configured:unknown/'),
                         ('accepted:verify/passed/verification', 'accepted:verify/defects/absent'), ('| human |', '| asserted |')]:
            with self.assertRaises(DefinitionError):
                parse_definition(raw.replace(old, new))
        self.assertEqual({s['role'] for s in self.parsed['steps'].values()}, {'backlog-manager','business-analyst','solution-architect','software-developer','quality-assurance'})
        self.assertNotIn('skill', raw.lower().split('## steps',1)[1].replace('skills', ''))


if __name__ == '__main__':
    unittest.main()
