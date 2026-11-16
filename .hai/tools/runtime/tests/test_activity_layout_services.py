"""Layout-aware service contracts, including unchanged logical recording evidence."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import uuid

TOOLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS))
from activity_layout import artifact
from runtime import chronicles, invocations, usage, workflows
from runtime.storage import SafetyError, fingerprint
from run_tests import test_work_path


class LayoutServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.base = '.hai_env/activities/00000000_000000_active'
        self.aid = str(uuid.uuid4())
        self.prov = {'source': 'synthetic service fixture', 'reason': 'verify layout contracts'}
        self.stamp = '2026-11-15T00:00:00Z'
        self.directory = self.root / self.base
        (self.directory / 'system').mkdir(parents=True)
        (self.root / '.hai_env/config').mkdir(parents=True)
        self.environment = {'state_format_version': 3, 'activities': {'location': '.hai_env/activities'},
            'features': {'chronicles': {'enabled': True, 'record_every_prompts': 5}}}
        (self.root / '.hai_env/config/state.json').write_text(json.dumps(self.environment), encoding='utf-8')
        (self.directory / 'system/state.json').write_text(json.dumps({'activity_layout_version': 2,
            'activity_id': self.aid, 'lifecycle': 'active'}), encoding='utf-8')

    def state_fingerprint(self):
        return fingerprint(self.root / artifact(self.root, self.base, 'state.json'))

    def test_usage_and_invocation_paths_are_owned_by_system_and_role(self):
        result, changed = usage.update(self.root, self.base, self.aid, {'provenance': self.prov},
            self.stamp, True, self.state_fingerprint())
        self.assertEqual(result['path'], self.base + '/system/usage.md')
        self.assertEqual(result['checkpoint_path'], self.base + '/system/usage.json')
        self.assertTrue(usage.read(self.root, self.base, self.aid)['available'])
        self.assertFalse((self.directory / 'usage.json').exists())
        request = {'role': 'software-developer', 'provenance': self.prov}
        allocated = invocations.prepare(self.root, self.base, self.aid, request, self.stamp)
        self.assertIn('/work/agents/software-developer/', allocated['path'])
        self.assertFalse((self.root / allocated['path']).exists())
        allocated, changed = invocations.allocate(self.root, self.base, allocated, self.state_fingerprint())
        self.assertTrue(allocated['allocated'])
        executor = {'handle': 'actual-fixture-handle', 'mode': 'spawned', 'invocation_id': allocated['invocation_id'],
            'writers_ended': True, 'evidence': 'Fixture host observed stopped worker'}
        self.assertEqual(workflows._verified_executor(self.root, {'path': self.base, 'activity_id': self.aid},
            {'role': 'software-developer'}, executor), executor)
        self.assertFalse((self.directory / 'files').exists())

    def test_executor_understands_only_supported_invocation_identity_formats(self):
        allocated = invocations.prepare(self.root, self.base, self.aid,
            {'role': 'software-developer', 'provenance': self.prov}, self.stamp)
        allocated, _ = invocations.allocate(self.root, self.base, allocated, self.state_fingerprint())
        path = self.root / allocated['metadata_path']
        metadata = json.loads(path.read_bytes())
        executor = {'handle': 'fixture-handle', 'mode': 'spawned', 'invocation_id': allocated['invocation_id'],
                    'writers_ended': True, 'evidence': 'Observed fixture stopped'}
        step = {'role': 'software-developer'}
        context = {'path': self.base, 'activity_id': self.aid}
        legacy = {**metadata, 'invocation_format_version': 1, 'agent': metadata['role']}
        del legacy['role']
        path.write_text(json.dumps(legacy), encoding='utf-8')
        self.assertEqual(workflows._verified_executor(self.root, context, step, executor), executor)
        for invalid in (True, 3, None):
            path.write_text(json.dumps({**legacy, 'invocation_format_version': invalid}), encoding='utf-8')
            with self.assertRaises(SafetyError):
                workflows._verified_executor(self.root, context, step, executor)

    def test_v2_recording_preserves_logical_hash_keys_and_readable_segment_paths(self):
        source = self.root / 'source.jsonl'
        records = [
            {'type': 'session_meta', 'payload': {'id': 'fixture-session', 'timestamp': self.stamp}},
            {'type': 'event_msg', 'payload': {'type': 'user_message', 'message': 'Exact human\n  bytes  '}},
            {'type': 'event_msg', 'payload': {'type': 'agent_message', 'message': 'Exact reply', 'phase': 'final_answer'}}]
        for record in records:
            record['timestamp'] = self.stamp
        source.write_text(''.join(json.dumps(row) + '\n' for row in records), encoding='utf-8')
        binding = {'path': str(source), 'session_id': 'fixture-session', 'start_position': 1,
            'representation': 'event_msg', 'enabled_intervals': [{'start': {'source_session_id': 'fixture-session',
            'source_position': 1}, 'end': None, 'provenance': 'Synthetic explicit assignment'}]}
        request = {'sources': [binding], 'provenance': self.prov}
        preview, changed = chronicles.synchronize(self.root, self.base, self.aid, request, self.stamp,
            False, self.state_fingerprint())
        self.assertEqual(changed, []); self.assertFalse((self.directory / 'chronicles').exists())
        result, changed = chronicles.synchronize(self.root, self.base, self.aid, request, self.stamp,
            True, self.state_fingerprint())
        self.assertEqual(result['checkpoint_path'], self.base + '/system/chronicles/checkpoint.json')
        ledger, fp = chronicles.load(self.root, self.base, self.aid)
        self.assertIn('chronicles/checkpoint.json', ledger['artifact_hashes'])
        self.assertNotIn('system/chronicles/checkpoint.json', ledger['artifact_hashes'])
        segment = ledger['sources'][0]['segment_path']
        self.assertTrue(segment.startswith('chronicles/')); self.assertTrue(segment.endswith('.md'))
        self.assertTrue((self.directory / segment).is_file())
        checkpoint = json.loads((self.directory / 'system/chronicles/checkpoint.json').read_text())
        self.assertEqual(checkpoint['verified_ranges'][0]['segment_path'], segment)
        before = (self.directory / segment).read_bytes()
        self.assertEqual(chronicles.verify(self.root, self.base, self.aid)['status'], 'verified')
        self.assertEqual(before, (self.directory / segment).read_bytes())
        self.assertFalse((self.directory / 'chronicles/core.json').exists())

    def test_test_runner_accepts_current_owned_areas_and_legacy_areas(self):
        for tail in ('work/test-work', 'work/agents/software-developer/' + str(uuid.uuid4()) + '/test-work',
                     'files/test-work', 'files/agent-invocations/' + str(uuid.uuid4()) + '/test-work'):
            self.assertEqual(test_work_path(self.root, self.base + '/' + tail), self.directory / tail)
        with self.assertRaises(Exception):
            test_work_path(self.root, self.base + '/results/test-work')
