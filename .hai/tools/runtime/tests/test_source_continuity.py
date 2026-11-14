"""Compatibility recovery preserves evidence and refuses uncertain attribution."""
import copy
import json
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from runtime import chronicles, recording
from runtime.storage import SafetyError
from runtime.recording_policy import RecordingInterruption
from runtime.source_continuity import legacy_matches, indexed_matches
from test_chronicles import CoreChronicleTests


class ContinuityTests(CoreChronicleTests):
    def test_foreign_locator_is_rediscovered_without_reinterpreting_path(self):
        import os
        from unittest import mock
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        previous = json.loads((self.base / 'chronicles/core.json').read_text())['sources'][0]
        old_binding = copy.deepcopy(previous['binding'])
        old_binding['path'] = '/foreign/session.jsonl' if os.name == 'nt' else 'C:\\foreign\\session.jsonl'
        with mock.patch('runtime.source_discovery.resolve', return_value={'path': str(self.source)}):
            _, evidence, messages = chronicles.read_assigned(old_binding, previous,
                root=self.root, base=self.base.relative_to(self.root).as_posix())
        self.assertTrue(evidence.get('reconciliation'))
        self.assertEqual(old_binding['path'], str(self.source))
        self.assertEqual(len(messages), 2)

    def test_message_indexes_retain_turn_identity(self):
        self.lines[2]['payload'].update(id='item-a', turn_id='turn-a')
        self.lines[3]['payload'].update(id='item-b', turn_id='turn-a')
        self.save()
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        self.lines[2]['payload']['id'] = 'new-item-a'
        self.lines[3]['payload']['id'] = 'new-item-b'
        self.save()
        result = self.sync()
        self.assertTrue(result['ok'], result)

    def test_rewritten_archived_positions_cannot_allow_duplicate_coverage(self):
        from runtime import activities
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        self.assertTrue(self.close()['ok'])
        created = activities.handle('create', self.root, {'initial_input': '', 'provenance': self.prov}, True)
        self.ident = created['result']['state']['activity_id']; self.base = self.root / created['result']['path']
        self.lines[1:1] = [self.record('event_msg', {'type': 'token_count'}) for _ in range(3)]
        self.save()
        self.assignment['start_position'] = 5
        self.assignment['enabled_intervals'][0]['start']['source_position'] = 5
        result = self.sync(sources=[self.assignment])
        self.assertFalse(result['ok'], result)
        self.assertFalse((self.base / 'chronicles').exists())

    def test_source_identity_conflicts_are_not_optional_interruptions(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        ledger = json.loads((self.base / 'chronicles/core.json').read_text())
        previous = ledger['sources'][0]
        self.lines[0]['payload']['id'] = 'different-session'; self.save()
        with self.assertRaises(SafetyError) as error:
            chronicles.read_assigned(copy.deepcopy(previous['binding']), previous, root=self.root, base=self.base.relative_to(self.root).as_posix())
        self.assertNotIsInstance(error.exception, RecordingInterruption)

    def test_discovery_identity_conflicts_are_not_optional_interruptions(self):
        from unittest import mock
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        ledger = json.loads((self.base / 'chronicles/core.json').read_text()); previous = ledger['sources'][0]
        self.source.unlink()
        with mock.patch('runtime.source_discovery.resolve', side_effect=SafetyError('Host and supplied session identities conflict')):
            with self.assertRaises(SafetyError) as error:
                chronicles.read_assigned(copy.deepcopy(previous['binding']), previous, root=self.root, base=self.base.relative_to(self.root).as_posix())
        self.assertNotIsInstance(error.exception, RecordingInterruption)

    def rewrite(self):
        self.lines.insert(1, self.record('event_msg', {'type': 'token_count'}))
        self.save()

    def test_rebase_retains_original_artifacts_and_records_proof(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        old = (self.base / 'chronicles/core.json').read_bytes()
        segment = next((self.base / 'chronicles').glob('*segment*.md'))
        old_segment = segment.read_bytes()
        self.rewrite()
        preview = self.sync(False); self.assertTrue(preview['ok'], preview)
        self.assertEqual((self.base / 'chronicles/core.json').read_bytes(), old)
        result = self.sync(); self.assertTrue(result['ok'], result)
        self.assertEqual(len(result['result']['reconciliations']), 1)
        ledger = json.loads((self.base / 'chronicles/core.json').read_text())
        self.assertEqual(ledger['sources'][0]['binding']['start_position'], 3)
        history = next((self.base / 'chronicles/history').iterdir())
        self.assertEqual((history / 'core.json').read_bytes(), old)
        self.assertEqual((history / segment.name).read_bytes(), old_segment)
        self.assertTrue((history / 'reconciliation.json').is_file())
        self.assertTrue(recording.handle('verify', self.root, {'activity_id': self.ident}, False)['ok'])
        retained = ledger['artifact_hashes']
        self.assertTrue(self.sync()['ok'])
        newer = json.loads((self.base / 'chronicles/core.json').read_text())
        for path, value in retained.items():
            if path.startswith('chronicles/history/'):
                self.assertEqual(newer['artifact_hashes'][path], value)

    def test_legacy_rebase_handles_headings_inside_exact_message(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        ledger_path = self.base / 'chronicles/core.json'
        ledger = json.loads(ledger_path.read_text()); ledger['sources'][0].pop('message_index')
        ledger_path.write_text(json.dumps(ledger), encoding='utf-8')
        self.rewrite()
        result = self.sync(); self.assertTrue(result['ok'], result)
        self.assertIn('Exact\n\n## Outcome:\n  user text  \n', next((self.base / 'chronicles').glob('*segment*.md')).read_text())

    def test_changed_or_duplicate_messages_are_not_adopted(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        old = (self.base / 'chronicles/core.json').read_bytes()
        self.lines[2]['payload']['message'] = 'changed user'; self.save()
        self.assertFalse(self.sync()['ok'])
        self.assertEqual((self.base / 'chronicles/core.json').read_bytes(), old)

    def test_discontinuous_intervals_cannot_be_silently_rebased(self):
        self.assignment['enabled_intervals'][0]['end'] = {'source_session_id': 'one', 'source_position': 2}
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        self.rewrite()
        self.assertFalse(self.sync()['ok'])

    def test_inserted_exchange_among_retained_messages_is_rejected(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        self.lines.insert(3, self.message('user_message', 'inserted old conversation'))
        self.save(); self.assertFalse(self.sync()['ok'])

    def test_tampered_history_is_still_rejected(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        self.rewrite(); self.assertTrue(self.sync()['ok'])
        next((self.base / 'chronicles/history').rglob('reconciliation.json')).write_bytes(b'changed')
        self.assertFalse(self.sync()['ok'])


class ExactMappingTests(unittest.TestCase):
    def test_turn_identity_survives_regenerated_item_ids(self):
        old = {'role': 'assistant', 'text': 'same', 'source_position': 1,
               'message_id': 'item-1', 'turn_id': 'turn-a'}
        newer = dict(old, source_position=4, message_id='item-99')
        self.assertEqual(indexed_matches([old], [newer]), [newer])
        with self.assertRaises(SafetyError):
            indexed_matches([old], [dict(newer, turn_id='turn-b')])

    def test_legacy_full_framing_delimiter_requires_manual_resolution(self):
        message = {'role': 'user', 'text': 'same\n\n## Outcome:\n\nembedded', 'source_position': 1}
        body = '# Activity transcript\n\n## Source:\n\n{}\n\n## Prompt:\n\n' + message['text'] + '\n\n'
        with self.assertRaises(SafetyError): legacy_matches(body, [message])

    def test_legacy_duplicate_rendering_is_ambiguous(self):
        message = {'role': 'user', 'text': 'same', 'source_position': 1}
        body = '# Activity transcript\n\n## Source:\n\n{}\n\n## Prompt:\n\nsame\n\n'
        with self.assertRaises(SafetyError): legacy_matches(body, [message, dict(message, source_position=2)])

    def test_ids_disambiguate_exact_duplicate_text(self):
        old = {'role': 'user', 'text': 'same', 'source_position': 1, 'message_id': 'a'}
        self.assertEqual(indexed_matches([old], [dict(old, source_position=4), dict(old, source_position=5, message_id='b')])[0]['source_position'], 4)

    def test_reordered_ids_cannot_match(self):
        first = {'role': 'user', 'text': 'a', 'source_position': 1, 'message_id': 'a'}
        second = {'role': 'assistant', 'text': 'b', 'source_position': 2, 'message_id': 'b'}
        with self.assertRaises(SafetyError): indexed_matches([first, second], [dict(second, source_position=4), dict(first, source_position=5)])
