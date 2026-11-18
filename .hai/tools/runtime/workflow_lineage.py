"""Format-3 accepted input binding and host-attributed human checkpoints."""
import hashlib
import json
from .storage import SafetyError
from .workflow_artifacts import observe


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode('utf-8')


def latest(state, step):
    records = [(key, row) for key, row in state['accepted'].items() if row['step_id'] == step]
    return max(records, key=lambda pair: pair[1].get('execution_number', int(pair[1]['attempt_id'].split('-')[-1]))) if records else (None, None)


def verify_record(root, base, state, key, historical=False, cache=None, active=None):
    cache = set() if cache is None else cache
    active = set() if active is None else active
    identity = (key, historical)
    if key in active:
        raise SafetyError('Cyclic accepted record identity')
    if identity in cache:
        return state['accepted'][key]
    record = state['accepted'].get(key)
    if record is None:
        raise SafetyError('Required source is not an accepted result: ' + str(key))
    active.add(key)
    try:
        for row in record['inputs'].values():
            if row is not None:
                verify_input(root, base, state, row, historical, cache, active)
        for row in record['outputs'].values():
            if observe(root, base + '/' + row['path']) != row['artifact']:
                raise SafetyError('Accepted internal output changed')
    finally:
        active.remove(key)
    cache.add(identity)
    return record


def verify_input(root, base, state, row, historical=False, cache=None, active=None):
    if observe(root, base + '/' + row['path']) != row['artifact']:
        raise SafetyError('Required retained input changed: ' + row['path'])
    key = row.get('acceptance_key')
    if key is None:
        initial = state['inputs'].get(row.get('workflow_input'))
        if initial is None or row['path'] != initial['path'] or row['artifact'] != initial['artifact']:
            raise SafetyError('Workflow input does not identify its pinned initial snapshot')
        return
    record = state['accepted'].get(key)
    if record is None or row.get('producer_result') != record['result']:
        raise SafetyError('Required accepted result identity is unavailable')
    output = record['outputs'].get(row['output_name'])
    if output is None or any(row.get(k) != output.get(k) for k in ('path', 'artifact', 'configured_path')):
        raise SafetyError('Required accepted output identity differs')
    historical = historical or row.get('historical_feedback') is True
    current_key, _ = latest(state, record['step_id'])
    if not historical and current_key != key:
        raise SafetyError('Required input is superseded: ' + key)
    if output.get('configured_path') and observe(root, output['configured_path']) != row['artifact']:
        raise SafetyError('Configured accepted handoff is missing or changed: ' + output['configured_path'])
    verify_record(root, base, state, key, historical, cache, active)


def inputs(root, base, state, step):
    result = {}
    cache, active = set(), set()
    for name, contract in step['inputs'].items():
        kind, source = contract['source'].split(':', 1)
        key, record = None, None
        if kind == 'workflow':
            producer = state['inputs'].get(source)
            binding = {'workflow_input': source}
        else:
            if kind == 'accepted':
                sid, label, output_name = source.split('/')
                key, record = latest(state, sid)
                if record is not None and record['result'] != label:
                    record = None
            else:
                incoming = state.get('last_accepted')
                key = incoming['key'] if incoming else None
                record = state['accepted'].get(key)
                output_name = source
            producer = record['outputs'].get(output_name) if record else None
            binding = {'acceptance_key': key, 'producer_step': record['step_id'] if record else None,
                       'producer_result': record['result'] if record else None, 'output_name': output_name}
        if producer is None:
            if contract['required']:
                raise SafetyError('Required accepted workflow input is unavailable: ' + name + ' (' + contract['source'] + ')')
            result[name] = None
            continue
        value = {**producer, **binding, 'source': contract['source']}
        if kind == 'feedback':
            value['historical_feedback'] = True
        verify_input(root, base, state, value, cache=cache, active=active)
        result[name] = value
    return result


def chat_messages(root, context):
    from .chat import load
    from activity_layout import artifact
    return load(root, artifact(root, context['path'], 'chat.jsonl'), context['activity_id'])[0]


def checkpoint(assignment):
    return hashlib.sha256(canonical({k: assignment[k] for k in ('activity_id', 'run_id', 'step_id', 'attempt_id', 'definition_sha256', 'inputs')})).hexdigest()


def approval(root, context, assignment, value):
    required = {'message_id', 'message_sha256', 'checkpoint_sha256', 'accepted', 'author', 'evidence'}
    if (not isinstance(value, dict) or set(value) != required or value['accepted'] is not True
            or any(not isinstance(value[k], str) or not value[k].strip() for k in required - {'accepted'})):
        raise SafetyError('Human checkpoint requires actual human message identity/hash and checkpoint-bound host semantic attestation')
    challenge = checkpoint(assignment)
    if value['checkpoint_sha256'] != challenge:
        raise SafetyError('Human approval applies to a different or stale checkpoint')
    message = next((m for m in chat_messages(root, context) if m['message_id'] == value['message_id']), None)
    if (message is None or message.get('role') != 'human' or message.get('message_type') != 'instruction'
            or message.get('delivery_status') != 'received' or message['sequence'] <= assignment['chat_sequence']):
        raise SafetyError('Approval must reference an actual received typed human instruction after checkpoint preparation')
    if hashlib.sha256(canonical(message)).hexdigest() != value['message_sha256']:
        raise SafetyError('Human approval message content identity differs')
    # The host assesses natural-language intent in the presented checkpoint context.
    # Typed chat attribution is not independently authenticated human identity.
    return {'attestation': value, 'message': message, 'checkpoint_sha256': challenge,
            'validation_boundary': 'host-attributed received human instruction; host semantic attestation, not independent authentication'}
