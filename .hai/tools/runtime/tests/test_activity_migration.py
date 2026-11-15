"""Explicit layout migration preserves old evidence and refuses unsafe retries."""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import uuid
from unittest import mock

TOOLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS))
from runtime import activities, activity_migration, chat, chronicles
from runtime.storage import SafetyError, fingerprint


class ActivityMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / '.hai_env/config').mkdir(parents=True)
        (self.root / '.hai/templates').mkdir(parents=True)
        shutil.copy(TOOLS.parent / 'templates/state.json', self.root / '.hai/templates/state.json')
        (self.root / '.hai_env/config/agent_instructions.md').write_bytes(b'')
        (self.root / '.hai_env/config/state.json').write_text(json.dumps({'state_format_version': 3,
            'activities': {'location': '.hai_env/activities'}, 'features': {'chronicles': {'enabled': False}}}), encoding='utf-8')
        self.prov = {'source': 'explicit fixture migration', 'reason': 'verify lossless current migration'}
        self.input = b'  Original legacy input\r\nwith exact bytes\n'
        r = activities.handle('create', self.root, {'initial_input': self.input.decode(),
            'layout_version': 1, 'provenance': self.prov}, True)
        self.assertTrue(r['ok'], r)
        self.aid = r['result']['state']['activity_id']; self.base = r['result']['path']
        self.directory = self.root / self.base
        self.stamp = '2026-11-15T12:34:56Z'

    def migrate(self, apply=True, allow_closed=False):
        return activity_migration.migrate(self.root, self.base, self.aid, self.prov,
            self.stamp, apply, 'Fixture objective', allow_closed=allow_closed)

    def close_fixture(self):
        result = activities.handle('close', self.root, {'activity_id': self.aid, 'outcome': 'completed',
            'archive_label': 'legacy-migration', 'outcome_text': 'Exact final outcome\n  with preserved whitespace  \n',
            'recording': {'status': 'disabled', 'details': 'Synthetic recording disabled'}, 'provenance': self.prov}, True)
        self.assertTrue(result['ok'], result)
        self.base = result['result']['archive_path']; self.directory = self.root / self.base

    def test_closed_archive_is_rejected_by_default_without_changes(self):
        self.close_fixture(); before = self.snapshot()
        for apply in (False, True):
            with self.assertRaisesRegex(SafetyError, 'explicit allow_closed'):
                self.migrate(apply)
            self.assertEqual(before, self.snapshot())

    def test_explicit_closed_conversion_preserves_archive_identity_and_exact_outcome(self):
        invocation = activities.handle('invocation-allocate', self.root, {'activity_id': self.aid,
            'agent': 'software-developer', 'provenance': self.prov}, True)
        self.assertTrue(invocation['ok'], invocation)
        iid = invocation['result']['invocation_id']
        invocation_path = self.root / invocation['result']['path']
        original_manifest = (invocation_path / 'invocation.json').read_bytes()
        (invocation_path / 'retained-review.md').write_bytes(b'Historically committed evidence')
        self.close_fixture(); archive_name = self.directory.name
        state_raw = (self.directory / 'state.json').read_bytes()
        old_state = json.loads(state_raw); outcome = (self.directory / 'outcome.md').read_bytes()
        before = self.snapshot(); result, changed = self.migrate(False, allow_closed=True)
        self.assertEqual(changed, []); self.assertEqual(before, self.snapshot())
        result, changed = self.migrate(allow_closed=True)
        new_state = json.loads((self.directory / 'system/state.json').read_text())
        self.assertEqual({key: new_state[key] for key in old_state}, old_state)
        self.assertEqual((new_state['lifecycle'], new_state['closed_at'], new_state['outcome']),
                         ('closed', old_state['closed_at'], old_state['outcome']))
        self.assertEqual(self.directory.name, archive_name)
        self.assertEqual((self.root / result['history_path'] / 'state.json').read_bytes(), state_raw)
        self.assertEqual((self.root / result['history_path'] / 'outcome.md').read_bytes(), outcome)
        self.assertEqual((self.root / result['history_path'] / 'input.md').read_bytes(), self.input)
        self.assertTrue((self.directory / 'README.md').read_bytes().endswith(b'## Final outcome\n\n' + outcome))
        self.assertFalse((self.directory / 'outcome.md').exists())
        retired = self.directory / 'history/legacy-material/agent-work/software-developer' / iid
        self.assertEqual((retired / 'invocation.json').read_bytes(), original_manifest)
        self.assertEqual((retired / 'retained-review.md').read_bytes(), b'Historically committed evidence')
        self.assertFalse((self.directory / 'work/agents/software-developer' / iid).exists())
        shown = activities.handle('show', self.root, {'activity_id': self.aid}, False)
        self.assertTrue(shown['ok'], shown)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() if p.is_file() else None
                for p in self.root.rglob('*')}

    def test_preview_and_apply_preserve_input_state_chat_and_role_invocations(self):
        old_state = (self.directory / 'state.json').read_bytes()
        (self.directory / 'README.md').write_bytes(b'Legacy custom README')
        (self.directory / 'analysis.md').write_bytes(b'Authored analysis')
        (self.directory / 'files').mkdir(); (self.directory / 'files/unknown.bin').write_bytes(b'\x00\xff')
        (self.directory / 'files/revisions').mkdir(); (self.directory / 'files/revisions/old.md').write_bytes(b'Old draft')
        (self.directory / 'files/test-work').mkdir(); (self.directory / 'files/test-work/check.txt').write_bytes(b'Check')
        (self.directory / 'files/questionnaires').mkdir(); (self.directory / 'files/questionnaires/request.md').write_bytes(b'Authored questions')
        (self.directory / 'unknown-root.data').write_bytes(b'Unknown root bytes')
        invocation = activities.handle('invocation-allocate', self.root, {'activity_id': self.aid,
            'agent': 'software-developer', 'provenance': self.prov}, True)
        self.assertTrue(invocation['ok'], invocation)
        iid = invocation['result']['invocation_id']
        invpath = self.root / invocation['result']['path']; (invpath / 'evidence.bin').write_bytes(b'\x01')
        posted = activities.handle('chat-post', self.root, {'activity_id': self.aid, 'author': 'host-coordinator',
            'text': 'Existing legacy message', 'provenance': self.prov}, True)
        self.assertTrue(posted['ok'], posted)
        old_chat = (self.directory / 'chat.jsonl').read_bytes()
        before = self.snapshot(); planned, changed = self.migrate(False)
        self.assertEqual(changed, []); self.assertEqual(before, self.snapshot())
        result, changed = self.migrate()
        state = json.loads((self.directory / 'system/state.json').read_text())
        original = json.loads(old_state)
        self.assertEqual({k: state[k] for k in original}, original)
        history = self.root / result['history_path']
        self.assertEqual((history / 'state.json').read_bytes(), old_state)
        self.assertEqual((history / 'input.md').read_bytes(), self.input)
        self.assertEqual((history / 'README.md').read_bytes(), b'Legacy custom README')
        raw = (self.directory / 'system/chat.jsonl').read_bytes(); self.assertTrue(raw.startswith(old_chat))
        messages, _, _ = chat.load(self.root, self.base + '/system/chat.jsonl', self.aid)
        self.assertEqual(messages[-1]['text'], self.input.decode())
        self.assertEqual((messages[-1]['role'], messages[-1]['message_type']), ('system', 'legacy-input'))
        self.assertEqual(messages[-1]['message_id'], state['initial_message_id'])
        self.assertEqual((self.directory / ('work/agents/software-developer/' + iid + '/evidence.bin')).read_bytes(), b'\x01')
        self.assertEqual((self.directory / 'results/analysis.md').read_bytes(), b'Authored analysis')
        self.assertEqual((self.directory / 'history/legacy-revisions/old.md').read_bytes(), b'Old draft')
        self.assertEqual((self.directory / 'history/legacy-material/files/unknown.bin').read_bytes(), b'\x00\xff')
        self.assertEqual((self.directory / 'history/legacy-material/root/unknown-root.data').read_bytes(), b'Unknown root bytes')
        self.assertEqual((self.directory / 'results/questionnaires/request.md').read_bytes(), b'Authored questions')
        self.assertFalse((self.directory / 'files').exists())
        shown = activities.handle('show', self.root, {'activity_id': self.aid}, False)
        self.assertTrue(shown['ok'], shown)
        self.assertTrue(activities.handle('discover', self.root, {}, False)['ok'])
        report = json.loads((self.root / result['evidence_path']).read_text())
        self.assertEqual(report['status'], 'completed'); self.assertIn('after_manifest', report)
        self.assertFalse((self.directory / 'input.md').exists()); self.assertFalse((self.directory / 'state.json').exists())

    def test_recording_metadata_moves_without_rewriting_hashes_or_readable_segments(self):
        source = self.root / 'synthetic-source.jsonl'
        rows = [{'type': 'session_meta', 'payload': {'id': 'fixture-source', 'timestamp': self.stamp}},
            {'type': 'event_msg', 'payload': {'type': 'user_message', 'message': 'Exact recorded human text'}},
            {'type': 'event_msg', 'payload': {'type': 'agent_message', 'message': 'Exact recorded answer', 'phase': 'final_answer'}}]
        source.write_text(''.join(json.dumps({**row, 'timestamp': self.stamp}) + '\n' for row in rows), encoding='utf-8')
        binding = {'path': str(source), 'session_id': 'fixture-source', 'representation': 'event_msg', 'start_position': 1,
            'enabled_intervals': [{'start': {'source_session_id': 'fixture-source', 'source_position': 1},
            'end': None, 'provenance': 'Explicit synthetic interval'}]}
        chronicles.synchronize(self.root, self.base, self.aid, {'sources': [binding], 'provenance': self.prov},
            self.stamp, True, fingerprint(self.directory / 'state.json'))
        ledger = (self.directory / 'chronicles/core.json').read_bytes()
        checkpoint = (self.directory / 'chronicles/checkpoint.json').read_bytes()
        segment = json.loads(ledger)['sources'][0]['segment_path']
        transcript = (self.directory / segment).read_bytes()
        self.migrate()
        self.assertEqual((self.directory / 'system/chronicles/core.json').read_bytes(), ledger)
        self.assertEqual((self.directory / 'system/chronicles/checkpoint.json').read_bytes(), checkpoint)
        self.assertEqual((self.directory / segment).read_bytes(), transcript)
        self.assertEqual(chronicles.verify(self.root, self.base, self.aid)['status'], 'verified')

    def test_empty_legacy_input_is_preserved_as_explicit_empty_legacy_context(self):
        (self.directory / 'input.md').write_bytes(b'')
        result, changed = self.migrate()
        messages, _, _ = chat.load(self.root, self.base + '/system/chat.jsonl', self.aid)
        self.assertEqual(messages[0]['text'], ''); self.assertEqual(messages[0]['role'], 'system')

    def test_target_collision_and_mixed_layout_refuse_without_changes(self):
        (self.directory / 'analysis.md').write_bytes(b'Source')
        (self.directory / 'results').mkdir(); (self.directory / 'results/analysis.md').write_bytes(b'Existing destination')
        before = self.snapshot()
        for apply in (False, True):
            with self.assertRaisesRegex(SafetyError, 'destination already exists'):
                self.migrate(apply)
            self.assertEqual(before, self.snapshot())
        (self.directory / 'results/analysis.md').unlink(); (self.directory / 'system').mkdir()
        before = self.snapshot()
        with self.assertRaisesRegex(SafetyError, 'Mixed'):
            self.migrate()
        self.assertEqual(before, self.snapshot())

    def test_partial_move_is_retained_and_never_automatically_reused(self):
        (self.directory / 'analysis.md').write_bytes(b'Source')
        original_move = activity_migration._move
        calls = []
        def failing_move(*args):
            calls.append(True)
            if len(calls) == 2:
                raise SafetyError('Injected interrupted move')
            return original_move(*args)
        with mock.patch.object(activity_migration, '_move', side_effect=failing_move):
            with self.assertRaisesRegex(SafetyError, 'Injected') as caught:
                self.migrate()
        self.assertTrue(caught.exception.changed_files)
        report = self.directory / 'evidence/migrations/activity-layout.json'
        self.assertEqual(json.loads(report.read_text())['status'], 'partial')
        retained = self.snapshot()
        with self.assertRaises(SafetyError): self.migrate()
        self.assertEqual(retained, self.snapshot())

    def test_retained_workflow_writer_blocks_even_preview(self):
        with mock.patch('runtime.workflows.runs', return_value=[({'executor': {'writers_ended': False}}, None, None, None)]):
            before = self.snapshot()
            for apply in (False, True):
                with self.assertRaisesRegex(SafetyError, 'unresolved writers'):
                    self.migrate(apply)
                self.assertEqual(before, self.snapshot())

    def test_hardlinked_source_is_rejected_without_changes(self):
        try:
            os.link(self.directory / 'input.md', self.root / 'input-alias.md')
        except OSError:
            self.skipTest('Hard-link creation unavailable')
        before = self.snapshot()
        with self.assertRaises(SafetyError):
            self.migrate()
        self.assertEqual(before, self.snapshot())
