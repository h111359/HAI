"""Deployment checks with no development library or implicit sibling probes."""
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
from runtime import environment, startup, activities, skills, packages, package_content
from runtime.storage import SafetyError
from role_state import status


class CoreBoundaryTests(unittest.TestCase):
    def setUp(self):
        parent = Path(os.environ['HAI_TEST_TMP']).resolve()
        self.temp = tempfile.TemporaryDirectory(prefix='boundary-', dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(TOOLS.parent, self.root / '.hai', ignore=shutil.ignore_patterns('__pycache__'))
        self.prov = {'source': 'isolated deployment fixture', 'reason': 'verify core boundary'}

    def initialize(self):
        result = environment.handle('environment/initialize', self.root, {'provenance': self.prov}, True)
        self.assertTrue(result['ok'], result)

    def guard(self, allowed=()):
        original_stat, original_lstat = Path.stat, Path.lstat
        def wrap(original):
            def checked(path, *args, **kwargs):
                try: relative = path.absolute().relative_to(self.root)
                except ValueError: relative = Path('.')
                if relative.parts and relative.parts[0] not in ('.hai', '.hai_env', *allowed):
                    raise AssertionError('Unconfigured sibling probe: ' + str(relative))
                return original(path, *args, **kwargs)
            return checked
        from contextlib import ExitStack
        stack = ExitStack()
        stack.enter_context(mock.patch.object(Path, 'stat', wrap(original_stat)))
        stack.enter_context(mock.patch.object(Path, 'lstat', wrap(original_lstat)))
        return stack

    def test_default_initialization_and_operations_never_probe_siblings(self):
        with self.guard():
            self.initialize()
            self.assertTrue(startup.handle('', self.root, {}, False)['ok'])
            self.assertEqual(status(self.root)['status'], 'ready')
            self.assertTrue(skills.handle('list', self.root, {}, False)['ok'])
            self.assertTrue(activities.handle('discover', self.root, {}, False)['ok'])
            self.assertTrue(activities.handle('create', self.root, {'initial_input':'Work','provenance':self.prov}, True)['ok'])
        self.assertEqual({p.name for p in self.root.iterdir()}, {'.hai', '.hai_env'})

    def test_unrelated_development_names_do_not_affect_readiness(self):
        self.initialize()
        for name in ['roles', 'skills', 'workflows', 'hai_roles_library', 'hai_agents_library', '.git']:
            (self.root / name).write_text('Unrelated project material.', encoding='utf-8')
        with self.guard():
            self.assertTrue(startup.handle('', self.root, {}, False)['ok'])
            self.assertTrue(skills.handle('list', self.root, {}, False)['ok'])
            self.assertEqual(status(self.root)['status'], 'ready')

    def test_explicit_custom_store_remains_supported(self):
        self.initialize()
        state = self.root / '.hai_env/config/state.json'
        value = json.loads(state.read_text(encoding='utf-8'))
        value['activities']['location'] = 'roles/activity-records'
        state.write_text(json.dumps(value), encoding='utf-8')
        with self.guard(allowed=('roles',)):
            self.assertTrue(startup.handle('', self.root, {}, False)['ok'])
            result = activities.handle('create', self.root, {'initial_input':'Configured work','provenance':self.prov}, True)
            self.assertTrue(result['ok'], result)
            self.assertTrue(result['result']['path'].startswith('roles/activity-records/'))

    def test_selected_source_mapping_and_configured_project_references(self):
        self.initialize()
        package = self.root / '.hai_env/incoming/worker'
        package.mkdir(parents=True)
        content = '# Instructions\n\n[Peer](../../../outside/peer/ROLE.md)\n'
        (package/'SKILL.md').write_text(content, encoding='utf-8')
        manifest = {'SKILL.md': None}
        with self.guard():
            with self.assertRaises(SafetyError):
                package_content.prepare(self.root, '.hai_env/incoming/worker', '.hai_env/skills/worker', manifest)
        # Explicit source root may now be inspected; only the selected peer is mapped.
        mapped, _, pending = package_content.prepare(self.root, '.hai_env/incoming/worker', '.hai_env/skills/worker', manifest,
            {'outside/peer':'.hai_env/roles/peer'})
        self.assertIn(b'../../roles/peer/ROLE.md', mapped['SKILL.md'])
        self.assertTrue(pending)
        (package/'SKILL.md').write_text('# Instructions\n\n[Policy](../../../project/policy.md)\n', encoding='utf-8')
        target = self.root / 'project'
        target.mkdir(); (target/'policy.md').write_text('Approved project policy.', encoding='utf-8')
        (self.root/'.hai_env/config/workspace-paths.json').write_text(json.dumps({'workspace_paths_format':1,'references':['project']}), encoding='utf-8')
        with self.guard(allowed=('project',)):
            _, _, pending = package_content.prepare(self.root, '.hai_env/incoming/worker', '.hai_env/skills/worker', manifest)
            self.assertEqual(pending, [])

if __name__ == '__main__':
    unittest.main()
