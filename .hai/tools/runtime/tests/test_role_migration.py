"""Lossless explicit migration, independent packages, and retained failure evidence."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile
import unittest
from unittest import mock

TOOLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS))
from runtime import activities, role_migration
from runtime.storage import read_json
from role_state import status
from role_upgrade import transform

BODY = '''## Purpose
Inspect scoped work.

## Scope
Read and report.

## Out of Scope
Changing material.

## Rules
- **Scope:** The worker MUST inspect only requested material.

## Procedures
### Inspect
Trigger: A bounded inspection is requested.

#### Description
Inspect the request and return findings.

#### Inputs
| Input | Meaning | Requirement | Source | If absent |
| --- | --- | --- | --- | --- |
| [input:task] | Request. | Mandatory | Caller. | Ask. |

#### Prerequisites
None.

#### Rules
None.

#### Steps
1. Inspect [input:task].

#### Outputs
| Output | Meaning | Completion criteria |
| --- | --- | --- |
| [output:result] | Findings. | Evidence reviewed. |

#### References
None.

## References
None.
'''


def tree(root):
    return {p.relative_to(root).as_posix(): (hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)
            for p in root.rglob('*')}


class RoleMigrationTests(unittest.TestCase):
    def setUp(self):
        # The caller chooses the Activity-owned work cwd; no OS temp artifacts.
        self.temp = tempfile.TemporaryDirectory(prefix='role-migration-fixture-', dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        shutil.copytree(TOOLS.parent, self.root / '.hai')
        self.prov = {'source': 'test host', 'reason': 'explicit role migration'}
        self.write('.hai_env/config/state.json', json.dumps({'state_format_version': 3,
            'activities': {'location': '.hai_env/activities'}, 'features': {'chronicles': {'enabled': False, 'record_every_prompts': 5}}, 'integrations': {}}))
        self.write('.hai_env/config/agent_instructions.md', '# Actual AI agent instructions\n')
        created = activities.handle('create', self.root, {'initial_input': 'request', 'summary': 'Migration fixture',
                                     'layout_version': 1 if self._testMethodName == 'test_legacy_core2_cli_migration_then_specification_extraction' else 2, 'provenance': self.prov}, True)
        self.assertTrue(created['ok'], created)
        self.base = created['result']['path']
        self.package('.hai_env/agents/worker', 'worker', 'Call to inspect installed agent packages.')
        self.write('.hai_env/agents/catalogue.md', '# Workspace agents\n\n| Agent | Selection guide | Definition |\n'
                   '| --- | --- | --- |\n| `worker` | Call to inspect installed agent packages. | [SKILL.md](worker/SKILL.md) |\n')

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode('utf-8') if isinstance(content, str) else content)
        return path

    def package(self, relative, name, description='Call to inspect source agent packages.'):
        self.write(relative + '/SKILL.md', '---\nname: ' + name + '\ndescription: ' + json.dumps(description)
            + '\nmetadata:\n  hai-configuration-contract: "configuration/contract.json"\n'
              '  hai-model-class: "light"\n  hai-reasoning-effort: "high"\n---\n\n' + BODY)
        self.write(relative + '/configuration/contract.json', json.dumps({'contract_format_version': 2,
            'agent': name, 'current_config_format_version': 7, 'supported_config_format_versions': [7], 'settings': {}}))

    def preview(self):
        return role_migration.handle(self.root, {'provenance': self.prov}, False)

    def apply(self, preview=None):
        preview = preview or self.preview()
        self.assertTrue(preview['ok'], preview)
        return role_migration.handle(self.root, {'provenance': self.prov,
            'writers_ended': True, 'expected_snapshot': preview['result']['expected_snapshot']}, True)

    def test_preview_is_deterministic_and_writes_nothing(self):
        before = tree(self.root)
        first, second = self.preview(), self.preview()
        self.assertTrue(first['ok'], first)
        self.assertEqual(first, second)
        self.assertEqual(tree(self.root), before)
        self.assertEqual(status(self.root)['status'], 'migration_required')

    def test_snapshot_and_host_attestation_are_required_before_staging(self):
        before = tree(self.root)
        p = self.preview()
        denied = role_migration.handle(self.root, {'provenance': self.prov,
            'expected_snapshot': p['result']['expected_snapshot']}, True)
        self.assertFalse(denied['ok'])
        denied = role_migration.handle(self.root, {'provenance': self.prov,
            'writers_ended': True, 'expected_snapshot': 'stale'}, True)
        self.assertFalse(denied['ok'])
        self.assertEqual(tree(self.root), before)

    def test_changed_source_and_destination_collisions_block(self):
        p = self.preview()
        self.write('.hai_env/agents/worker/local.bin', b'changed')
        self.assertFalse(self.apply(p)['ok'])
        self.write('.hai_env/roles/local/ROLE.md', 'collision')
        before = tree(self.root)
        self.assertFalse(self.preview()['ok'])
        self.assertEqual(tree(self.root), before)

    def test_independent_packages_settings_profiles_and_history_survive(self):
        self.package('hai_agents_library/agents/worker', 'worker')
        self.package('.hai_env/agents/local-advisor', 'local-advisor', 'Local custom package.')
        self.package('.hai_env/agents/agent-definition-manager', 'agent-definition-manager', 'Manager agent definition package.')
        self.write('hai_agents_library/README.md', '[Worker](agents/worker/SKILL.md)\nEnvironment-manager installs packages through Leader.\n')
        raw_settings = b'{"config_format_version":7,"settings":{},"unknown":{"agent":"business-data","values":[null,true,1]}}\r\n'
        self.write('.hai_env/config/agents/agent-definition-manager.json', raw_settings)
        profile = b'{"format_version":1,"models":{"light":"small","standard":"normal","advanced":"large"}}\n'
        self.write('.hai_env/config/model_profiles.json', profile)
        historical = self.write(self.base + '/history/old/run.json', b'{"agent":"historic","SKILL.md":"hash"}\r\n')
        native = self.write('.agents/skills/real/SKILL.md', 'actual skill SKILL.md\n')
        skill = self.write('.hai_env/agents/worker/skills/real/SKILL.md', 'A genuine skill keeps SKILL.md and agent package data.\n')
        original_skill = skill.read_bytes()
        nested = self.write('.hai_env/agents/worker/resources/real/SKILL.md', 'Genuine SKILL.md agent package rules')
        nested_body = self.write('.hai_env/agents/worker/resources/real/procedures/test.md', '[Own](../SKILL.md) agent package text')
        nested_bytes = (nested.read_bytes(), nested_body.read_bytes())
        before = tree(self.root)
        result = self.apply()
        self.assertTrue(result['ok'], result)
        self.assertEqual(status(self.root)['status'], 'ready')
        for key in ('historical',):
            self.assertEqual(historical.read_bytes(), b'{"agent":"historic","SKILL.md":"hash"}\r\n')
        self.assertEqual(native.read_text(), 'actual skill SKILL.md\n')
        self.assertEqual((self.root / '.hai_env/roles/worker/skills/real/SKILL.md').read_bytes(), original_skill)
        self.assertEqual((self.root / '.hai_env/roles/worker/resources/real/SKILL.md').read_bytes(), nested_bytes[0])
        self.assertEqual((self.root / '.hai_env/roles/worker/resources/real/procedures/test.md').read_bytes(), nested_bytes[1])
        self.assertEqual((self.root / '.hai_env/config/roles/role-definition-manager.json').read_bytes(), raw_settings)
        self.assertEqual((self.root / '.hai_env/config/model_profiles.json').read_bytes(), profile)
        installed = (self.root / '.hai_env/roles/worker/ROLE.md').read_text()
        source = (self.root / 'hai_roles_library/roles/worker/ROLE.md').read_text()
        self.assertIn('installed role packages', installed)
        self.assertIn('source role packages', source)
        library_readme = (self.root / 'hai_roles_library/README.md').read_text()
        self.assertIn('[Worker](roles/worker/ROLE.md)', library_readme)
        self.assertIn('runtime installs packages through host coordinator.', library_readme)
        self.assertTrue((self.root / '.hai_env/roles/local-advisor/ROLE.md').is_file())
        contract = read_json(self.root / '.hai_env/roles/role-definition-manager/configuration/contract.json')
        self.assertEqual((contract['contract_format_version'], contract['role'], contract['current_config_format_version']), (3, 'role-definition-manager', 7))
        for move in result['result']['mappings']:
            original = move['source']
            backup = move['backup']
            for path, digest in before.items():
                if digest and (path == original or path.startswith(original + '/')):
                    retained = self.root / (backup + path[len(original):])
                    self.assertEqual(hashlib.sha256(retained.read_bytes()).hexdigest(), digest)
        self.assertFalse(self.preview()['ok'])

    def test_partial_failure_retains_original_and_blocks_retry(self):
        original = role_migration.rename_exclusive
        count = 0
        def fail_publish(source, destination):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError('injected publication failure')
            return original(source, destination)
        with mock.patch.object(role_migration, 'rename_exclusive', side_effect=fail_publish):
            result = self.apply()
        self.assertFalse(result['ok'])
        marker = read_json(self.root / '.hai_env/config/role-migration.json')
        self.assertEqual(marker['status'], 'partial')
        self.assertTrue(marker['mappings'][0]['original_retained'])
        self.assertTrue((self.root / marker['mappings'][0]['backup'] / 'worker/SKILL.md').is_file())
        self.assertIn('.hai_env/agents', result['changed_files'])
        self.assertEqual(status(self.root)['status'], 'partial')
        before = tree(self.root)
        self.assertFalse(self.preview()['ok'])
        self.assertEqual(tree(self.root), before)

    def test_validated_stage_tampering_is_not_published(self):
        original = role_migration.rename_exclusive
        def tamper(source, destination):
            result = original(source, destination)
            if str(destination).endswith('originals' + os.sep + '.hai_env' + os.sep + 'agents'):
                candidates = list((self.root / self.base / 'work/coordinator/role-migration').glob('*/candidate/.hai_env/roles/worker/ROLE.md'))
                candidates[0].write_text('invalid candidate')
            return result
        with mock.patch.object(role_migration, 'rename_exclusive', side_effect=tamper):
            result = self.apply()
        self.assertFalse(result['ok'], result)
        self.assertFalse((self.root / '.hai_env/roles').exists())
        self.assertEqual(read_json(self.root / '.hai_env/config/role-migration.json')['status'], 'partial')

    def test_changed_profile_dependency_keeps_partial(self):
        original = role_migration.rename_exclusive
        def tamper(source, destination):
            result = original(source, destination)
            self.write('.hai_env/config/model_profiles.json', '{}')
            return result
        with mock.patch.object(role_migration, 'rename_exclusive', side_effect=tamper):
            result = self.apply()
        self.assertFalse(result['ok'])
        self.assertEqual(read_json(self.root / '.hai_env/config/role-migration.json')['status'], 'partial')
        self.assertEqual((self.root / '.hai_env/config/model_profiles.json').read_bytes(), b'{}')

    def test_only_execution_metadata_blocks_unfinished_work(self):
        run = self.base + '/workflow-runs/run-one'
        self.write(run + '/state.json', json.dumps({'status': 'finished', 'executor': {'writers_ended': True}}))
        self.write(run + '/attempts/step/attempt/files/customer-state.json', '{"business":"data"}')
        self.write(run + '/attempts/step/attempt/files/state.json', '{"business":"data"}')
        self.assertTrue(self.preview()['ok'])
        self.write(run + '/state.json', json.dumps({'status': 'running', 'executor': {'writers_ended': False}}))
        before = tree(self.root)
        self.assertFalse(self.preview()['ok'])
        self.assertEqual(tree(self.root), before)

    def test_missing_mandatory_instructions_blocks_direct_apply(self):
        p = self.preview()
        (self.root / '.hai_env/config/agent_instructions.md').unlink()
        before = tree(self.root)
        self.assertFalse(self.apply(p)['ok'])
        self.assertEqual(tree(self.root), before)

    def test_orphan_workflow_record_requires_resolution(self):
        self.write(self.base + '/workflow-runs/orphan/events.jsonl', '{}\n')
        before = tree(self.root)
        self.assertFalse(self.preview()['ok'])
        self.assertEqual(tree(self.root), before)

    def test_hardlink_alias_is_rejected_without_writes(self):
        source = self.root / '.hai_env/agents/worker/SKILL.md'
        os.link(source, self.root / 'alias.md')
        before = tree(self.root)
        self.assertFalse(self.preview()['ok'])
        self.assertEqual(tree(self.root), before)

    def test_legacy_core2_cli_migration_then_specification_extraction(self):
        from runtime import environment
        self.package('.hai_env/agents/specification-manager', 'specification-manager', 'Maintain product specification.')
        contract = {'contract_format_version': 2, 'agent': 'specification-manager',
                    'current_config_format_version': 1, 'supported_config_format_versions': [1],
                    'settings': {'enabled': {'type': 'boolean', 'default': False},
                                 'location': {'type': 'workspace-relative-directory', 'default': '.hai_env/specifications'}}}
        self.write('.hai_env/agents/specification-manager/configuration/contract.json', json.dumps(contract))
        catalogue = self.root / '.hai_env/agents/catalogue.md'
        catalogue.write_text(catalogue.read_text() + '| `specification-manager` | Maintain product specification. | [SKILL.md](specification-manager/SKILL.md) |\n')
        state = read_json(self.root / '.hai_env/config/state.json')
        state['state_format_version'] = 2
        state['features']['specification'] = {'enabled': True, 'location': '.hai_env/specifications'}
        self.write('.hai_env/config/state.json', json.dumps(state))
        p = self.preview()
        self.assertTrue(p['ok'], p)
        self.assertEqual(p['result']['activity_layout_version'], 1)
        request = {'provenance': self.prov, 'writers_ended': True, 'expected_snapshot': p['result']['expected_snapshot']}
        cli = subprocess.run([sys.executable, '-B', str(TOOLS / 'hai.py'), '--workspace', str(self.root),
                              '--request-stdin', '--apply', 'roles', 'migrate'], input=json.dumps(request),
                              capture_output=True, text=True)
        result = json.loads(cli.stdout)
        self.assertEqual(cli.returncode, 0, result)
        self.assertIn('/files/role-migration/', result['result']['backup_path'])
        self.assertFalse((self.root / self.base / 'history').exists())
        upgraded = environment.handle('environment/migrate-specification', self.root, {'provenance': self.prov}, True)
        self.assertTrue(upgraded['ok'], upgraded)
        self.assertEqual(read_json(self.root / '.hai_env/config/state.json')['state_format_version'], 3)
        self.assertEqual(read_json(self.root / '.hai_env/config/roles/specification-manager.json')['settings'],
                         {'enabled': True, 'location': '.hai_env/specifications'})

    def test_reusable_workflows_convert_but_pinned_snapshots_stay_exact(self):
        from test_workflow_runs import DEFINITION
        from workflows.definition import parse_definition
        legacy = DEFINITION.replace('workflow_format: 2', 'workflow_format: 1').replace('#### Role', '#### Agent')
        self.write('.hai_env/workflows/sample.md', legacy)
        pinned = self.write(self.base + '/workflow-runs/finished-run/definition.md', legacy)
        self.write(self.base + '/workflow-runs/finished-run/state.json', json.dumps({'status': 'finished', 'executor': {'writers_ended': True}}))
        result = self.apply()
        self.assertTrue(result['ok'], result)
        converted = (self.root / '.hai_env/workflows/sample.md').read_bytes()
        self.assertIn(b'workflow_format: 2', converted)
        self.assertIn(b'revision: 2', converted)
        self.assertIn(b'#### Role', converted)
        parse_definition(converted)
        self.assertEqual(pinned.read_bytes(), legacy.encode())

    def test_recreated_legacy_root_blocks_completion(self):
        original = role_migration.rename_exclusive
        def recreate(source, destination):
            result = original(source, destination)
            if destination == self.root / '.hai_env/roles':
                self.write('.hai_env/agents/new/SKILL.md', 'new writer')
            return result
        with mock.patch.object(role_migration, 'rename_exclusive', side_effect=recreate):
            result = self.apply()
        self.assertFalse(result['ok'])
        self.assertEqual(read_json(self.root / '.hai_env/config/role-migration.json')['status'], 'partial')
        self.assertTrue((self.root / '.hai_env/agents/new/SKILL.md').exists())

    def test_fragment_entry_links_and_python_ownership_guards(self):
        raw = (b'[Own](../SKILL.md#procedures) [Peer](../../peer/SKILL.md#rules) '
               b'[Canonical](.hai_env/agents/peer/SKILL.md#scope) '
               b'[Genuine](.hai_env/agents/peer/skills/example/SKILL.md#usage)')
        converted = transform('conventions/release.md', raw, package_names={'peer'})
        self.assertIn(b'[Own](../ROLE.md#procedures)', converted)
        self.assertIn(b'[Peer](../../peer/ROLE.md#rules)', converted)
        self.assertIn(b'[Canonical](.hai_env/roles/peer/ROLE.md#scope)', converted)
        self.assertIn(b'[Genuine](.hai_env/roles/peer/skills/example/SKILL.md#usage)', converted)
        guards = b"protected = {('hai_agents_library','agents'),('.hai_env','agents')}"
        self.assertEqual(transform('scripts/guard.py', guards),
                         b"protected = {('hai_roles_library','roles'),('.hai_env','roles')}")

    def test_transform_scope_and_self_entry_links(self):
        raw = b'[Own](../SKILL.md) [Real](../skills/x/SKILL.md) [SKILL.md](../../skills/x/SKILL.md)'
        converted = transform('procedures/inspect.md', raw)
        self.assertIn(b'[Own](../ROLE.md)', converted)
        self.assertIn(b'[Real](../skills/x/SKILL.md)', converted)
        self.assertIn(b'[SKILL.md](../../skills/x/SKILL.md)', converted)
        arbitrary = b'{"agent":"customer","SKILL.md":"document","path":".hai_env/agents"}'
        self.assertEqual(transform('data/customer.json', arbitrary), arbitrary)
        self.assertEqual(transform('skills/x/SKILL.md', raw), raw)
        with self.assertRaises(ValueError):
            transform('configuration/contract.json', b'{"contract_format_version":1,"agent":"a","agent":"b"}')


if __name__ == '__main__':
    unittest.main()
