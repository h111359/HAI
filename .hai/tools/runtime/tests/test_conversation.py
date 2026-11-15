"""Persistent typed conversation is independent of optional source chronicles."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

TOOLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS))
from activity_layout import artifact
from runtime import activities, chat


class ConversationTests(unittest.TestCase):
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
        self.prov = {'source': 'actual synthetic user instruction', 'reason': 'verify persistent conversation'}
        self.input = '  Human instruction\r\nverbatim whitespace\n' + '\u03bb' * 40000
        self.created = activities.handle('create', self.root, {'initial_input': self.input, 'provenance': self.prov}, True)
        self.assertTrue(self.created['ok'], self.created)
        self.aid = self.created['result']['state']['activity_id']
        self.base = self.created['result']['path']
        self.path = self.root / artifact(self.root, self.base, 'chat.jsonl')

    def post(self, **kwargs):
        return activities.handle('chat-post', self.root, {'activity_id': self.aid, 'author': 'host-coordinator',
            'text': 'Recorded message', 'role': 'assistant', 'message_type': 'reply', 'provenance': self.prov, **kwargs}, True)

    def read(self):
        r = activities.handle('chat-read', self.root, {'activity_id': self.aid}, False)
        self.assertTrue(r['ok'], r)
        return r['result']['messages']

    def test_new_activity_keeps_untruncated_human_input_without_chronicles(self):
        messages = self.read()
        self.assertEqual(messages[0]['text'], self.input)
        self.assertEqual((messages[0]['role'], messages[0]['message_type']), ('human', 'instruction'))
        self.assertIn('/system/chat.jsonl', str(self.path).replace('\\', '/'))
        self.assertFalse((self.root / self.base / 'input.md').exists())
        self.assertFalse((self.root / self.base / 'chronicles').exists())
        with mock.patch('runtime.source_discovery.resolve', side_effect=AssertionError('Conversation must not discover transcripts')):
            self.assertTrue(self.post()['ok'])

    def test_roles_and_repeated_equal_text_keep_distinct_occurrences_and_old_prefix(self):
        prefix = self.path.read_bytes(); inode = self.path.stat().st_ino
        for role, kind in [('human', 'instruction'), ('assistant', 'reply'), ('agent', 'coordination'), ('system', 'coordination')]:
            result = self.post(role=role, message_type=kind, text='Identical words')
            self.assertTrue(result['ok'], result)
        messages = self.read()
        self.assertEqual([m['role'] for m in messages[1:]], ['human', 'assistant', 'agent', 'system'])
        self.assertEqual(len({m['message_id'] for m in messages}), 5)
        self.assertEqual(self.path.stat().st_ino, inode); self.assertTrue(self.path.read_bytes().startswith(prefix))

    def test_stable_source_id_replay_is_idempotent_and_conflict_preserves_bytes(self):
        result = self.post(source_message_id='host-session:message-42')
        self.assertTrue(result['ok'], result); before = self.path.read_bytes()
        result = self.post(source_message_id='host-session:message-42')
        self.assertTrue(result['ok'], result); self.assertEqual(result['changed_files'], [])
        self.assertEqual(before, self.path.read_bytes()); self.assertEqual(len(self.read()), 2)
        conflict = self.post(source_message_id='host-session:message-42', text='Changed content')
        self.assertFalse(conflict['ok']); self.assertEqual(before, self.path.read_bytes())

    def test_mixed_legacy_prefix_is_retained_while_new_records_are_typed(self):
        first = self.read()[0]
        first.pop('role'); first.pop('message_type'); first.pop('delivery_status'); first['chat_format_version'] = 1
        first['text'] = 'Existing old coordination message'
        prefix = chat.encode(first); self.path.write_bytes(prefix)
        self.assertTrue(self.post()['ok'])
        self.assertTrue(self.path.read_bytes().startswith(prefix))
        self.assertEqual([m['chat_format_version'] for m in self.read()], [1, 2])

    def test_assistant_delivery_is_prepared_unless_host_explicitly_observed_delivery(self):
        self.assertTrue(self.post(text='Prepared final reply')['ok'])
        delivered = self.post(text='Previously delivered reply', delivery_status='delivered')
        self.assertTrue(delivered['ok'], delivered)
        self.assertEqual([m['delivery_status'] for m in self.read()], ['received', 'prepared', 'delivered'])
