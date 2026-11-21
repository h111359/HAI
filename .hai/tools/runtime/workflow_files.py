"""Resolve format-4 file bindings and apply verified workflow publications."""
from pathlib import PurePosixPath

from activity_layout import version as activity_layout
from workflows.definition import file_location

from .storage import SafetyError, checked_path, fingerprint, read_json, write_bytes
from .workflow_artifacts import digest, mkdirs
from .workflow_config import canonical_spelling


def resolve(owner_path, base, location):
    scope, tail = location.split(':', 1)
    if scope == 'activity':
        return owner_path + '/' + tail
    if scope == 'run':
        return base + '/' + tail
    return tail


def _overlaps(left, right):
    left, right = left.casefold(), right.casefold()
    return left == right or left.startswith(right + '/') or right.startswith(left + '/')


def destination(root, owner_path, base, location, store):
    relative = resolve(owner_path, base, location)
    scope, tail = location.split(':', 1)
    if scope == 'run':
        if not tail.startswith('files/'):
            raise SafetyError('Run file destinations must be under run:files/')
    elif scope == 'activity':
        if activity_layout(root, owner_path) == 2:
            bucket, separator, _ = tail.partition('/')
            if not separator or bucket not in ('results', 'evidence', 'work'):
                raise SafetyError('Layout-2 Activity outputs must be under results/, evidence/, or work/')
        protected = ('system', 'history', 'chronicles', 'workflow-runs', 'work/agents',
                     'evidence/migrations', 'files/agent-invocations', 'files/revisions', 'README.md', 'state.json',
                     'log.md', 'chat.jsonl', 'input.md', 'outcome.md', 'usage.md', 'usage.json')
        if any(_overlaps(tail, reserved) for reserved in protected):
            raise SafetyError('Activity file destination overlaps managed storage: ' + relative)
    elif any(_overlaps(relative, reserved) for reserved in
             ('.hai', '.hai_env/config', '.hai_env/roles', '.hai_env/agents', '.hai_env/skills',
              '.hai_env/workflows', '.hai_env/workflow-runs', '.hai_env/.runtime.lock',
              '.git', '.aws', '.agents', '.codex', store)):
        raise SafetyError('Workspace file destination overlaps managed storage: ' + relative)
    if any(part.casefold() in {'.env', '.envrc', 'credentials', 'secrets.toml'}
           for part in relative.split('/')):
        raise SafetyError('Workflow destination names a protected secrets file: ' + relative)
    path = checked_path(root, relative)
    canonical_spelling(root, relative)
    return relative, path


def bind(root, owner_path, base, definition, overrides, store):
    contracts = {**definition['inputs'], **definition['intermediate_files'], **definition['final_files']}
    if not isinstance(overrides, dict) or set(overrides) - set(contracts):
        raise ValueError('paths must map only declared file names to paths')
    bindings, seen = {}, []
    questions = [{'file': name, 'format': contract['format'], 'expectation': contract['expectation']}
                 for name, contract in contracts.items() if contract['mode'] == 'ask' and name not in overrides]
    if questions:
        return {}, questions
    for name, contract in contracts.items():
        supplied = name in overrides
        mode = contract['mode']
        if supplied and mode == 'fixed':
            raise ValueError('Cannot override fixed file location: ' + name)
        raw = overrides[name] if supplied else contract['location']
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError('Expected a nonempty path for ' + name)
        input_file = name in definition['inputs']
        location = file_location(raw, output=not input_file, where=name)
        binding = {'location': location, 'selected_by': 'user' if supplied else mode}
        bindings[name] = binding
        if input_file:
            path = resolve(owner_path, base, location)
            target = checked_path(root, path)
            canonical_spelling(root, path)
            if not target.exists() and not contract['required'] and not supplied:
                binding['available'] = False
            elif not target.is_file():
                raise SafetyError('Expected an existing workflow input file: ' + path)
        else:
            path, target = destination(root, owner_path, base, location, store)
            baseline = fingerprint(target)
            action = contract.get('action', 'create')
            if (baseline is None) != (action == 'create'):
                raise SafetyError(f'{name}: {action} destination has unexpected existence: {path}')
            binding['baseline'] = list(baseline) if baseline is not None else None
        action = contract.get('action')
        for prior, prior_input in seen:
            updating_input = prior_input and action == 'update' and path == prior
            if not updating_input and (not input_file or not prior_input) and _overlaps(path, prior):
                raise SafetyError(f'Overlapping workflow file locations: {prior}, {path}')
        seen.append((path, input_file))
    return bindings, questions


def assignment_outputs(step, state, relative, owner_path, base):
    result = {}
    for name, output in step['outputs'].items():
        binding = state['bindings'][name]
        suffix = PurePosixPath(binding['location'].split(':', 1)[1]).suffix
        result[name] = {**output, 'location': 'attempt:files/' + name + suffix,
                        'path': relative + '/files/' + name + suffix,
                        'destination': binding['location'],
                        'resolved_destination': resolve(owner_path, base, binding['location'])}
    return result


def publication_plan(root, owner_path, base, store, state, definition, outputs, kind, target):
    from .workflow_lineage import latest, verify_record

    selected = {name: output for name, output in outputs.items() if name in definition['intermediate_files']}
    delivered = definition['outcomes'][target]['files'] if kind == 'end' else []
    step_id, attempt_id = state['current_step'], state['current_attempt']
    next_accepted = {**state['accepted'], step_id + '/' + attempt_id: {
        'step_id': step_id, 'attempt_id': attempt_id,
        'execution_number': state['step_attempt_counts'][step_id],
    }}
    after = {**state, 'accepted': next_accepted}
    for name in delivered:
        if name in outputs:
            selected[name] = outputs[name]
            continue
        for sid, step in definition['steps'].items():
            if name in step['outputs']:
                if sid == state['current_step']:
                    raise SafetyError('Outcome requires a file from the current result: ' + name)
                key, record = latest(state, sid)
                if record is None or name not in record['outputs']:
                    raise SafetyError('Outcome requires a current accepted file: ' + name)
                verify_record(root, base, after, key)
                selected[name] = record['outputs'][name]
                break
    plan = {}
    for name, output in selected.items():
        binding = state['bindings'][name]
        previous = state.get('materialized_files', {}).get(name)
        expected = previous['fingerprint'] if previous else binding['baseline']
        relative, path = destination(root, owner_path, base, binding['location'], store)
        current = fingerprint(path)
        if current != (tuple(expected) if expected else None):
            raise SafetyError('Workflow destination changed since binding or the previous write: ' + relative)
        plan[name] = {'path': output['path'], 'artifact': output['artifact'],
                      'location': binding['location'], 'expected': expected, 'final': name in delivered}
    return plan


def publish(root, owner_path, base, store, plan, changed):
    ready = {}
    for name, row in plan.items():
        relative, path = destination(root, owner_path, base, row['location'], store)
        source = base + '/' + row['path']
        raw = checked_path(root, source, allow_missing=False).read_bytes()
        if digest(raw) != row['artifact']['sha256']:
            raise SafetyError('Accepted publication source changed: ' + name)
        current = fingerprint(path)
        if current is None or current[-1] != row['artifact']['sha256']:
            expected = tuple(row['expected']) if row['expected'] else None
            if current != expected:
                raise SafetyError('Workflow destination changed before publication: ' + relative)
            if '/' in relative:
                mkdirs(root, relative.rsplit('/', 1)[0], changed)
            write_bytes(root, relative, raw, expected)
            changed.append(relative)
            current = fingerprint(checked_path(root, relative, allow_missing=False))
            if current[-1] != row['artifact']['sha256']:
                raise SafetyError('Workflow destination changed after publication: ' + relative)
        ready[name] = {**row, 'fingerprint': list(current)}
    return ready


def inventory(root, owner_path, base, state, definition):
    from .workflow_lineage import latest, verify_record

    files = {}
    for name, binding in state['bindings'].items():
        kind, contract = next((kind, definition[kind][name]) for kind in
                              ('inputs', 'intermediate_files', 'final_files') if name in definition[kind])
        row = {'kind': kind, 'format': contract['format'], 'expectation': contract['expectation'],
               'location': binding['location'], 'selected_by': binding['selected_by'],
               'resolved_path': resolve(owner_path, base, binding['location'])}
        if kind == 'inputs':
            source = state['inputs'].get(name)
            row.update(status='ready' if source else 'absent', snapshot=source)
        else:
            row.update(status='expected', versions=[])
        files[name] = row
    for key, record in sorted(state['accepted'].items(), key=lambda item: item[1]['execution_number']):
        current, _ = latest(state, record['step_id'])
        live = key == current
        if live:
            try:
                verify_record(root, base, state, key)
            except SafetyError:
                live = False
        for name, output in record['outputs'].items():
            row = files[name]
            materialized = state.get('materialized_files', {}).get(name)
            status = 'ready' if live else 'superseded'
            if live and materialized and materialized['path'] == output['path']:
                if materialized['final']:
                    status = 'delivered'
                try:
                    current_file = fingerprint(checked_path(root, row['resolved_path']))
                    if current_file is None or current_file[-1] != output['artifact']['sha256']:
                        status = 'destination-changed'
                except (SafetyError, OSError):
                    status = 'destination-changed'
            pending = state.get('pending_publications', {}).get(name)
            if pending and pending['path'] == output['path']:
                status = 'awaiting-publication'
            row['versions'].append({'step': record['step_id'], 'attempt': record['attempt_id'],
                                    'status': status, **output})
            row['status'] = status
    if state['current_attempt']:
        relative = '/'.join((base, 'attempts', state['current_step'], state['current_attempt'], 'assignment.json'))
        assignment = read_json(checked_path(root, relative, allow_missing=False))
        for name, output in assignment['outputs'].items():
            draft = checked_path(root, base + '/' + output['path'])
            if draft.is_file():
                files[name]['draft'] = {'path': output['path'], 'status': 'awaiting-acceptance'}
                if files[name]['status'] == 'expected':
                    files[name]['status'] = 'awaiting-acceptance'
    if state['status'] in ('finished', 'cancelled'):
        for row in files.values():
            if row['status'] == 'expected':
                row['status'] = 'not-produced'
    return files
