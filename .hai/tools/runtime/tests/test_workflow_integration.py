"""Workflow integration with CLI discovery, Activity closure and storage boundaries."""
import contextlib
import io
import json
import unittest
import test_workflow_runs as fixtures
from runtime import activities, cli, workflows
from runtime.storage import SafetyError


class WorkflowIntegrationTests(unittest.TestCase):
    def setUp(self):
        fixtures.WorkflowRunTests.setUp(self)

    def test_cli_lists_registration_and_validates_template_without_starting_run(self):
        template = self.root / '.hai/templates/sample.md'
        template.write_bytes(self.defpath.read_bytes())
        request = self.root / 'validate.json'
        request.write_text(json.dumps({'definition': '.hai/templates/sample.md'}), encoding='utf-8')
        for args in (['workflow', 'list'], ['workflow', 'validate', '--request', 'validate.json']):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = cli.main([*args, '--workspace', str(self.root)])
            report = json.loads(output.getvalue())
            self.assertEqual(code, 0, report)
            self.assertTrue(report['ok'], report)
            self.assertEqual(report['changed_files'], [])
        self.assertFalse((self.activity / 'workflow-runs').exists())
        result = workflows.handle('start', self.root, {'activity_id': self.aid,
            'definition': '.hai/templates/sample.md', 'provenance': self.prov}, True)
        self.assertFalse(result['ok'], result)
        self.assertFalse((self.activity / 'workflow-runs').exists())

    def test_unfinished_run_blocks_activity_close_before_lifecycle_writes(self):
        result = workflows.handle('start', self.root, {'activity_id': self.aid,
            'definition': '.hai_env/workflows/sample.md', 'provenance': self.prov}, True)
        self.assertTrue(result['ok'], result)
        before = {p.relative_to(self.root).as_posix(): p.read_bytes()
                  for p in self.root.rglob('*') if p.is_file()}
        # The workflow gate must precede recording, usage and lifecycle writes.
        result = activities.handle('close', self.root,
            {'activity_id': self.aid, 'provenance': self.prov}, True)
        self.assertFalse(result['ok'], result)
        self.assertIn('workflow', str(result).lower())
        after = {p.relative_to(self.root).as_posix(): p.read_bytes()
                 for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_missing_workflow_collection_does_not_block_ordinary_activity(self):
        self.defpath.unlink()
        self.defdir.rmdir()
        workflows.assert_activity_closable(self.root, self.aid)
        result = activities.handle('record', self.root,
            {'activity_id': self.aid, 'log': 'Ordinary work', 'provenance': self.prov}, True)
        self.assertTrue(result['ok'], result)
        self.assertFalse((self.activity / 'workflow-runs').exists())

    def test_workflow_roots_cannot_be_configured_as_activity_store(self):
        state_path = self.root / '.hai_env/config/state.json'
        state = json.loads(state_path.read_text(encoding='utf-8'))
        for path in ('roles', 'roles/activities', 'skills', 'workflows', '.hai_env/skills', '.hai_env/skills/activities', '.hai_env/roles', '.hai_env/roles/activities', 'hai_roles_library', 'hai_agents_library', '.hai_env/workflows', '.hai_env/workflows/activities',
                     '.hai_env/workflow-runs', '.hai_env/workflow-runs/activities'):
            state['activities']['location'] = path
            state_path.write_text(json.dumps(state), encoding='utf-8')
            with self.assertRaises(SafetyError, msg=path):
                activities.store_path(self.root)

    def test_archival_moves_runs_with_owner_and_allows_only_inspection(self):
        result = workflows.handle('start', self.root, {'activity_id': self.aid,
            'definition': '.hai_env/workflows/sample.md', 'provenance': self.prov}, True)
        self.assertTrue(result['ok'], result)
        run = result['result']['state']
        common = {'activity_id': self.aid, 'run_id': run['run_id'], 'provenance': self.prov}
        result = workflows.handle('cancel', self.root,
            {**common, 'expected_revision': run['revision']}, True)
        self.assertTrue(result['ok'], result)
        run_dir = self.root / workflows.run_base(self.root, self.aid, run['run_id'])
        before = {p.relative_to(run_dir).as_posix(): p.read_bytes()
                  for p in run_dir.rglob('*') if p.is_file()}
        result = activities.handle('close', self.root, {'activity_id': self.aid,
            'outcome': 'completed', 'archive_label': 'workflow-fixture',
            'outcome_text': 'Controlled workflow fixture complete.',
            'recording': {'status': 'disabled', 'details': 'Fixture recording disabled'},
            'provenance': self.prov}, True)
        self.assertTrue(result['ok'], result)
        old_run_dir = run_dir
        run_dir = self.root / workflows.run_base(self.root, self.aid, run['run_id'])
        self.assertNotEqual(old_run_dir, run_dir)
        self.assertFalse(old_run_dir.exists())
        result = workflows.handle('show', self.root,
            {'activity_id': self.aid, 'run_id': run['run_id']}, False)
        self.assertTrue(result['ok'], result)
        result = workflows.handle('resume', self.root,
            {**common, 'expected_revision': result['result']['state']['revision']}, True)
        self.assertFalse(result['ok'], result)
        self.assertEqual(before, {p.relative_to(run_dir).as_posix(): p.read_bytes()
                                  for p in run_dir.rglob('*') if p.is_file()})

    def test_configured_activity_store_owns_runs_without_activity_uuid_level(self):
        store = self.root / 'project-work'
        store.mkdir()
        moved = store / self.activity.name
        self.activity.rename(moved)
        self.activity = moved
        state_path = self.root / '.hai_env/config/state.json'
        state = json.loads(state_path.read_text(encoding='utf-8'))
        state['activities']['location'] = 'project-work'
        state_path.write_text(json.dumps(state), encoding='utf-8')
        result = workflows.handle('start', self.root, {'activity_id': self.aid,
            'definition': '.hai_env/workflows/sample.md', 'provenance': self.prov}, True)
        self.assertTrue(result['ok'], result)
        run = result['result']['state']
        self.assertEqual(result['result']['path'],
                         'project-work/' + moved.name + '/workflow-runs/' + run['run_id'])
        self.assertFalse((self.root / '.hai_env/workflow-runs').exists())
        self.assertFalse((moved / 'workflow-runs' / self.aid).exists())

    def test_external_legacy_runs_are_not_silently_ignored_or_reused(self):
        legacy = self.root / '.hai_env/workflow-runs' / self.aid
        legacy.mkdir(parents=True)
        (legacy / 'partial-evidence.txt').write_text('Keep this evidence', encoding='utf-8')
        before = {p.relative_to(self.root).as_posix(): p.read_bytes()
                  for p in self.root.rglob('*') if p.is_file()}
        for apply in (False, True):
            result = workflows.handle('start', self.root, {'activity_id': self.aid,
                'definition': '.hai_env/workflows/sample.md', 'provenance': self.prov}, apply)
            self.assertFalse(result['ok'], result)
            self.assertIn('explicit relocation', str(result))
        with self.assertRaises(SafetyError):
            workflows.assert_activity_closable(self.root, self.aid)
        self.assertEqual(before, {p.relative_to(self.root).as_posix(): p.read_bytes()
                                  for p in self.root.rglob('*') if p.is_file()})
        self.assertFalse((self.activity / 'workflow-runs').exists())


if __name__ == '__main__':
    unittest.main()
