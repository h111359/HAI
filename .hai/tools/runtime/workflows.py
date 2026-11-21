"""Activity-bounded workflow records; the host, never Python, dispatches agents."""
import copy
import hashlib
import json
import re
import sys
import uuid
from pathlib import Path, PurePosixPath
from activity_layout import invocation_path

from .storage import SafetyError, checked_path, fingerprint, read_json, write_bytes, write_json, lock
from .activities import envelope, provenance, now, store_path, discover
from .workflow_artifacts import observe, copy_snapshot, mkdirs, digest

ROOT = 'workflow-runs'
LEGACY_ROOT = '.hai_env/workflow-runs'
DEFINITIONS = '.hai_env/workflows'
TERMINAL = {'finished', 'cancelled'}
STATES = {'ready', 'prepared', 'running', 'waiting', 'blocked', 'paused', 'cancelling', 'publishing', *TERMINAL}
MUTATIONS = {'start', 'prepare-step', 'record-execution', 'complete-step', 'publish', 'pause', 'resume', 'cancel', 'retry-step'}


def canonical_json(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode('utf-8')


def ident(value, name):
    if not isinstance(value, str):
        raise ValueError(name + ' must be a canonical UUID')
    try:
        if str(uuid.UUID(value)) != value:
            raise ValueError()
    except ValueError as exc:
        raise ValueError(name + ' must be a canonical UUID') from exc
    return value


def assessment(value, name='assessment'):
    if (not isinstance(value, dict) or set(value) != {'accepted', 'author', 'evidence'}
            or value['accepted'] is not True or any(not isinstance(value[k], str) or not value[k].strip() for k in ('author', 'evidence'))):
        raise ValueError(name + ' requires accepted:true, author and evidence')
    return value


def activity(root, activity_id, active=False):
    ident(activity_id, 'activity_id')
    if active:
        from .startup import require_mutation_context
        require_mutation_context(root)
        current = discover(root, store_path(root))
        if current['status'] != 'current' or current['activity_id'] != activity_id:
            raise SafetyError('Workflow mutation requires the sole current owning Activity')
        return current
    from .activities import find
    location = store_path(root)
    if discover(root, location)['status'] == 'invalid':
        raise SafetyError('Activity store is invalid')
    return find(root, location, activity_id)


def run_root(root, activity_id):
    context = activity(root, activity_id)
    legacy = checked_path(root, LEGACY_ROOT + '/' + ident(activity_id, 'activity_id'))
    if legacy.exists():
        raise SafetyError('Legacy external workflow runs require explicit relocation into the owning Activity; no fallback is permitted')
    return context['path'] + '/' + ROOT


def run_base(root, activity_id, run_id):
    return run_root(root, activity_id) + '/' + ident(run_id, 'run_id')


def definition(root, relative, registered=True):
    from workflows.definition import parse_definition
    if not isinstance(relative, str) or (registered and not re.fullmatch(r'\.hai_env/workflows/[a-z][a-z0-9-]*\.md', relative)):
        raise ValueError('Definition must be one direct Markdown file in .hai_env/workflows')
    path = checked_path(root, relative, allow_missing=False)
    if path.suffix != '.md' or not path.is_file():
        raise ValueError('Definition must be a Markdown file')
    before = fingerprint(path)
    raw = path.read_bytes()
    parsed = parse_definition(raw, source=relative)
    if parsed['name'] != path.stem:
        raise ValueError('Workflow name must equal its filename')
    if fingerprint(path) != before:
        raise SafetyError('Workflow definition changed while reading')
    return parsed, raw


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise SafetyError('Duplicate workflow event key')
        out[key] = value
    return out


def load_run(root, activity_id, run_id, *, parent=None):
    """Read verified committed history; a stale projection is returned, not written."""
    from workflows.definition import parse_definition
    base = run_base(root, activity_id, run_id) if parent is None else parent + '/' + ident(run_id, 'run_id')
    directory = checked_path(root, base, allow_missing=False)
    if not directory.is_dir():
        raise SafetyError('Workflow run is not a directory')
    event_path = checked_path(root, base + '/events.jsonl', allow_missing=False)
    raw = event_path.read_bytes()
    if not raw or not raw.endswith(b'\n'):
        raise SafetyError('Partial workflow event history requires reconciliation')
    events, previous = [], None
    for line in raw.splitlines():
        event = json.loads(line, object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(SafetyError('Nonfinite workflow event value')))
        if not isinstance(event, dict) or set(event) != {'sequence', 'operation_id', 'operation', 'time', 'provenance', 'previous_hash', 'state', 'sha256'}:
            raise SafetyError('Invalid workflow event shape')
        expected = digest(canonical_json({k: v for k, v in event.items() if k != 'sha256'}))
        if event['sequence'] != len(events) + 1 or event['previous_hash'] != previous or event['sha256'] != expected:
            raise SafetyError('Workflow event history chain is inconsistent')
        ident(event['operation_id'], 'operation_id')
        state = event['state']
        if (not isinstance(state, dict) or state.get('workflow_run_format') not in (1, 2, 3)
                or state.get('activity_id') != activity_id or state.get('run_id') != run_id
                or state.get('revision') != event['sequence'] or state.get('status') not in STATES
                or not isinstance(state.get('integrity'), dict)):
            raise SafetyError('Invalid workflow state identity or version')
        events.append(event)
        previous = event['sha256']
    latest = copy.deepcopy(events[-1]['state'])
    projection = checked_path(root, base + '/state.json')
    stale = not projection.exists()
    if projection.exists():
        saved = read_json(projection)
        rev = saved.get('revision') if isinstance(saved, dict) else None
        if type(rev) is not int or rev < 1 or rev > len(events) or saved != events[rev - 1]['state']:
            raise SafetyError('Workflow projection conflicts with committed history')
        stale = rev != len(events)
    for relative, expected in latest['integrity'].items():
        if not isinstance(relative, str):
            raise SafetyError('Invalid workflow artifact key')
        actual = observe(root, base + '/' + relative)
        if actual != expected:
            raise SafetyError('Recorded workflow artifact changed: ' + relative)
    # A result/assignment created without a committed event cannot be silently reused.
    attempts = checked_path(root, base + '/attempts')
    if attempts.exists():
        for path in attempts.glob('*/*/*'):
            rel = path.relative_to(root).as_posix()
            checked_path(root, rel, allow_missing=False)
            if path.is_file() and (path.name in ('assignment.json', 'result.json') or re.fullmatch(r'rejection-\d+\.json', path.name)):
                key = path.relative_to(directory).as_posix()
                if key not in latest['integrity']:
                    raise SafetyError('Uncommitted workflow attempt metadata requires reconciliation: ' + key)
    if latest.get('workflow_run_format') == 2 and attempts.exists():
        for path in attempts.glob('*/*/accepted/**/*'):
            checked_path(root, path.relative_to(root).as_posix(), allow_missing=False)
            if path.is_file() and not any(path.relative_to(directory).as_posix() == key or path.relative_to(directory).as_posix().startswith(key + '/') for key in latest['integrity']):
                raise SafetyError('Uncommitted accepted output staging requires reconciliation')
    pinned = checked_path(root, base + '/definition.md', allow_missing=False)
    parsed = parse_definition(pinned.read_bytes(), source=base + '/definition.md', allow_legacy=True)
    if parsed['sha256'] != latest['definition']['sha256']:
        raise SafetyError('Pinned workflow definition hash differs')
    return latest, parsed, base, stale


def runs(root, activity_id):
    relative = run_root(root, activity_id)
    parent = checked_path(root, relative)
    if not parent.exists():
        return []
    if not parent.is_dir():
        raise SafetyError('Workflow Activity run store is not a directory')
    result = []
    for child in sorted(parent.iterdir()):
        checked_path(root, child.relative_to(root).as_posix(), allow_missing=False)
        ident(child.name, 'run_id')
        result.append(load_run(root, activity_id, child.name, parent=relative))
    return result


def unfinished(root, activity_id):
    """Read the Activity's run registration from committed records, with per-run issues."""
    rows, issues = [], []
    try:
        relative = run_root(root, activity_id)
        parent = checked_path(root, relative)
        children = sorted(parent.iterdir()) if parent.exists() else []
    except (SafetyError, OSError, ValueError) as exc:
        return {'status': 'unverified', 'runs': [], 'issues': [str(exc)]}
    for child in children:
        try:
            state, _, _, _ = load_run(root, activity_id, child.name, parent=relative)
        except (SafetyError, OSError, ValueError, TypeError, KeyError) as exc:
            issues.append(f'{child.name}: {exc}')
            continue
        if state['status'] not in TERMINAL:
            defaults = {'publishing': 'Complete pending file publication', 'ready': 'Prepare the next step',
                        'paused': 'Resume the run when authorized', 'prepared': 'Dispatch the prepared assignment'}
            rows.append({'run_id': state['run_id'], 'workflow': state['definition']['name'],
                         'status': state['status'], 'current_step': state['current_step'],
                         'current_attempt': state['current_attempt'], 'revision': state['revision'],
                         'pending_action': state.get('pending_action') or state.get('block_reason') or
                         defaults.get(state['status'])})
    return {'status': 'partial' if issues else 'valid', 'runs': rows, 'issues': issues}


def assert_activity_closable(root, activity_id):
    for state, _, _, _ in runs(root, activity_id):
        if state['status'] not in TERMINAL or (state.get('executor') and state['executor'].get('writers_ended') is not True):
            raise SafetyError('Activity has unfinished workflow run or unresolved writer: ' + state['run_id'])


def _slot(root, activity_id, selected):
    for state, _, _, _ in runs(root, activity_id):
        if state['run_id'] == selected:
            continue
        if (state.get('current_attempt') is not None or state.get('workflow_run_format') >= 2) and state['status'] not in {'paused', *TERMINAL}:
            raise SafetyError('Another workflow run holds this Activity execution slot: ' + state['run_id'])


def _commit(root, base, state, op, prov, changed, expected_events=None, expected_state=None):
    previous = None
    old_raw = b''
    events_path = checked_path(root, base + '/events.jsonl')
    if events_path.exists():
        old_raw = events_path.read_bytes()
        previous = json.loads(old_raw.splitlines()[-1])['sha256']
    event = {'sequence': state['revision'], 'operation_id': str(uuid.uuid4()), 'operation': op,
             'time': now(), 'provenance': prov, 'previous_hash': previous, 'state': copy.deepcopy(state)}
    event['sha256'] = digest(canonical_json(event))
    for relative, expected in state['integrity'].items():
        if observe(root, base + '/' + relative) != expected:
            raise SafetyError('Workflow artifact changed before transition: ' + relative)
    write_bytes(root, base + '/events.jsonl', old_raw + canonical_json(event) + b'\n', expected_events)
    changed.append(base + '/events.jsonl')
    state_path = checked_path(root, base + '/state.json')
    write_json(root, base + '/state.json', state, expected_state)
    changed.append(base + '/state.json')
    load_run(root, state['activity_id'], state['run_id'])


def _remember(root, base, state, relative):
    state['integrity'][relative] = observe(root, base + '/' + relative)


def _source(root, context, location):
    kind, tail = location.split(':', 1)
    relative = context['path'] + '/' + tail if kind == 'activity' else tail
    path = checked_path(root, relative, allow_missing=False)
    lowered = relative.casefold()
    forbidden = ('.git', '.hai_env/config', '.hai_env/roles', '.hai_env/agents', '.aws', '.codex', '.agents')
    if any(lowered == x or lowered.startswith(x + '/') for x in forbidden):
        raise SafetyError('Workflow input names protected metadata or secrets')
    if any(part.casefold() in {'.env', '.envrc', 'credentials', 'secrets.toml'} for part in path.parts):
        raise SafetyError('Workflow input names a protected secrets file')
    store = store_path(root)
    if lowered.startswith(store.casefold() + '/'):
        if relative != context['path'] and not relative.startswith(context['path'] + '/'):
            raise SafetyError('Workflow input belongs to another Activity or uses a noncanonical Activity path')
    legacy = LEGACY_ROOT.casefold()
    if lowered == legacy or lowered.startswith(legacy + '/'):
        raise SafetyError('Legacy external workflow artifacts require explicit relocation')
    owner_runs = context['path'] + '/' + ROOT
    expected = None
    if lowered == owner_runs.casefold() or lowered.startswith(owner_runs.casefold() + '/'):
        if relative != owner_runs and not relative.startswith(owner_runs + '/'):
            raise SafetyError('Workflow input uses a noncanonical run store path')
        parts = relative[len(owner_runs):].lstrip('/').split('/')
        if len(parts) < 2:
            raise SafetyError('Workflow input must identify an accepted output, not a run directory')
        prior, _, _, _ = load_run(root, context['activity_id'], parts[0])
        key = '/'.join(parts[1:])
        published = next((row for row in prior.get('materialized_files', {}).values()
                          if row['location'] == 'run:' + key), None)
        retained = published['path'] if published else key
        if retained not in prior['integrity'] or not any(
                retained == row['path'] for record in prior['accepted'].values() for row in record.get('outputs', {}).values()):
            raise SafetyError('Prior run input is not accepted output evidence')
        expected = prior['integrity'][retained]
    # Reject ancestors that would copy protected stores or other Activity records.
    if path.is_dir():
        for protected in (*forbidden, store, LEGACY_ROOT, owner_runs):
            candidate = checked_path(root, protected)
            if candidate == path or path in candidate.parents:
                raise SafetyError('Workflow directory input encloses protected content')
        for row in observe(root, relative)['manifest']:
            if any(part.casefold() in {'.git', '.aws', '.codex', '.env', '.envrc', 'credentials', 'secrets.toml'} for part in row['path'].split('/')):
                raise SafetyError('Workflow directory input contains protected content')
    observed = observe(root, relative)
    if expected is not None and observed != expected:
        raise SafetyError('Prior accepted workflow output changed before snapshot')
    return relative, observed


def _readiness(root, role_name, request):
    from .environment import config, role_tools
    catalogue = role_tools.audit(root)
    registrations = [row for row in catalogue['roles'] if row['name'] == role_name]
    if len(registrations) != 1:
        raise SafetyError('Workflow role is not validly registered: ' + role_name)
    rel = registrations[0]['definition']
    role_path = checked_path(root, rel, allow_missing=False)
    fields = role_tools.read_definition(role_path, root)
    contract_rel = str(PurePosixPath(rel).parent) + '/' + fields['metadata']['hai-configuration-contract'] if 'hai-configuration-contract' in fields.get('metadata', {}) else None
    if contract_rel:
        contract = config.load_contract(checked_path(root, contract_rel, allow_missing=False), role_name)
        saved = config.read_configuration(root, role_name, contract)
    else:
        if checked_path(root, '.hai_env/config/roles/' + role_name + '.json').exists():
            raise SafetyError('Saved role configuration has no declared owner contract: ' + role_name)
        saved = {'status': 'configured', 'settings': {}, 'issues': []}
    if saved['status'] not in ('configured', 'defaulted'):
        raise SafetyError('Workflow role configuration is unavailable: ' + str(saved['issues']))
    if saved['settings'].get('enabled') is False:
        raise SafetyError('Workflow role owned feature is disabled: ' + role_name)
    resolved = role_tools.resolve(root, rel, request.get('runtime'))
    if not resolved['ok']:
        raise SafetyError('Workflow role model/effort unavailable: ' + str(resolved['issues']))
    assessment(request.get('prerequisite_assessment'), 'prerequisite_assessment')
    authority = request.get('authority')
    if not isinstance(authority, str) or not authority.strip():
        raise ValueError('prepare/retry requires an actual authority reference')
    return {'role': role_name, 'definition': rel, 'definition_sha256': digest(role_path.read_bytes()),
            'configuration': saved, 'model': resolved['request'],
            'runtime': request.get('runtime'),
            'contract_sha256': digest(checked_path(root, contract_rel, allow_missing=False).read_bytes()) if contract_rel else None,
            'prerequisite_assessment': request['prerequisite_assessment'], 'authority': authority}


def _unchanged_readiness(root, step, assignment):
    pinned = assignment['readiness']
    current = _readiness(root, step['role'], pinned)
    if current != pinned:
        raise SafetyError('Role definition, configuration or model changed after preparation; stop and retry with reviewed prerequisites')


def _inputs(root, base, state, step):
    if state['workflow_run_format'] >= 2:
        from .workflow_lineage import inputs
        return inputs(root, base, state, step)
    result = {}
    incoming = state.get('last_accepted')
    output_map = {}
    if incoming:
        output_map = state['accepted'][incoming['key']]['outputs']
    for name, row in step['inputs'].items():
        kind, key = row['source'].split(':', 1)
        producer = state['inputs'].get(key) if kind == 'workflow' else output_map.get(key)
        if producer is None:
            if row['required']:
                raise SafetyError('Required workflow input is unavailable: ' + name)
            result[name] = None
            continue
        path = producer['path']
        actual = observe(root, base + '/' + path)
        if actual != producer['artifact']:
            raise SafetyError('Workflow predecessor input changed: ' + name)
        result[name] = {'path': path, 'artifact': actual, 'source': row['source']}
    return result


def _executor(value):
    if (not isinstance(value, dict) or not {'handle', 'mode', 'writers_ended', 'evidence'} <= set(value)
            or value['mode'] not in ('direct', 'spawned') or type(value['writers_ended']) is not bool
            or any(not isinstance(value[k], str) or not value[k].strip() for k in ('handle', 'evidence'))):
        raise ValueError('executor requires actual handle, direct/spawned mode, writers_ended Boolean and evidence')
    if value['mode'] == 'spawned' and not value.get('invocation_id'):
        raise ValueError('Spawned executor requires allocated invocation_id')
    return value


def _same_executor(first, second):
    return all(first.get(key) == second.get(key) for key in ('handle', 'mode', 'invocation_id'))


def _verified_executor(root, context, step, value):
    value = _executor(value)
    if value['mode'] == 'spawned':
        invocation = ident(value['invocation_id'], 'invocation_id')
        metadata = read_json(checked_path(root, invocation_path(root, context['path'], step['role'], invocation) + '/invocation.json', allow_missing=False))
        if (type(metadata.get('invocation_format_version')) is not int
                or metadata['invocation_format_version'] not in (1, 2)
                or metadata.get('activity_id') != context['activity_id'] or metadata.get('invocation_id') != invocation
                or metadata.get('role' if metadata['invocation_format_version'] == 2 else 'agent') != step['role']):
            raise SafetyError('Executor invocation is not allocated to this Activity and role')
    return value


def handle(operation, workspace, request, apply):
    root = Path(workspace).resolve(strict=True)
    op = operation.split('/')[-1].split('.')[-1]
    if op == 'install':
        from .workflow_config import install
        return install(operation, root, request, apply)
    changed = []
    common = {'activity_id', 'run_id', 'expected_revision', 'provenance'}
    fields = {'list': set(), 'validate': {'definition'}, 'show': {'activity_id', 'run_id'},
              'start': {'activity_id', 'definition', 'provenance', 'paths'}, 'publish': common,
              'prepare-step': common | {'runtime', 'authority', 'prerequisite_assessment'},
              'record-execution': common | {'step_id', 'attempt_id', 'status', 'executor', 'details'},
              'complete-step': common | {'step_id', 'attempt_id', 'result', 'assessment', 'executor', 'human_approval'},
              'pause': common | {'executor'}, 'resume': common | {'runtime', 'authority', 'prerequisite_assessment'},
              'cancel': common | {'executor'},
              'retry-step': common | {'step_id', 'attempt_id', 'executor', 'effect_resolution', 'runtime', 'authority', 'prerequisite_assessment'}}
    try:
        if op not in fields:
            return envelope(operation, 'unsupported', issues=['Unknown workflow operation'])
        if not isinstance(request, dict) or set(request) - fields[op]:
            raise ValueError('Unknown workflow request fields')
        if apply and op not in MUTATIONS:
            raise ValueError('Read-only workflow operation does not support --apply')

        def execute():
            if op in ('list', 'validate'):
                if op == 'validate':
                    parsed, _ = definition(root, request.get('definition'), registered=False)
                    return envelope(operation, result={'definition': parsed, 'structural_status': 'valid', 'semantic_review': 'not_checked', 'readiness': 'not_checked'})
                directory = checked_path(root, DEFINITIONS)
                found = []
                if directory.exists():
                    if not directory.is_dir():
                        raise SafetyError('Workflow definition collection is not a directory')
                    for path in sorted(directory.iterdir()):
                        if path.suffix.lower() != '.md':
                            continue
                        try:
                            parsed, _ = definition(root, path.relative_to(root).as_posix())
                            found.append({'name': parsed['name'], 'revision': parsed['revision'], 'path': path.relative_to(root).as_posix(), 'status': 'valid'})
                        except (SafetyError, ValueError, OSError) as exc:
                            found.append({'path': path.relative_to(root).as_posix(), 'status': 'invalid', 'issues': [str(exc)]})
                return envelope(operation, result={'definitions': found})

            context = activity(root, request.get('activity_id'), active=op in MUTATIONS)
            aid = request['activity_id']
            if op == 'start':
                from role_state import require_ready
                require_ready(root)
                provenance(request)
                parsed, raw = definition(root, request.get('definition'))
                configuration = None
                inventory = parsed['workflow_format'] == 4
                if not inventory and 'paths' in request:
                    raise ValueError('Per-run paths require workflow format 4')
                if parsed['workflow_format'] == 3:
                    from .workflow_config import load as load_configuration
                    configuration = load_configuration(root, parsed)
                    _slot(root, aid, None)
                rid = str(uuid.uuid4())
                base = run_base(root, aid, rid)
                if inventory:
                    from .workflow_files import bind, resolve
                    _slot(root, aid, None)
                    bindings, questions = bind(root, context['path'], base, parsed, request.get('paths', {}), store_path(root))
                    if questions:
                        return envelope(operation, 'needs_input', {'questions': questions, 'definition': parsed['name']})
                inputs = {}
                for name, row in parsed['inputs'].items():
                    if inventory and bindings[name].get('available') is False:
                        continue
                    location = bindings[name]['location'] if inventory else row['location']
                    source, evidence = _source(root, context, location)
                    kind = evidence['kind']
                    if inventory and kind != 'file':
                        raise SafetyError('Format-4 input must be a file: ' + source)
                    suffix = PurePosixPath(source).suffix if kind == 'file' else ''
                    inputs[name] = {'source': source, 'path': 'inputs/' + name + suffix, 'artifact': evidence}
                    if inventory:
                        bindings[name].update(artifact=evidence, snapshot=inputs[name]['path'])
                if inventory:
                    input_paths = {row['source']: row['artifact'] for row in inputs.values()}
                    for name in parsed['final_files']:
                        binding = bindings[name]
                        original = input_paths.get(resolve(context['path'], base, binding['location']))
                        if original and binding['baseline'][-1] != original['sha256']:
                            raise SafetyError('Update destination changed while binding input snapshot: ' + name)
                if checked_path(root, base).exists():
                    raise SafetyError('New workflow run destination already exists; preserve it for reconciliation')
                state = {'workflow_run_format': max(1, parsed['workflow_format'] - 1), 'activity_id': aid, 'run_id': rid,
                         'definition': {'name': parsed['name'], 'revision': parsed['revision'], 'sha256': parsed['sha256']},
                         'created_at': now(), 'updated_at': now(), 'revision': 1, 'status': 'ready',
                         'current_step': parsed['entry'], 'current_attempt': None,
                         'attempt_count': 0, 'step_attempt_counts': {}, 'inputs': inputs,
                         'last_accepted': None, 'accepted': {}, 'outcome': None, 'block_reason': None,
                         'executor': None, 'integrity': {}}
                if configuration is not None:
                    state['configuration'] = configuration
                if inventory:
                    state.update(bindings=bindings, materialized_files={}, pending_publications={})
                if not apply:
                    return envelope(operation, 'planned', {'state': state, 'path': base, 'readiness': 'checked at prepare-step'})
                mkdirs(root, base, changed)
                write_bytes(root, base + '/definition.md', raw); changed.append(base + '/definition.md')
                _remember(root, base, state, 'definition.md')
                if inventory:
                    write_json(root, base + '/bindings.json', {'activity_id': aid, 'run_id': rid, 'files': bindings})
                    changed.append(base + '/bindings.json')
                    _remember(root, base, state, 'bindings.json')
                for row in inputs.values():
                    copied = copy_snapshot(root, row['source'], base + '/' + row['path'], changed)
                    if copied != row['artifact']:
                        raise SafetyError('Workflow input changed after inspection; preserve partial snapshot for reconciliation', changed)
                    _remember(root, base, state, row['path'])
                _commit(root, base, state, op, request['provenance'], changed)
                return envelope(operation, result={'state': state, 'path': base}, changed=changed)

            state, parsed, base, stale = load_run(root, aid, request.get('run_id'))
            inventory = parsed['workflow_format'] == 4
            if op in ('prepare-step', 'record-execution', 'complete-step', 'retry-step', 'resume') and parsed['workflow_format'] not in (2, 3, 4):
                raise SafetyError('Legacy workflow runs are inspectable; resolve them before explicit role migration, then start a new migrated definition')
            if op == 'show':
                payload = {'state': state, 'path': base, 'projection_stale': stale}
                if inventory:
                    from .workflow_files import inventory as file_inventory
                    payload['files'] = file_inventory(root, context['path'], base, state, parsed)
                return envelope(operation, result=payload)
            provenance(request)

            def finish_publications(pending):
                from .workflow_files import publish
                event_fp = fingerprint(checked_path(root, base + '/events.jsonl', allow_missing=False))
                state_fp = fingerprint(checked_path(root, base + '/state.json'))
                finalized = copy.deepcopy(pending)
                finalized.update(finalized.pop('after_publication'))
                finalized.update(revision=pending['revision'] + 1, updated_at=now())
                if apply:
                    materialized = publish(root, context['path'], base, store_path(root), pending['pending_publications'], changed)
                    finalized['materialized_files'].update(materialized)
                finalized['pending_publications'] = {}
                if apply:
                    _commit(root, base, finalized, 'publish', request['provenance'], changed, event_fp, state_fp)
                return finalized

            # Retry acknowledgment must precede the now-stale revision check.
            key = str(request.get('step_id')) + '/' + str(request.get('attempt_id'))
            if op == 'complete-step' and key in state['accepted']:
                record = state['accepted'][key]
                replay_executor = _executor(request.get('executor'))
                if (record['result'] != request.get('result') or record['assessment'] != request.get('assessment')
                        or not _same_executor(record['executor'], replay_executor) or not replay_executor['writers_ended']
                        or (state['workflow_run_format'] >= 2 and record.get('human_approval_request') != request.get('human_approval'))):
                    raise SafetyError('Conflicting replay of accepted workflow completion')
                if state['status'] == 'publishing' and state['last_accepted']['key'] == key and apply:
                    state = finish_publications(state)
                return envelope(operation, result={'state': state, 'acceptance': record, 'replayed': True}, changed=changed)
            if type(request.get('expected_revision')) is not int or request['expected_revision'] != state['revision']:
                raise SafetyError('Workflow expected_revision is stale; inspect current state')
            if state['status'] in TERMINAL:
                raise SafetyError('Finished/cancelled workflow run is read-only')
            if op == 'publish':
                if not inventory or state['status'] != 'publishing':
                    raise SafetyError('Workflow has no pending file publication')
                return envelope(operation, 'ok' if apply else 'planned',
                                {'state': finish_publications(state), 'publications': state['pending_publications']}, changed)
            if state['status'] == 'publishing':
                raise SafetyError('Finish pending file publication before changing this run')
            events_fp = fingerprint(checked_path(root, base + '/events.jsonl', allow_missing=False))
            projection_fp = fingerprint(checked_path(root, base + '/state.json'))
            candidate = copy.deepcopy(state)
            candidate['updated_at'] = now()
            candidate['revision'] += 1
            step_id = state['current_step']
            step = parsed['steps'][step_id]
            attempt = state.get('current_attempt')

            def allocate():
                _slot(root, aid, state['run_id'])
                readiness = _readiness(root, step['role'], request)
                if state['attempt_count'] >= parsed['max_run_attempts'] or state['step_attempt_counts'].get(step_id, 0) >= parsed['max_step_attempts']:
                    limits = []
                    if state['attempt_count'] >= parsed['max_run_attempts']:
                        limits.append('max_run_attempts')
                    if state['step_attempt_counts'].get(step_id, 0) >= parsed['max_step_attempts']:
                        limits.append('max_step_attempts:' + step_id)
                    candidate.update(status='blocked', block_reason='attempt-limit', reached_limits=limits)
                    return None
                resolved = _inputs(root, base, state, step)
                number = state['step_attempt_counts'].get(step_id, 0) + 1
                new_attempt = f'attempt-{number:04}'
                relative = 'attempts/' + step_id + '/' + new_attempt
                if checked_path(root, base + '/' + relative).exists():
                    raise SafetyError('New workflow attempt destination already exists; preserve it for reconciliation')
                configured_outputs = None
                if state.get('workflow_run_format') == 2:
                    from .workflow_config import outputs as configured
                    configured_outputs = configured(root, state, step, number)
                declared_outputs = configured_outputs if configured_outputs is not None else step['outputs']
                if inventory:
                    from .workflow_files import assignment_outputs
                    declared_outputs = assignment_outputs(step, state, relative, context['path'], base)
                assignment = {'assignment_format': 4 if inventory else 3 if configured_outputs is not None else 2, 'activity_id': aid, 'run_id': state['run_id'],
                              'step_id': step_id, 'attempt_id': new_attempt, 'role': step['role'],
                              'instruction': step['instruction'], 'inputs': resolved,
                              'outputs': declared_outputs, 'results': step['results'], 'readiness': readiness,
                              'definition_sha256': parsed['sha256'], 'created_at': now()}
                if state['workflow_run_format'] >= 2:
                    from .workflow_lineage import chat_messages, checkpoint
                    assignment['execution_number'] = number
                    messages = chat_messages(root, context)
                    assignment['chat_sequence'] = messages[-1]['sequence'] if messages else 0
                    assignment['checkpoint_sha256'] = checkpoint(assignment)
                candidate.pop('pending_action', None)
                candidate.update(status='prepared', current_attempt=new_attempt, executor=None, block_reason=None,
                                 attempt_count=state['attempt_count'] + 1)
                candidate['step_attempt_counts'][step_id] = number
                if apply:
                    mkdirs(root, base + '/' + relative, changed)
                    if inventory and declared_outputs:
                        mkdirs(root, base + '/' + relative + '/files', changed)
                    if configured_outputs is not None:
                        for output in configured_outputs.values():
                            mkdirs(root, PurePosixPath(output['path']).parent.as_posix(), changed)
                    write_json(root, base + '/' + relative + '/assignment.json', assignment)
                    changed.append(base + '/' + relative + '/assignment.json')
                    _remember(root, base, candidate, relative + '/assignment.json')
                return assignment

            payload = {}
            if op == 'prepare-step':
                if state['status'] == 'prepared' and attempt:
                    relative = 'attempts/' + step_id + '/' + attempt + '/assignment.json'
                    _inputs(root, base, state, step)
                    _readiness(root, step['role'], request)
                    assignment = read_json(checked_path(root, base + '/' + relative))
                    _unchanged_readiness(root, step, assignment)
                    return envelope(operation, result={'state': state, 'assignment': assignment, 'replayed': True})
                if state['status'] not in ('ready', 'blocked') or attempt is not None:
                    raise SafetyError('Workflow is not ready for a new assignment')
                payload['assignment'] = allocate()
            elif op == 'retry-step':
                if request.get('step_id') != step_id or request.get('attempt_id') != attempt or not attempt or state['status'] not in ('blocked', 'paused'):
                    raise SafetyError('Retry does not identify a stopped unfinished attempt')
                ended = _verified_executor(root, context, step, request.get('executor'))
                if state.get('executor') and not _same_executor(ended, state['executor']):
                    raise SafetyError('Retry writer evidence does not identify current executor')
                if not ended['writers_ended'] or not isinstance(request.get('effect_resolution'), str) or not request['effect_resolution'].strip():
                    raise SafetyError('Retry requires ended writers and actual effect resolution')
                candidate.setdefault('effect_resolutions', []).append({'step_id': step_id, 'attempt_id': attempt,
                    'executor': ended, 'resolution': request['effect_resolution'], 'time': now()})
                payload['assignment'] = allocate()
            elif op == 'record-execution':
                if not attempt or request.get('step_id') != step_id or request.get('attempt_id') != attempt or state['status'] not in ('prepared', 'running', 'waiting', 'blocked', 'cancelling'):
                    raise SafetyError('Execution report does not identify the current attempt')
                executor = _verified_executor(root, context, step, request.get('executor'))
                if state['status'] == 'prepared':
                    assignment = read_json(checked_path(root, base + '/attempts/' + step_id + '/' + attempt + '/assignment.json', allow_missing=False))
                    _unchanged_readiness(root, step, assignment)
                    _inputs(root, base, state, step)
                status = request.get('status')
                if status not in ('running', 'waiting', 'blocked') or (status in ('running', 'waiting') and executor['writers_ended']):
                    raise ValueError('Execution status must be actual running/waiting/blocked with consistent writer evidence')
                if state['status'] == 'cancelling' and status != 'blocked':
                    raise SafetyError('Cancellation cannot silently resume execution')
                if state.get('executor') and not _same_executor(state['executor'], executor):
                    raise SafetyError('Executor identity changed within an attempt')
                if not isinstance(request.get('details'), str) or not request['details'].strip():
                    raise ValueError('Execution report requires details')
                candidate.update(status=status, executor=executor, block_reason=request['details'] if status == 'blocked' else None)
                if status == 'waiting':
                    candidate['pending_action'] = request['details']
                else:
                    candidate.pop('pending_action', None)
            elif op == 'complete-step':
                if not attempt or request.get('step_id') != step_id or request.get('attempt_id') != attempt or state['status'] not in ('running', 'waiting', 'blocked'):
                    raise SafetyError('Completion does not identify a started current attempt')
                executor = _verified_executor(root, context, step, request.get('executor'))
                if not state.get('executor') or not _same_executor(executor, state['executor']) or not executor['writers_ended']:
                    raise SafetyError('Completion requires the actual executor with verified ended writers')
                label = request.get('result')
                result = step['results'].get(label) if isinstance(label, str) else None
                relative = 'attempts/' + step_id + '/' + attempt
                assignment = read_json(checked_path(root, base + '/' + relative + '/assignment.json', allow_missing=False))
                try:
                    assessment(request.get('assessment'))
                    _unchanged_readiness(root, step, assignment)
                    if result is None:
                        raise ValueError('Undeclared workflow result')
                    for row in assignment['inputs'].values():
                        if row and observe(root, base + '/' + row['path']) != row['artifact']:
                            raise SafetyError('Assigned input changed before completion')
                    if state['workflow_run_format'] >= 2:
                        current_inputs = _inputs(root, base, state, step)
                        if current_inputs != assignment['inputs']:
                            raise SafetyError('Accepted source binding changed after preparation')
                        from .workflow_lineage import approval
                        human = approval(root, context, assignment, request.get('human_approval')) if result.get('gate') == 'human' else None
                        if result.get('gate') != 'human' and request.get('human_approval') is not None:
                            raise SafetyError('Human approval supplied to an undeclared checkpoint')
                    outputs = {}
                    for name in result['outputs']:
                        output = step['outputs'][name]
                        if state.get('workflow_run_format') == 2:
                            external = assignment['outputs'][name]['path']
                            location = relative + '/accepted/' + PurePosixPath(external).name
                            evidence = observe(root, external)
                            if checked_path(root, base + '/' + location).exists():
                                raise SafetyError('Uncommitted accepted copy already exists; preserve for reconciliation')
                            outputs[name] = {'path': location, 'configured_path': external, 'artifact': evidence,
                                             'format': output['format'], 'expectation': output['expectation']}
                        else:
                            tail = assignment['outputs'][name]['location'].split(':', 1)[1]
                            location = relative + '/' + tail
                            if inventory and not checked_path(root, base + '/' + location, allow_missing=False).is_file():
                                raise SafetyError('Format-4 output must be a regular file: ' + name)
                            outputs[name] = {'path': location, 'artifact': observe(root, base + '/' + location),
                                             'format': output['format'], 'expectation': output['expectation']}
                    kind, target = result['next'].split(':', 1)
                    publications = {}
                    if inventory:
                        from .workflow_files import publication_plan
                        publications = publication_plan(root, context['path'], base, store_path(root), state,
                                                        parsed, outputs, kind, target)
                except (SafetyError, ValueError) as exc:
                    candidate.pop('pending_action', None)
                    candidate.update(status='blocked', executor=executor, block_reason='invalid-output: ' + str(exc))
                    rejection = {'result': label, 'assessment': request.get('assessment'), 'reason': str(exc), 'time': now()}
                    if apply:
                        path = relative + '/rejection-' + f'{candidate["revision"]:04}' + '.json'
                        write_json(root, base + '/' + path, rejection); changed.append(base + '/' + path)
                        _remember(root, base, candidate, path)
                    payload['rejection'] = rejection
                else:
                    if state.get('workflow_run_format') == 2 and apply:
                        for output in outputs.values():
                            copied = copy_snapshot(root, output['configured_path'], base + '/' + output['path'], changed)
                            if copied != output['artifact']:
                                raise SafetyError('Output changed during accepted copy staging', changed)
                    record = {'result_format': 2 if state['workflow_run_format'] >= 2 else 1, 'activity_id': aid, 'run_id': state['run_id'], 'step_id': step_id,
                              'attempt_id': attempt, 'result': label, 'inputs': assignment['inputs'], 'outputs': outputs,
                              'assessment': request['assessment'], 'executor': executor, 'accepted_at': now(),
                              'next': result['next']}
                    if state['workflow_run_format'] >= 2:
                        record['human_approval'] = human
                        record['human_approval_request'] = request.get('human_approval')
                        record['execution_number'] = assignment['execution_number']
                    if apply:
                        write_json(root, base + '/' + relative + '/result.json', record); changed.append(base + '/' + relative + '/result.json')
                        _remember(root, base, candidate, relative + '/result.json')
                    for row in outputs.values():
                        candidate['integrity'][row['path']] = row['artifact']
                    candidate['accepted'][key] = record
                    candidate['last_accepted'] = {'key': key, 'step': step_id, 'attempt': attempt, 'result': label}
                    candidate.pop('pending_action', None)
                    candidate.update(status='finished' if kind == 'end' else 'ready',
                                     current_step=step_id if kind == 'end' else target,
                                     current_attempt=None, outcome=target if kind == 'end' else None,
                                     executor=None, block_reason=None)
                    if publications:
                        candidate['after_publication'] = {field: candidate[field] for field in
                                                          ('status', 'current_step', 'outcome')}
                        candidate.update(status='publishing', current_step=step_id, outcome=None,
                                         pending_publications=publications)
                    payload['acceptance'] = record
            elif op in ('pause', 'cancel'):
                executor = request.get('executor')
                if state.get('executor'):
                    executor = _verified_executor(root, context, step, executor)
                    if not _same_executor(executor, state['executor']):
                        raise SafetyError('Stop evidence must identify current executor')
                    if not executor['writers_ended']:
                        if op == 'pause':
                            raise SafetyError('Pause requires verified stopped writers')
                        candidate.update(status='cancelling', executor=executor)
                    else:
                        candidate.update(status='paused' if op == 'pause' else 'cancelled', executor=executor)
                else:
                    candidate.update(status='paused' if op == 'pause' else 'cancelled')
            elif op == 'resume':
                if state['status'] != 'paused':
                    raise SafetyError('Only a paused run can resume')
                _slot(root, aid, state['run_id'])
                if attempt and state.get('executor'):
                    candidate.update(status='blocked', block_reason='effect-resolution-required')
                elif attempt:
                    _readiness(root, step['role'], request)
                    assignment = read_json(checked_path(root, base + '/attempts/' + step_id + '/' + attempt + '/assignment.json', allow_missing=False))
                    _unchanged_readiness(root, step, assignment)
                    _inputs(root, base, state, step)
                    candidate.update(status='prepared', block_reason=None)
                else:
                    candidate.update(status='ready', block_reason=None)
            else:
                raise ValueError('Unsupported workflow mutation')

            if not apply:
                return envelope(operation, 'planned', {'state': candidate, **payload, 'projection_stale': stale})
            _commit(root, base, candidate, op, request['provenance'], changed, events_fp, projection_fp)
            if candidate['status'] == 'publishing':
                candidate = finish_publications(candidate)
            if 'rejection' in payload:
                return envelope(operation, 'blocked', {'state': candidate, **payload}, changed, [payload['rejection']['reason']])
            return envelope(operation, result={'state': candidate, **payload}, changed=changed)

        if apply and op in MUTATIONS:
            with lock(root):
                return execute()
        return execute()
    except (SafetyError, OSError, ValueError, TypeError, KeyError) as exc:
        changed.extend(x for x in getattr(exc, 'changed_files', []) if x not in changed)
        return envelope(operation, 'partial' if changed else 'input_error' if isinstance(exc, (ValueError, TypeError, KeyError)) else 'blocked',
                        changed=changed, issues=[str(exc)])
