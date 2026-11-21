"""Availability may interrupt optional recording, never falsify verification."""
import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_chronicles as fixtures
from runtime import activities, environment, recording
from runtime.recording_policy import effective, recoverable, RecordingInterruption
from runtime.storage import SafetyError


class RecordingPolicyTests(unittest.TestCase):
    setUp = fixtures.CoreChronicleTests.setUp
    tearDown = fixtures.CoreChronicleTests.tearDown
    save_state = fixtures.CoreChronicleTests.save_state
    record = fixtures.CoreChronicleTests.record
    message = fixtures.CoreChronicleTests.message
    save = fixtures.CoreChronicleTests.save
    sync = fixtures.CoreChronicleTests.sync
    close = fixtures.CoreChronicleTests.close

    def mode(self, value=None):
        self.state['features']['chronicles'].pop('mode', None)
        if value is not None:
            self.state['features']['chronicles']['mode'] = value
        self.save_state()

    def test_missing_mode_defaults_best_effort_and_mandatory_is_strict(self):
        self.mode()
        self.assertFalse(effective(self.state)['required'])
        self.assertTrue(effective(self.state, True)['required'])
        self.mode('required')
        self.assertTrue(effective(self.state)['required'])
        self.state['features']['chronicles']['enabled'] = False
        self.assertFalse(effective(self.state)['required'])
        self.assertTrue(effective(self.state, True)['required'])

    def test_retired_recording_controls_are_rejected_without_mutation(self):
        before=(self.root/'.hai_env/config/state.json').read_bytes()
        for key,value in [('enabled',False),('mode','required'),('record_every_prompts',5)]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                environment.handle('environment/configure', self.root,
                    {'changes': {'features.chronicles.'+key:value}, 'provenance':self.prov},True)
        self.assertEqual(before,(self.root/'.hai_env/config/state.json').read_bytes())

    def test_best_effort_close_records_gap_and_preserves_retained_bytes(self):
        self.mode()
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        before = {p.relative_to(self.base): p.read_bytes() for p in (self.base / 'chronicles').iterdir()}
        with mock.patch('runtime.chronicles.synchronize', side_effect=RecordingInterruption('Source format is unsupported')):
            result = self.close()
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['result']['recording']['status'], 'unavailable')
        archive = self.root / result['result']['archive_path']
        self.assertIn('coverage gap', (archive / 'outcome.md').read_text())
        for relative, original in before.items():
            self.assertEqual((archive / relative).read_bytes(), original)

    def test_required_and_independently_mandatory_close_still_block(self):
        for mode, mandatory in [('required', False), ('best_effort', True)]:
            self.mode(mode)
            with mock.patch('runtime.chronicles.synchronize', side_effect=RecordingInterruption('Unavailable source')):
                result = self.close(recording_requirement={'enabled': True, 'mandatory': mandatory})
            self.assertFalse(result['ok'], result)
            self.assertFalse((self.base / 'outcome.md').exists())

    def test_integrity_and_partial_errors_cannot_be_downgraded(self):
        self.mode()
        for error in [SafetyError('Chronicle artifact changed'), RecordingInterruption('partial', ['chronicles/x'])]:
            self.assertFalse(recoverable(error))
            with mock.patch('runtime.chronicles.synchronize', side_effect=error):
                result = self.close()
            self.assertFalse(result['ok'], result)
            self.assertFalse((self.base / 'outcome.md').exists())

    def test_explicit_synchronize_does_not_claim_success_for_optional_gaps(self):
        self.mode()
        with mock.patch('runtime.chronicles.synchronize', side_effect=RecordingInterruption('Source format is unsupported')):
            result = self.sync()
        self.assertFalse(result['ok'], result)
        self.assertEqual(result['changed_files'], [])

    def test_real_missing_source_can_close_only_in_best_effort_mode(self):
        self.mode()
        sid = 'ae9f1b34-0a77-4eae-bdbf-00d035c57d4b'
        self.lines[0]['payload']['id'] = sid
        self.assignment['session_id'] = sid
        self.assignment['enabled_intervals'][0]['start']['source_session_id'] = sid
        self.save()
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        self.source.unlink()
        with mock.patch.dict(os.environ, {'CODEX_THREAD_ID': sid,
                'CODEX_HOME': str(self.root / 'missing-host-store')}, clear=True):
            explicit = self.sync()
            self.assertFalse(explicit['ok'], explicit)
            result = self.close()
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['result']['recording']['status'], 'unavailable')

    def test_real_tampered_artifact_blocks_best_effort_closure(self):
        self.mode()
        result = self.sync(sources=[self.assignment])
        self.assertTrue(result['ok'], result)
        segment = self.base / result['result']['segments'][0]
        segment.write_text('unauthorized edit', encoding='utf-8')
        self.source.unlink()
        result = self.close()
        self.assertFalse(result['ok'], result)
        self.assertIn('artifact changed', str(result['issues']))
        self.assertEqual(segment.read_text(), 'unauthorized edit')
        self.assertFalse((self.base / 'outcome.md').exists())


if __name__ == '__main__':
    unittest.main()
