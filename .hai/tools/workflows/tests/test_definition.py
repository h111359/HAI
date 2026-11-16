"""Behavioral fixtures for single-file workflow structure and handoff contracts."""
from pathlib import Path
import hashlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from workflows.definition import DefinitionError, load_definition, parse_definition


def step(name='inspect', *, inputs=None, outputs=None, results=None, agent='not-installed-role'):
    inputs = inputs if inputs is not None else [('request', 'workflow:request', 'yes', 'markdown', 'Actual supplied request.')]
    outputs = outputs if outputs is not None else [('report', 'attempt:report.md', 'markdown', 'Actual findings.')]
    results = results if results is not None else [('assessed', 'The assessment covers the request.', 'report', 'end:assessed')]
    def table(headers, rows):
        return '| ' + ' | '.join(headers) + ' |\n| ' + ' | '.join(['---'] * len(headers)) + ' |\n' + ''.join('| ' + ' | '.join(row) + ' |\n' for row in rows)
    return (f'### {name}\n\n#### Role\n\n{agent}\n\n#### Instruction\n\nInspect the input and record actual findings.\n\n#### Inputs\n\n'
            + table(['Name', 'Source', 'Required', 'Format', 'Expectation'], inputs)
            + '\n#### Outputs\n\n' + table(['Name', 'Location', 'Format', 'Expectation'], outputs)
            + '\n#### Results\n\n' + table(['Name', 'When', 'Outputs', 'Next'], results))


def workflow(*steps, outcomes=('assessed',)):
    return ('---\nworkflow_format: 2\nname: sample\nrevision: 1\nentry: inspect\nmax_step_attempts: 3\nmax_run_attempts: 12\n---\n'
            '# Example assessment\n\n## Purpose\n\nAssess a supplied request.\n\n## Inputs\n\n'
            '| Name | Location | Format | Expectation |\n| --- | --- | --- | --- |\n'
            '| request | activity:input.md | markdown | Actual supplied request. |\n\n## Outcomes\n\n'
            '| Name | Meaning |\n| --- | --- |\n'
            + ''.join(f'| {name} | A recorded final outcome. |\n' for name in outcomes)
            + '\n## Steps\n\n' + '\n'.join(steps or [step()]))


class DefinitionTests(unittest.TestCase):
    def invalid(self, text, message):
        with self.assertRaisesRegex(DefinitionError, message):
            parse_definition(text, 'fixture.md')

    def test_contract_is_structural_not_role_readiness(self):
        parsed = parse_definition(workflow())
        self.assertEqual(parsed['steps']['inspect']['role'], 'not-installed-role')
        self.assertTrue(parsed['steps']['inspect']['inputs']['request']['required'])
        self.assertEqual(parsed['steps']['inspect']['results']['assessed']['outputs'], ['report'])
        self.assertEqual(parsed['inputs']['request']['location'], 'activity:input.md')

    def test_exact_bytes_unicode_and_line_endings(self):
        for newline in ('\n', '\r\n'):
            text = workflow().replace('Actual findings.', 'Findings about café and 東京.').replace('\n', newline)
            raw = text.encode('utf-8'); result = parse_definition(raw)
            self.assertEqual(result['sha256'], hashlib.sha256(raw).hexdigest())
            self.assertIn('東京', result['steps']['inspect']['outputs']['report']['expectation'])

    def test_arbitrary_result_names_and_artifact_formats(self):
        text = workflow(step(outputs=[('report', 'attempt:report.xlsx', 'spreadsheet chosen by author', 'Author-required cells.')],
                             results=[('feasible-with-conditions', 'Condition one.', 'report', 'end:assessed'),
                                      ('needs-discovery', 'Condition two.', 'report', 'end:assessed'),
                                      ('outside-scope', 'Condition three.', 'report', 'end:assessed')]))
        self.assertEqual(len(parse_definition(text)['steps']['inspect']['results']), 3)
        for path, fmt in [('attempt:image.PNG', 'PNG'), ('attempt:data', 'directory'), ('attempt:empty.bin', 'empty binary'), ('attempt:records.json', 'JSON array')]:
            with self.subTest(path=path):
                result = parse_definition(workflow(step(outputs=[('report', path, fmt, 'Author decides valid content.')])) )
                self.assertEqual(result['steps']['inspect']['outputs']['report']['format'], fmt)

    def test_missing_duplicate_unknown_and_unsupported_frontmatter(self):
        for old, new, error in [('entry: inspect\n', '', 'missing keys'),
                                ('entry: inspect', 'entry: inspect\nentry: inspect', 'duplicate key'),
                                ('entry: inspect', 'entry: inspect\nother: value', 'unknown'),
                                ('workflow_format: 2', 'workflow_format: 99', 'unsupported version'),
                                ('revision: 1', 'revision: 0', 'positive'),
                                ('name: sample', 'name: "sample"', 'bare scalar'),
                                ('name: sample', 'name: Sample', 'bare scalar'),
                                ('name: sample', 'name: sample # comment', 'bare scalar')]:
            with self.subTest(new=new): self.invalid(workflow().replace(old, new), error)

    def test_bom_invalid_utf8_and_nul_rejected(self):
        for raw in [b'\xef\xbb\xbf' + workflow().encode(), b'\xff', workflow().encode() + b'\x00']:
            with self.assertRaises(DefinitionError): parse_definition(raw)

    def test_identifier_limits(self):
        self.invalid(workflow().replace('name: sample', 'name: ' + 'a' * 65), '64')
        self.invalid(workflow(step(agent='bad--role')), 'kebab-case')

    def test_title_sections_and_duplicate_steps_are_explicit(self):
        self.invalid(workflow().replace('# Example assessment', 'Example assessment'), 'H1')
        self.invalid(workflow().replace('## Purpose', '## Other'), 'sections in order')
        self.invalid(workflow(step(), step()), 'duplicate section')
        self.invalid(workflow().replace('#### Results', '#### Other'), 'sections in order')

    def test_empty_prose_and_missing_table_rejected(self):
        self.invalid(workflow().replace('Assess a supplied request.', ''), 'Purpose')
        self.invalid(workflow().replace('Inspect the input and record actual findings.', ''), 'Instruction')
        self.invalid(workflow().replace('| request | workflow:request | yes | markdown | Actual supplied request. |', 'prose instead'), 'literal pipe table')

    def test_table_cell_errors_include_section_and_row(self):
        self.invalid(workflow().replace('Actual findings.', ''), r'Outputs: row 1, line')
        self.invalid(workflow().replace('Actual findings.', 'findings | extra'), 'expected 4 cells')
        self.invalid(workflow().replace('Actual findings.', r'findings \| extra'), 'literal pipe table')
        self.invalid(workflow().replace('| Name | Source | Required | Format | Expectation |', '| Name | Source | Optional | Format | Expectation |'), 'headers')

    def test_fake_headings_in_code_fences_and_unclosed_fences_fail(self):
        self.invalid(workflow().replace('Inspect the input and record actual findings.', '```markdown\n#### Outputs\n```'), 'imitates')
        self.invalid(workflow() + '\n```text\nunfinished', 'unclosed')
        result = parse_definition(workflow().replace('Inspect the input and record actual findings.', 'Inspect using:\n```text\nplain command\n```'))
        self.assertIn('plain command', result['steps']['inspect']['instruction'])
        self.invalid(workflow().replace('## Purpose', '  ## Purpose'), 'column one')

    def test_required_values_and_literal_sources(self):
        self.invalid(workflow().replace('| yes | markdown |', '| optional | markdown |'), 'yes or no')
        self.invalid(workflow().replace('workflow:request', '`workflow:request`'), 'prefix')
        self.invalid(workflow().replace('workflow:request', 'last-known:request'), 'prefix')
        self.invalid(workflow().replace('workflow:request', 'workflow:missing'), 'unknown workflow input')

    def test_entry_requires_no_incoming_artifact(self):
        self.invalid(workflow(step(inputs=[('request', 'incoming:report', 'yes', 'markdown', 'Previous report.')])), 'entry cannot require')
        result = parse_definition(workflow(step(inputs=[('request', 'incoming:report', 'no', 'markdown', 'Previous report if available.')])))
        self.assertFalse(result['steps']['inspect']['inputs']['request']['required'])

    def test_missing_entry_target_result_output_and_outcome(self):
        self.invalid(workflow().replace('entry: inspect', 'entry: missing'), 'unknown step')
        self.invalid(workflow().replace('end:assessed', 'step:missing'), 'unknown target')
        self.invalid(workflow().replace('end:assessed', 'end:missing'), 'unknown outcome')
        self.invalid(workflow().replace('| report | end:assessed |', '| missing | end:assessed |'), 'unknown output')

    def test_all_branches_must_provide_required_input(self):
        start = step(outputs=[('report', 'attempt:report.md', 'markdown', 'Report.'), ('questions', 'attempt:questions.md', 'markdown', 'Questions.')],
                     results=[('ready', 'Ready.', 'report', 'step:next'), ('questions', 'Questions remain.', 'questions', 'step:next')])
        target = step('next', inputs=[('report', 'incoming:report', 'yes', 'markdown', 'Actual report.')])
        self.invalid(workflow(start, target), 'required incoming output.*missing')
        target = step('next', inputs=[('report', 'incoming:report', 'no', 'markdown', 'Actual report when available.')])
        self.assertEqual(len(parse_definition(workflow(start, target))['steps']), 2)

    def test_incoming_and_initial_formats_must_agree(self):
        start = step(results=[('ready', 'Ready.', 'report', 'step:next')])
        target = step('next', inputs=[('report', 'incoming:report', 'yes', 'PNG', 'Image report.')])
        self.invalid(workflow(start, target), 'Format descriptions differ')
        self.invalid(workflow().replace('| request | workflow:request | yes | markdown |', '| request | workflow:request | yes | JSON |'), 'Format differs')

    def test_unreachable_unused_and_terminal_path_checks(self):
        self.invalid(workflow(step(), step('unused')), 'unreachable steps')
        self.invalid(workflow(outcomes=('assessed', 'unused')), 'unreachable outcomes')
        self.invalid(workflow(step(outputs=[('report', 'attempt:report.md', 'markdown', 'Report.'), ('unused', 'attempt:unused.md', 'markdown', 'Unused.')])), 'unused declared outputs')
        start = step(results=[('finish', 'Done.', 'report', 'end:assessed'), ('loop', 'Try looping.', 'report', 'step:loop')])
        loop = step('loop', inputs=[], results=[('again', 'Repeat.', 'report', 'step:loop')])
        self.invalid(workflow(start, loop), 'no possible terminal path')

    def test_bounded_cycles_with_terminal_path_are_valid(self):
        start = step(results=[('again', 'Repeat.', 'report', 'step:inspect'), ('done', 'Done.', 'report', 'end:assessed')])
        self.assertEqual(parse_definition(workflow(start))['max_step_attempts'], 3)

    def test_duplicate_outputs_results_and_output_lists_fail(self):
        self.invalid(workflow(step(outputs=[('report', 'attempt:a.md', 'markdown', 'A.'), ('report', 'attempt:b.md', 'markdown', 'B.')])), 'duplicate name')
        self.invalid(workflow(step(results=[('assessed', 'A.', 'report', 'end:assessed'), ('assessed', 'B.', 'report', 'end:assessed')])), 'duplicate name')
        self.invalid(workflow().replace('| report | end:assessed |', '| report, report | end:assessed |'), 'distinct output names')

    def test_unsafe_reserved_alias_and_overlapping_paths_fail(self):
        for location in ['attempt:../escape', 'attempt:C:/file', 'attempt:/absolute', 'attempt:a\\b',
                         'attempt:CON.txt', 'attempt:file:stream', 'attempt:result.json',
                         'attempt:assignment.json/nested', 'attempt:rejection-0001.json', 'attempt:`report.md`']:
            with self.subTest(location=location):
                self.invalid(workflow(step(outputs=[('report', location, 'any', 'Actual artifact.')])), 'path|output|components|metadata|literal')
        for location in ['attempt:REPORT.md', 'attempt:report.md/nested', 'attempt:report']:
            first = 'attempt:report.md' if location != 'attempt:report' else 'attempt:report/nested'
            text = workflow(step(outputs=[('report', first, 'any', 'A.'), ('other', location, 'any', 'B.')], results=[('assessed', 'Done.', 'report, other', 'end:assessed')]))
            self.invalid(text, 'overlapping output path')

    def test_protected_initial_input_paths_fail(self):
        for path in ['workspace:.git/config', 'workspace:.hai_env/config/state.json', 'workspace:.codex/config.json']:
            self.invalid(workflow().replace('activity:input.md', path), 'protected')

    def test_load_checks_identity_regular_type_and_exact_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory).resolve() / 'sample.md'; raw = workflow().encode(); path.write_bytes(raw)
            self.assertEqual(load_definition(path)['sha256'], hashlib.sha256(raw).hexdigest())
            wrong = path.with_name('other.md'); wrong.write_bytes(raw)
            with self.assertRaisesRegex(DefinitionError, 'filename'): load_definition(wrong)
            with self.assertRaises(DefinitionError): load_definition(Path(directory))
            with self.assertRaises(DefinitionError): load_definition(path.with_name('missing.md'))

    def test_load_rejects_symlink_when_platform_allows_it(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory).resolve() / 'sample.md'; path.write_text(workflow(), encoding='utf-8')
            linked = path.with_name('linked.md')
            try: linked.symlink_to(path)
            except (OSError, NotImplementedError): self.skipTest('symlink creation unavailable')
            with self.assertRaises(DefinitionError): load_definition(linked)

    def test_load_rejects_hardlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory).resolve() / 'sample.md'; path.write_text(workflow(), encoding='utf-8')
            linked = path.with_name('hardlink.md')
            try: os.link(path, linked)
            except (OSError, NotImplementedError): self.skipTest('hardlink creation unavailable')
            with self.assertRaises(DefinitionError): load_definition(path)

    def test_legacy_role_label_is_only_readable_for_historical_runs(self):
        raw = workflow().replace('workflow_format: 2', 'workflow_format: 1').replace('#### Role', '#### Agent').encode()
        with self.assertRaisesRegex(DefinitionError, 'explicit role migration'):
            parse_definition(raw)
        parsed = parse_definition(raw, allow_legacy=True)
        self.assertEqual(parsed['workflow_format'], 1)
        self.assertEqual(parsed['steps']['inspect']['role'], 'not-installed-role')
        self.assertEqual(parsed['sha256'], hashlib.sha256(raw).hexdigest())


if __name__ == '__main__':
    unittest.main()
