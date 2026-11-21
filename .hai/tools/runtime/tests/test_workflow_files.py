import os
import unittest
from unittest import mock

import test_workflow_runs as fixtures
from runtime import activities, startup, workflow_files, workflows
from runtime.storage import SafetyError
from workflows.definition import DefinitionError, parse_definition


DEFINITION = """---
workflow_format: 4
name: sample
revision: 1
entry: prepare
max_step_attempts: 2
max_run_attempts: 4
---
# Files

## Purpose
Prepare a report and deliver it after review.

## Inputs
| Name | Required | Mode | Location | Format | Expectation |
| --- | --- | --- | --- | --- | --- |
| proposal | yes | ask | - | markdown | A bounded proposal. |
| optional | no | fixed | optional.md | markdown | Extra context. |

## Intermediate Files
| Name | Mode | Location | Format | Expectation |
| --- | --- | --- | --- | --- |
| notes | default | run:files/notes.md | markdown | Assessment notes. |

## Final Files
| Name | Action | Mode | Location | Format | Expectation |
| --- | --- | --- | --- | --- | --- |
| report | create | default | run:files/report.md | markdown | Reviewed report. |

## Outcomes
| Name | Meaning | Files |
| --- | --- | --- |
| delivered | The report was reviewed. | report |
| declined | No report was approved. | - |

## Steps
### prepare
#### Role
worker

#### Instruction
Prepare notes and a report from the proposal.

#### Inputs
| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| proposal | workflow:proposal | yes | markdown | Original proposal. |

#### Outputs
| Name |
| --- |
| notes |
| report |

#### Results
| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| prepared | Notes and report are ready for review. | notes, report | step:review | none |
| declined | The proposal cannot be assessed. | - | end:declined | none |

### review
#### Role
worker

#### Instruction
Review the notes and report.

#### Inputs
| Name | Source | Required | Format | Expectation |
| --- | --- | --- | --- | --- |
| notes | incoming:notes | yes | markdown | Notes from preparation. |
| report | accepted:prepare/prepared/report | yes | markdown | Prepared report. |

#### Outputs
| Name |
| --- |

#### Results
| Name | When | Outputs | Next | Gate |
| --- | --- | --- | --- | --- |
| verified | The report meets the criteria. | - | end:delivered | none |
| revise | The report needs another attempt. | - | step:prepare | none |
"""


class WorkflowFileTests(unittest.TestCase):
    setUp_fixture = fixtures.WorkflowRunTests.setUp
    call = fixtures.WorkflowRunTests.call
    show = fixtures.WorkflowRunTests.show
    mutation = fixtures.WorkflowRunTests.mutation
    prepare = fixtures.WorkflowRunTests.prepare
    running = fixtures.WorkflowRunTests.running
    finish = fixtures.WorkflowRunTests.finish

    def setUp(self):
        self.setUp_fixture(layout_version=2)
        self.defpath.write_text(DEFINITION, encoding='utf-8')
        input_dir = self.activity / 'work'
        input_dir.mkdir()
        (input_dir / 'proposal.md').write_text('Activity proposal', encoding='utf-8')
        (self.root / 'proposal.md').write_text('Workspace proposal', encoding='utf-8')

    def start(self, paths=None, apply=True):
        result = self.call('start', apply=apply, definition='.hai_env/workflows/sample.md', paths=paths or {})
        if result['ok'] and apply:
            self.run_id = result['result']['state']['run_id']
            self.base = self.root / result['result']['path']
        return result

    def files(self):
        result = workflows.handle('show', self.root, {'activity_id': self.aid, 'run_id': self.run_id}, False)
        self.assertTrue(result['ok'], result)
        return result['result']['files']

    def draft(self, text='first'):
        assignment = self.prepare()['result']['assignment']
        self.running()
        for name, row in assignment['outputs'].items():
            (self.base / row['path']).write_text(f'{name}: {text}', encoding='utf-8')
        return assignment

    def test_launch_bindings_status_handoffs_and_archive(self):
        missing = self.start()
        self.assertEqual(missing['status'], 'needs_input')
        self.assertEqual([row['file'] for row in missing['result']['questions']], ['proposal'])
        self.assertEqual(missing['result']['user_notice']['action_owner'], 'user')
        self.assertEqual(missing['result']['questions'][0]['prompt'], 'Where is the proposal file saved?')
        self.assertEqual(missing['changed_files'], [])
        self.assertFalse(self.start({'proposal': 'proposal.md', 'optional': 'proposal.md'})['ok'])
        self.assertFalse(self.start({'proposal': 'proposal.md', 'report': 'activity:system/state.json'})['ok'])
        self.assertFalse(self.start({'proposal': 'proposal.md', 'report': 'activity:report.md'})['ok'])
        override = {'proposal': 'activity:work/proposal.md', 'report': 'activity:results/reviewed.md'}
        self.assertTrue(self.start(override, apply=False)['ok'])
        self.assertTrue(self.start(override)['ok'])
        self.assertTrue((self.base / 'bindings.json').is_file())
        self.assertEqual(self.files()['optional']['status'], 'absent')
        snapshot = self.files()['proposal']['snapshot']
        self.assertEqual((self.base / snapshot['path']).read_text(), 'Activity proposal')
        summary = startup.handle('', self.root, {}, False)['result']['activity_context']['workflows']
        self.assertEqual([(row['run_id'], row['current_step']) for row in summary['runs']], [(self.run_id, 'prepare')])

        first = self.draft()
        self.assertEqual(self.files()['report']['status'], 'awaiting-acceptance')
        self.assertTrue(self.finish('prepared')['ok'])
        self.assertEqual((self.base / 'files/notes.md').read_text(), 'notes: first')
        final = self.activity / 'results/reviewed.md'
        self.assertFalse(final.exists())
        self.assertEqual(self.files()['report']['status'], 'ready')
        self.draft()
        self.assertTrue(self.finish('revise')['ok'])
        self.draft('second')
        self.assertTrue(self.finish('prepared')['ok'])
        notes = self.files()['notes']
        self.assertEqual([row['status'] for row in notes['versions']], ['superseded', 'ready'])
        self.assertEqual((self.base / first['outputs']['notes']['path']).read_text(), 'notes: first')
        self.assertEqual((self.base / 'files/notes.md').read_text(), 'notes: second')

        review = self.draft()
        self.assertEqual(review['outputs'], {})
        self.assertIn('attempt-0002', review['inputs']['report']['path'])
        self.assertTrue(self.finish('verified')['ok'])
        self.assertEqual(final.read_text(), 'report: second')
        self.assertEqual(self.files()['report']['status'], 'delivered')
        prior_output = 'activity:workflow-runs/' + self.run_id + '/files/notes.md'
        preview = workflows.handle('start', self.root, {'activity_id': self.aid, 'provenance': self.prov,
            'definition': '.hai_env/workflows/sample.md', 'paths': {'proposal': prior_output}}, False)
        self.assertTrue(preview['ok'], preview)
        shown = activities.handle('show', self.root, {'activity_id': self.aid}, False)
        self.assertEqual(shown['result']['workflows']['runs'], [])
        archived = activities.handle('close', self.root, {'activity_id': self.aid, 'outcome': 'completed',
            'archive_label': 'fixture', 'outcome_text': 'Done', 'recording': {'status': 'disabled', 'details': 'Fixture'},
            'provenance': self.prov}, True)
        self.assertTrue(archived['ok'], archived)
        report = self.files()['report']
        self.assertEqual(report['status'], 'delivered')
        self.assertEqual(report['resolved_path'], archived['result']['archive_path'] + '/results/reviewed.md')

    def test_update_conflict_and_recovery_from_interrupted_publication(self):
        self.defpath.write_text(DEFINITION.replace(
            'report | create | default | run:files/report.md', 'report | update | fixed | proposal.md'), encoding='utf-8')
        self.assertTrue(self.start({'proposal': 'proposal.md'})['ok'])
        self.draft()
        self.assertTrue(self.finish('prepared')['ok'])
        self.draft()
        proposal = self.root / 'proposal.md'
        original = proposal.read_bytes()
        original_stat = proposal.stat()
        proposal.write_bytes(b'changed after launch')
        blocked = self.finish('verified')
        self.assertEqual(blocked['status'], 'blocked')
        self.assertEqual(proposal.read_bytes(), b'changed after launch')
        proposal.write_bytes(original)
        os.utime(proposal, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
        real_publish = workflow_files.publish

        def interrupt(*args, **kwargs):
            real_publish(*args, **kwargs)
            raise SafetyError('simulated interruption before publication event')

        with mock.patch.object(workflow_files, 'publish', side_effect=interrupt):
            interrupted = self.finish('verified')
        self.assertEqual(interrupted['status'], 'partial')
        self.assertIn('simulated interruption before publication event', interrupted['issues'], interrupted)
        self.assertEqual(self.show()['status'], 'publishing')
        self.assertEqual(proposal.read_text(), 'report: first')
        pending = startup.handle('', self.root, {}, False)['result']['activity_context']['workflows']['runs']
        self.assertEqual(pending[0]['status'], 'publishing')
        resumed = self.mutation('publish')
        self.assertTrue(resumed['ok'], resumed)
        self.assertEqual(self.files()['report']['status'], 'delivered')
        self.assertEqual(proposal.read_text(), 'report: first')

    def test_ambiguous_paths_and_empty_file_lists(self):
        with self.assertRaisesRegex(DefinitionError, 'unavailable files'):
            parse_definition(DEFINITION.replace('end:declined | none |',
                'end:declined | none |\n| incomplete | The report is incomplete. | - | end:delivered | none |'))
        without_files = '\n'.join(line for line in DEFINITION.split('### review')[0].splitlines()
                                  if not line.startswith(('| proposal |', '| optional |', '| notes |',
                                                          '| report |', '| delivered |', '| prepared |')))
        self.defpath.write_text(without_files, encoding='utf-8')
        self.assertTrue(self.start()['ok'])
        self.draft()
        self.assertTrue(self.finish('declined')['ok'])
        self.assertEqual(self.files(), {})

    def test_install_and_discover_more_than_one_unfinished_run(self):
        source = self.root / 'sample.md'
        self.defpath.replace(source)
        install = workflows.handle('install', self.root, {'definition': 'sample.md', 'provenance': self.prov}, True)
        self.assertTrue(install['ok'], install)
        self.assertFalse((self.root / '.hai_env/config/workflows/sample.json').exists())
        self.assertTrue(self.start({'proposal': 'proposal.md'})['ok'])
        first = self.run_id
        self.assertTrue(self.mutation('pause')['ok'])
        self.run_id = None
        self.assertTrue(self.start({'proposal': 'proposal.md'})['ok'])
        prepared = self.prepare()['result']['assignment']
        waiting = self.mutation('record-execution', step_id=prepared['step_id'], attempt_id=prepared['attempt_id'],
                                status='waiting', executor=self.executor, details='Confirm the affected area.')
        self.assertTrue(waiting['ok'], waiting)
        summary = activities.handle('discover', self.root, {}, False)['result']['workflows']
        rows = {row['run_id']: row for row in summary['runs']}
        self.assertEqual(rows[first]['status'], 'paused')
        self.assertEqual(rows[self.run_id]['status'], 'waiting')
        self.assertEqual(rows[self.run_id]['pending_action'], 'Confirm the affected area.')


if __name__ == '__main__':
    unittest.main()
