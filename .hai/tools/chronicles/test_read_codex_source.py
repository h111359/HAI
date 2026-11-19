"""Conservative Codex source fixtures; no real session access or writes by reader."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from read_codex_source import read_source

STAMP = "2026-11-02T08:00:00Z"


class CodexSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name).resolve()/"source.jsonl"

    def record(self, kind, payload):
        return {"timestamp": STAMP, "type": kind, "payload": payload}

    def save(self, records):
        meta = self.record("session_meta", {"id": "session", "timestamp": STAMP})
        raw = "\n".join(json.dumps(record, ensure_ascii=False) for record in [meta, *records])+"\n"
        self.source.write_text(raw, encoding="utf-8")
        return self.source.read_bytes()

    def test_events_preserve_text_repeats_positions_and_exclude_tools_progress(self):
        exact = "  café\n**same**\u2028text\t "
        records = [self.record("event_msg", {"type": "user_message", "message": exact}),
                   self.record("response_item", {"type": "message", "role": "user", "content": [{"type": "input_text", "text": exact}]}),
                   self.record("event_msg", {"type": "user_message", "message": exact}),
                   self.record("event_msg", {"type": "agent_message", "phase": "commentary", "message": "progress"}),
                   self.record("response_item", {"type": "function_call", "arguments": "secret tool metadata"}),
                   self.record("event_msg", {"type": "agent_message", "phase": "final_answer", "message": "Exact final.\n"})]
        before = self.save(records)
        result = read_source(self.source, "event_msg", "session")
        self.assertTrue(result["ok"], result)
        self.assertEqual([item["text"] for item in result["messages"]], [exact, exact, "Exact final.\n"])
        self.assertEqual([item["source_position"] for item in result["messages"]], [1, 3, 6])
        self.assertEqual(result["source_sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(self.source.read_bytes(), before)

    def test_response_items_use_one_representation_and_exact_block_concatenation(self):
        self.save([self.record("response_item", {"type": "message", "role": "user", "id": "original",
                   "content": [{"type": "input_text", "text": "a "}, {"type": "input_text", "text": " b"}]}),
                   self.record("event_msg", {"type": "user_message", "message": "a  b"}),
                   self.record("response_item", {"type": "message", "role": "assistant", "phase": "final_answer",
                   "content": [{"type": "output_text", "text": "result"}]})])
        result = read_source(self.source, "response_item")
        self.assertTrue(result["ok"], result)
        self.assertEqual([item["text"] for item in result["messages"]], ["a  b", "result"])
        self.assertEqual(result["messages"][0]["message_id"], "original")

    def test_missing_source_and_wrong_session_are_explicit(self):
        self.assertFalse(read_source(self.source, "event_msg")["ok"])
        self.save([])
        self.assertFalse(read_source(self.source, "event_msg", "another")["ok"])

    def test_unknown_final_phase_does_not_become_outcome(self):
        self.save([self.record("event_msg", {"type": "agent_message", "message": "maybe progress"})])
        result = read_source(self.source, "event_msg")
        self.assertFalse(result["ok"])
        self.assertEqual(result["messages"], [])

    def test_consistent_resume_metadata_preserves_positions_and_exact_text(self):
        for representation in ("event_msg", "response_item"):
            with self.subTest(representation=representation):
                if representation == "event_msg":
                    first = self.record(representation, {"type": "user_message", "message": "exact prompt\n"})
                    final = self.record(representation, {"type": "agent_message", "phase": "final_answer", "message": "exact final\n"})
                else:
                    first = self.record(representation, {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "exact prompt\n"}]})
                    final = self.record(representation, {"type": "message", "role": "assistant", "phase": "final_answer", "content": [{"type": "output_text", "text": "exact final\n"}]})
                resumed = {"type": "session_meta", "timestamp": "2026-11-02T09:00:00Z",
                           "payload": {"id": "session", "timestamp": STAMP, "memory_mode": "resumed"}}
                before = self.save([first, resumed, final])
                result = read_source(self.source, representation, "session")
                self.assertTrue(result["ok"], result)
                self.assertEqual(result["original_started_at"], STAMP)
                self.assertEqual([item["source_position"] for item in result["messages"]], [1, 3])
                self.assertEqual([item["text"] for item in result["messages"]], ["exact prompt\n", "exact final\n"])
                self.assertEqual(self.source.read_bytes(), before)

    def test_conflicting_or_invalid_resume_identity_still_blocks(self):
        for payload in ({"id": "different", "timestamp": STAMP},
                        {"id": "session", "timestamp": "2026-11-02T09:00:00Z"},
                        {"id": "session", "timestamp": None},
                        {"timestamp": STAMP}):
            with self.subTest(payload=payload):
                self.save([self.record("session_meta", payload)])
                result = read_source(self.source, "event_msg", "session")
                self.assertFalse(result["ok"], result)
                self.assertEqual(result["source_session_id"], "session")
                self.assertEqual(result["original_started_at"], STAMP)

    def test_explicit_prefix_preserves_identity_and_exposes_later_eligible_source(self):
        original = self.save([
            self.record("event_msg", {"type": "user_message", "message": "closure request\n"}),
            self.record("event_msg", {"type": "agent_message", "phase": "final_answer", "message": "saved earlier final\n"}),
        ])
        prefix = self.source.with_name("explicit-prefix.jsonl")
        prefix.write_bytes(original)
        with self.source.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(self.record("event_msg", {"type": "token_count", "info": {}}))+"\n")
        snapshot = read_source(prefix, "event_msg", "session")
        current = read_source(self.source, "event_msg", "session")
        self.assertTrue(snapshot["ok"], snapshot)
        self.assertTrue(current["ok"], current)
        self.assertEqual(snapshot["source_session_id"], current["source_session_id"])
        self.assertEqual(snapshot["original_started_at"], current["original_started_at"])
        self.assertEqual(snapshot["messages"], current["messages"])
        self.assertEqual([item["source_position"] for item in snapshot["messages"]], [1, 2])
        self.assertNotEqual(snapshot["source_sha256"], current["source_sha256"])
        self.assertTrue(self.source.read_bytes().startswith(prefix.read_bytes()))
        with self.source.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(self.record("event_msg", {"type": "user_message", "message": "new eligible prompt\n"}))+"\n")
        newer = read_source(self.source, "event_msg", "session")
        self.assertTrue(newer["ok"], newer)
        self.assertEqual([item["source_position"] for item in newer["messages"] if item["source_position"] > 2], [4])
        self.assertEqual(prefix.read_bytes(), original)

    def test_truncated_source_keeps_gap_not_complete_coverage(self):
        self.save([self.record("event_msg", {"type": "user_message", "message": "preceding"})])
        with self.source.open("a") as stream:
            stream.write('{"type":')
        result = read_source(self.source, "event_msg")
        self.assertFalse(result["ok"])
        self.assertEqual(len(result["messages"]), 1)

    def test_missing_identity_timestamp_and_unsupported_content_block(self):
        for record in (self.record("session_meta", {"id": "another", "timestamp": STAMP}),
                       {"type": "event_msg", "payload": {"type": "user_message", "message": "no time"}},
                       self.record("response_item", {"type": "message", "role": "user", "content": [{"type": "input_image"}]})):
            with self.subTest(record=record):
                self.save([record])
                self.assertFalse(read_source(self.source, "response_item" if record["type"]=="response_item" else "event_msg")["ok"])
        self.source.write_text(json.dumps(self.record("event_msg", {"type": "user_message", "message": "no session"})), encoding='utf-8')
        self.assertFalse(read_source(self.source, "event_msg")["ok"])

    def test_duplicate_keys_and_blank_records_fail(self):
        for suffix in ('{"type":"event_msg","type":"response_item","payload":{}}\n', '\n'):
            self.save([])
            with self.source.open("a") as stream:
                stream.write(suffix)
            self.assertFalse(read_source(self.source, "event_msg")["ok"])

    def test_malformed_message_discriminators_never_claim_complete_source(self):
        cases = [
            ({"timestamp": STAMP, "payload": {"type": "user_message", "message": "lost"}}, "event_msg"),
            (self.record("event_msg", {"message": "lost"}), "event_msg"),
            (self.record("response_item", {"type": "message", "content": [{"type": "input_text", "text": "lost"}]}), "response_item"),
            (self.record("response_item", {"role": "user", "content": [{"type": "input_text", "text": "lost"}]}), "response_item"),
            (self.record("event_msg", {"type": "unknown_message", "message": "lost"}), "event_msg"),
        ]
        for record, representation in cases:
            with self.subTest(record=record):
                self.save([record])
                result = read_source(self.source, representation)
                self.assertFalse(result["ok"], result)
                self.assertTrue(result["issues"])

    def test_known_excluded_events_and_instruction_messages_stay_excluded(self):
        self.save([self.record("event_msg", {"type": "token_count", "info": {}}),
                   self.record("event_msg", {"type": "warning", "message": "not a human prompt"}),
                   self.record("response_item", {"type": "message", "role": "developer", "content": [{"type": "input_text", "text": "internal"}]})])
        for representation in ("event_msg", "response_item"):
            result = read_source(self.source, representation)
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["messages"], [])

    def test_noncanonical_link_source_rejected(self):
        self.save([])
        link = self.source.with_name("link.jsonl")
        try:
            link.symlink_to(self.source)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        self.assertFalse(read_source(link, "event_msg")["ok"])

    def test_cli_missing_source_is_machine_readable(self):
        result = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("read_codex_source.py")),
                                 str(self.source), "--representation", "event_msg"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["ok"])
        self.assertFalse(self.source.exists())

    def test_completed_items_keep_exact_text_and_exclude_nonfinal_work(self):
        self.save([
            self.record('event_msg', {'type': 'item_completed', 'turn_id': 'turn-1',
                'item': {'type': 'UserMessage', 'id': 'item-1',
                         'content': [{'type': 'text', 'text': '  café\n'}, {'type': 'text', 'text': 'next'}]}}),
            self.record('event_msg', {'type': 'item_completed',
                'item': {'type': 'AgentMessage', 'phase': 'commentary', 'content': []}}),
            self.record('event_msg', {'type': 'item_completed',
                'item': {'type': 'Reasoning', 'text': 'never record'}}),
            self.record('event_msg', {'type': 'item_completed',
                'item': {'type': 'SubAgentActivity', 'text': 'not a human message'}}),
            self.record('event_msg', {'type': 'item_completed',
                'item': {'type': 'AgentMessage', 'id': 'item-2', 'phase': 'final_answer',
                         'content': [{'type': 'Text', 'text': 'Done.\n'}]}}),
        ])
        result = read_source(self.source, 'auto', 'session')
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['representation'], 'event_msg')
        self.assertEqual(result['adapters'], ['codex-completed-item-v1'])
        self.assertEqual([m['text'] for m in result['messages']], ['  café\nnext', 'Done.\n'])
        self.assertEqual(result['messages'][0]['turn_id'], 'turn-1')

    def test_completed_compactions_preserve_chat_positions_and_source_bytes(self):
        compaction = self.record('event_msg', {'type': 'item_completed',
            'thread_id': 'session', 'turn_id': 'turn',
            'item': {'type': 'ContextCompaction', 'id': 'compaction-id'},
            'started_at_ms': 1794753057464, 'completed_at_ms': 1794753147522})
        exact = '  request\nwith whitespace\t '
        before = self.save([compaction,
            self.record('event_msg', {'type': 'user_message', 'message': exact}),
            compaction,
            self.record('event_msg', {'type': 'agent_message',
                'phase': 'final_answer', 'message': 'Done.\n'}), compaction])
        for representation in ('event_msg', 'auto'):
            with self.subTest(representation=representation):
                result = read_source(self.source, representation, 'session')
                self.assertTrue(result['ok'], result)
                self.assertEqual([m['text'] for m in result['messages']], [exact, 'Done.\n'])
                self.assertEqual([m['source_position'] for m in result['messages']], [2, 4])
                self.assertEqual(result['source_sha256'], hashlib.sha256(before).hexdigest())
                self.assertEqual(self.source.read_bytes(), before)

    def test_changed_or_incomplete_compaction_items_are_not_silently_discarded(self):
        for item in ({'type': 'ContextCompaction'},
                     {'type': 'ContextCompaction', 'id': ''},
                     {'type': 'ContextCompaction', 'id': 7},
                     {'type': 'ContextCompaction', 'id': 'x', 'content': [{'type': 'text', 'text': 'unknown'}]},
                     {'type': 'FutureCompaction', 'id': 'x'}):
            with self.subTest(item=item):
                self.save([self.record('event_msg', {'type': 'item_completed', 'item': item})])
                self.assertFalse(read_source(self.source, 'auto')['ok'])

    def test_reviewed_web_extension_results_are_not_conversation(self):
        extension = {'type': 'Extension', 'kind': 'web.search', 'id': 'tool-id',
                     'query': 'task data', 'action': {'type': 'search'},
                     'results': [{'text': 'untrusted tool text is not a user message'}]}
        for action in ({'type': 'search'}, {'type': 'openPage', 'url': 'https://example.test'}):
            extension['action'] = action
            self.save([
                self.record('event_msg', {'type': 'user_message', 'message': 'request'}),
                self.record('event_msg', {'type': 'item_completed', 'item': extension}),
                self.record('event_msg', {'type': 'agent_message', 'phase': 'final_answer', 'message': 'answer'})])
            result = read_source(self.source, 'auto', 'session')
            self.assertTrue(result['ok'], result)
            self.assertEqual([m['text'] for m in result['messages']], ['request', 'answer'])
            self.assertEqual([m['source_position'] for m in result['messages']], [1, 3])
        for change in ({'kind': 'future.chat'}, {'content': 'unknown message'}, {'results': None},
                       {'id': ''}, {'query': None}, {'action': []}):
            item = dict(extension, **change)
            self.save([self.record('event_msg', {'type': 'item_completed', 'item': item})])
            self.assertFalse(read_source(self.source, 'auto')['ok'])

    def test_partial_mode_keeps_exact_messages_on_both_sides_of_unknown_records(self):
        raw = self.save([
            self.record('event_msg', {'type': 'user_message', 'message': '  before\n'}),
            self.record('event_msg', {'type': 'future_chat', 'text': 'opaque unknown payload'}),
            self.record('future_outer', {'content': 'opaque outer payload'}),
            self.record('event_msg', {'type': 'agent_message', 'message': 'after\t ', 'phase': 'final_answer'})])
        result = read_source(self.source, 'auto', 'session', allow_partial=True)
        self.assertTrue(result['usable'], result)
        self.assertFalse(result['ok']); self.assertFalse(result['complete'])
        self.assertEqual([m['text'] for m in result['messages']], ['  before\n', 'after\t '])
        self.assertEqual([m['source_position'] for m in result['messages']], [1, 4])
        self.assertEqual([g['source_position'] for g in result['gaps']], [2, 3])
        self.assertNotIn('opaque', str(result['gaps']))
        self.assertEqual(self.source.read_bytes(), raw)
        self.assertFalse(read_source(self.source, 'event_msg')['usable'])

    def test_reviewed_outer_metadata_is_excluded_but_future_shapes_remain_gaps(self):
        usage = {k: 'id' for k in ('thread_id', 'turn_id', 'session_id', 'root_turn_id', 'response_id')}
        usage.update({k: {} for k in ('usage', 'turn_token_usage', 'thread_token_usage')})
        records = [self.record('event_msg', {'type': 'user_message', 'message': 'request'}),
                   self.record('token_usage_record', usage),
                   self.record('inter_agent_communication_metadata', {'trigger_turn': True}),
                   self.record('world_state', {'full': False, 'state': {'tool_data': 'not conversation'}}),
                   self.record('event_msg', {'type': 'agent_message', 'phase': 'final_answer', 'message': 'answer'})]
        self.save(records)
        result = read_source(self.source, 'auto', 'session', allow_partial=True)
        self.assertTrue(result['complete'], result)
        self.assertEqual([m['text'] for m in result['messages']], ['request', 'answer'])
        self.assertEqual([m['source_position'] for m in result['messages']], [1, 5])
        for kind, payload in [('token_usage_record', dict(usage, content='unreviewed')),
                              ('inter_agent_communication_metadata', {'trigger_turn': 'yes'}),
                              ('world_state', {'full': True, 'state': [], 'message': 'unreviewed'}),
                              ('future_chat', {'text': 'unknown'})]:
            self.save([records[0], self.record(kind, payload), records[-1]])
            result = read_source(self.source, 'auto', 'session', allow_partial=True)
            self.assertTrue(result['usable'], result)
            self.assertFalse(result['complete'])
            self.assertEqual(result['gaps'][0]['source_position'], 2)

    def test_partial_auto_does_not_hide_gap_only_event_view_with_response_fallback(self):
        self.save([
            self.record('event_msg', {'type': 'future_chat', 'text': 'not understood'}),
            self.record('response_item', {'type': 'message', 'role': 'user',
                'content': [{'type': 'input_text', 'text': 'alternative view'}]})])
        result = read_source(self.source, 'auto', 'session', allow_partial=True)
        self.assertTrue(result['usable'], result)
        self.assertEqual(result['representation'], 'event_msg')
        self.assertEqual(result['messages'], [])
        self.assertEqual(result['gaps'][0]['source_position'], 1)

    def test_partial_mode_does_not_waive_identity_or_json_integrity(self):
        for record in (self.record('session_meta', {'id': 'wrong', 'timestamp': STAMP}),
                       self.record('session_meta', {'timestamp': STAMP})):
            self.save([self.record('event_msg', {'type': 'user_message', 'message': 'supported'}), record])
            result = read_source(self.source, 'event_msg', 'session', allow_partial=True)
            self.assertFalse(result['usable'], result)
        self.save([self.record('event_msg', {'type': 'user_message', 'message': 'supported'})])
        with self.source.open('a') as stream: stream.write('{"type":')
        self.assertFalse(read_source(self.source, 'event_msg', 'session', allow_partial=True)['usable'])

    def test_cli_partial_mode_succeeds_with_explicit_incomplete_coverage(self):
        self.save([self.record('event_msg', {'type': 'future_chat', 'text': 'opaque'})])
        command = [sys.executable, '-B', str(Path(__file__).with_name('read_codex_source.py')), str(self.source)]
        result = subprocess.run(command + ['--allow-partial'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        parsed = json.loads(result.stdout)
        self.assertTrue(parsed['usable']); self.assertFalse(parsed['complete']); self.assertTrue(parsed['gaps'])
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)

    def test_auto_falls_back_to_response_without_merging_views(self):
        response = self.record('response_item', {'type': 'message', 'role': 'user',
            'content': [{'type': 'input_text', 'text': 'prompt'}]})
        self.save([response])
        self.assertEqual(read_source(self.source, 'auto')['representation'], 'response_item')
        self.save([response, self.record('event_msg', {'type': 'user_message', 'message': 'prompt'})])
        result = read_source(self.source, 'auto')
        self.assertTrue(result['ok'], result)
        self.assertEqual(len(result['messages']), 1)
        self.assertEqual(result['representation'], 'event_msg')

    def test_unknown_nested_shapes_and_content_fail_instead_of_disappearing(self):
        for item in ({'type': 'FutureMessage', 'content': []},
                     {'type': 'UserMessage', 'content': [{'type': 'image'}]},
                     {'type': 'AgentMessage', 'content': [{'type': 'Text', 'text': 'ambiguous'}]},
                     {}):
            with self.subTest(item=item):
                self.save([self.record('event_msg', {'type': 'item_completed', 'item': item})])
                self.assertFalse(read_source(self.source, 'auto')['ok'])
        self.save([self.record('event_msg', {'type': 'user_message', 'message': 'known'}),
                   self.record('event_msg', {'type': 'future_user_message', 'text': 'unread'})])
        self.assertFalse(read_source(self.source, 'auto')['ok'])
        self.save([self.record('response_item', {'type': 'future_message', 'role': 'user',
                   'content': [{'type': 'input_text', 'text': 'unread'}]})])
        self.assertFalse(read_source(self.source, 'response_item')['ok'])
        self.save([self.record('response_item', {'type': 'future_chat', 'body': 'unread'})])
        self.assertFalse(read_source(self.source, 'response_item')['ok'])


if __name__ == "__main__":
    unittest.main()
