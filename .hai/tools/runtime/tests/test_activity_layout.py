"""Public layout-2 lifecycle, declared destinations and disposable-work boundaries."""
import contextlib
import io
import json
import unittest
from unittest import mock

import test_conversation as fixtures
import discovery
from runtime import activities, cli


class ActivityLayoutTests(unittest.TestCase):
    def setUp(self):
        fixtures.ConversationTests.setUp(self)

    def call(self, op, apply=True, **kwargs):
        return activities.handle(op, self.root,
            {'activity_id': self.aid, 'provenance': self.prov, **kwargs}, apply)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob('*') if p.is_file()}

    def test_default_creates_only_readme_and_system_with_exact_original_reference(self):
        base = self.root / self.base
        self.assertEqual({p.name for p in base.iterdir()}, {'README.md', 'system'})
        self.assertEqual({p.name for p in (base / 'system').iterdir()}, {'state.json', 'log.md', 'chat.jsonl', 'usage.json'})
        state = json.loads((base / 'system/state.json').read_text())
        message = json.loads((base / 'system/chat.jsonl').read_text())
        self.assertEqual(state['initial_message_id'], message['message_id'])
        self.assertEqual(message['text'], self.input)
        self.assertNotIn(self.input, (base / 'README.md').read_text())

    def test_close_appends_final_report_preserves_readme_and_archives_system(self):
        base = self.root / self.base
        before = (base / 'README.md').read_bytes()
        result = self.call('close', outcome='completed', archive_label='layout-test',
            outcome_text='Final reviewed result.', recording={'status': 'disabled', 'details': 'Fixture off'})
        self.assertTrue(result['ok'], result)
        archived = self.root / result['result']['archive_path']
        self.assertFalse(base.exists())
        self.assertFalse((archived / 'outcome.md').exists())
        self.assertIn('## Final outcome\n\nFinal reviewed result.', (archived / 'README.md').read_text())
        copies = list((archived / 'history/readme').glob('*.md'))
        self.assertEqual(len(copies), 1)
        self.assertEqual(copies[0].read_bytes(), before)
        self.assertTrue((archived / 'system/usage.json').exists())
        self.assertFalse((archived / 'system/usage.md').exists())
        self.assertIn('[Usage](system/usage.json)', (archived / 'README.md').read_text())
        self.assertIn('[Previous versions](history)', (archived / 'README.md').read_text())
        self.assertEqual(json.loads((archived / 'system/state.json').read_text())['lifecycle'], 'closed')

    def test_declared_output_contract_and_alias_rejection_are_zero_write(self):
        for names in (['definition.md', 'results/definition.md'], ['evidence/check', 'evidence/check/result.md'], ['system/unexpected.json'], ['ad-hoc.md']):
            for apply in (False, True):
                before = self.snapshot()
                result = self.call('record', apply, log='Invalid candidate', artifacts=[
                    {'name': name, 'text': 'Evidence', 'reason': 'Fixture'} for name in names])
                self.assertFalse(result['ok'], result)
                self.assertEqual(before, self.snapshot())
        result = self.call('record', log='Declared review output', artifacts=[
            {'name': 'results/design/proposal.md', 'text': 'Review this proposal.', 'reason': 'Requested design'}])
        self.assertTrue(result['ok'], result)
        self.assertTrue((self.root / self.base / 'results/design/proposal.md').exists())
        self.assertIn('[Reviewable outputs](results)', (self.root / self.base / 'README.md').read_text())

    def test_mixed_unknown_or_malformed_layout_does_not_mutate(self):
        path = self.root / self.base / 'system/state.json'
        original = path.read_bytes()
        state = json.loads(original)
        for value in ([], None, {**state, 'activity_layout_version': True},
                      {**state, 'activity_layout_version': 2.0}, {**state, 'activity_layout_version': 99}):
            path.write_text(json.dumps(value), encoding='utf-8')
            result = self.call('record', log='Must not write')
            self.assertFalse(result['ok'], result)
            self.assertEqual(result['changed_files'], [])
            path.write_bytes(original)
        (path.parent.parent / 'state.json').write_bytes(original)
        self.assertFalse(self.call('record', log='Mixed must block')['ok'])

    def test_request_stdin_avoids_request_files_and_rejects_duplicate_keys(self):
        before = self.snapshot()
        request = json.dumps({'activity_id': self.aid})
        for content, expected in ((request, 0), ('{"activity_id":"one","activity_id":"two"}', 2)):
            output = io.StringIO()
            with mock.patch('sys.stdin', io.StringIO(content)), contextlib.redirect_stdout(output):
                code = cli.main(['activity', 'show', '--workspace', str(self.root), '--request-stdin'])
            self.assertEqual(code, expected, output.getvalue())
        self.assertEqual(before, self.snapshot())

    def test_partial_migration_report_blocks_public_continuation_and_closure(self):
        directory = self.root / self.base / 'evidence/migrations'
        directory.mkdir(parents=True)
        report = directory / 'activity-layout.json'
        for status in ('prepared', 'partial'):
            report.write_text(json.dumps({'activity_layout_migration_format': 1, 'status': status}), encoding='utf-8')
            before = self.snapshot()
            for op, kwargs in [('record', {'log': 'Must block'}),
                               ('close', {'outcome': 'completed', 'archive_label': 'blocked',
                                          'outcome_text': 'Not allowed', 'recording': {'status': 'disabled', 'details': 'Fixture'}})]:
                result = self.call(op, **kwargs)
                self.assertFalse(result['ok'], result)
                self.assertIn('Incomplete Activity migration', str(result))
                self.assertEqual(result['changed_files'], [])
            self.assertEqual(before, self.snapshot())

    def test_stdin_uses_utf8_bytes_even_with_non_utf8_host_text_stream(self):
        content = '\u041f\u0440\u0438\u0432\u0435\u0442 \u03bb'
        request = json.dumps({'activity_id': self.aid, 'author': 'human-user', 'role': 'human',
                              'text': content, 'provenance': self.prov}, ensure_ascii=False).encode('utf-8')
        output = io.StringIO()
        with io.TextIOWrapper(io.BytesIO(request), encoding='ascii') as incoming:
            with mock.patch('sys.stdin', incoming), contextlib.redirect_stdout(output):
                code = cli.main(['activity', 'chat-post', '--workspace', str(self.root), '--request-stdin'])
        self.assertEqual(code, 0, output.getvalue())
        self.assertEqual(json.loads(output.getvalue())['result']['message']['text'], content)

    def test_json_deliverable_retains_exact_declared_content_without_markdown_footer(self):
        text = '[1, {"actual": true}]\n'
        result = self.call('record', log='Retain declared JSON output', artifacts=[
            {'name': 'evidence/tests/check.json', 'text': text, 'reason': 'Structured verification evidence'}])
        self.assertTrue(result['ok'], result)
        path = self.root / self.base / 'evidence/tests/check.json'
        self.assertEqual(path.read_bytes(), text.encode('utf-8'))
        self.assertEqual(json.loads(path.read_text()), [1, {'actual': True}])
        self.assertIn('Structured verification evidence', (self.root / self.base / 'system/log.md').read_text())

    def test_selected_closed_migration_requires_active_work_and_explicit_option(self):
        def close(aid, label):
            result = self.call('close', activity_id=aid, outcome='completed', archive_label=label,
                               outcome_text='Exact original closure result.',
                               recording={'status': 'disabled', 'details': 'Fixture'})
            self.assertTrue(result['ok'], result)
            return result

        close(self.aid, 'first')
        old = activities.handle('create', self.root,
            {'initial_input': 'Old request', 'layout_version': 1, 'provenance': self.prov}, True)
        self.assertTrue(old['ok'], old)
        aid = old['result']['state']['activity_id']
        closed = close(aid, 'legacy-target')
        original_state = closed['result']['state']
        original_outcome = (self.root / closed['result']['archive_path'] / 'outcome.md').read_bytes()
        before = self.snapshot()
        self.assertFalse(self.call('migrate-layout', activity_id=aid, allow_closed=True)['ok'])
        self.assertEqual(before, self.snapshot())
        work = activities.handle('create', self.root, {'initial_input': 'Migration work', 'provenance': self.prov}, True)
        self.assertTrue(work['ok'], work)
        work_state = self.root / work['result']['path'] / 'system/state.json'
        work_before = work_state.read_bytes()
        before = self.snapshot()
        self.assertFalse(self.call('migrate-layout', activity_id=aid)['ok'])
        self.assertEqual(before, self.snapshot())
        self.assertTrue(self.call('migrate-layout', False, activity_id=aid, allow_closed=True)['ok'])
        self.assertEqual(before, self.snapshot())
        result = self.call('migrate-layout', activity_id=aid, allow_closed=True)
        self.assertTrue(result['ok'], result)
        target = self.root / closed['result']['archive_path']
        for key, value in original_state.items():
            self.assertEqual(result['result']['state'][key], value)
        self.assertIn(original_outcome, (target / 'README.md').read_bytes())
        self.assertEqual(work_before, work_state.read_bytes())

    def test_migration_report_appearing_during_discovery_is_structured_failure(self):
        original = discovery._validate_state

        def report_appears(state):
            result = original(state)
            directory = self.root / self.base / 'evidence/migrations'
            directory.mkdir(parents=True, exist_ok=True)
            (directory / 'activity-layout.json').write_text(json.dumps({
                'activity_layout_migration_format': 1, 'activity_id': self.aid, 'status': 'completed'}))
            return result

        with mock.patch.object(discovery, '_validate_state', side_effect=report_appears):
            result = activities.handle('discover', self.root, {}, False)
        self.assertFalse(result['ok'], result)
        self.assertIn('metadata changed during discovery', str(result))
        self.assertEqual(result['changed_files'], [])

    def test_cleanup_requires_evidence_and_ended_writers_and_keeps_allocations(self):
        work = self.root / self.base / 'work/coordinator'
        work.mkdir(parents=True)
        (work / 'temporary-request.json').write_text('{}')
        request = {'paths': ['work/coordinator'], 'writers_ended': True, 'evidence_retained': True}
        before = self.snapshot()
        result = self.call('work-cleanup', False, **request)
        self.assertTrue(result['ok'], result); self.assertEqual(before, self.snapshot())
        self.assertFalse(self.call('work-cleanup', **{**request, 'writers_ended': False})['ok'])
        self.assertFalse(self.call('work-cleanup', **{**request, 'paths': ['system']})['ok'])
        result = self.call('work-cleanup', **request)
        self.assertTrue(result['ok'], result); self.assertFalse(work.exists())
        allocated = self.call('invocation-allocate', role='reviewer')
        self.assertTrue(allocated['ok'], allocated)
        relative = allocated['result']['activity_relative_path']
        before = self.snapshot()
        self.assertFalse(self.call('work-cleanup', paths=[relative], writers_ended=True, evidence_retained=True)['ok'])
        self.assertEqual(before, self.snapshot())


if __name__ == '__main__':
    unittest.main()
