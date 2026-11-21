"""Always-on source reconciliation into the Activity append-only conversation.

Caller owns the runtime lock. Operational state contains references, never bodies.
Legacy recording is read only during explicit migration.
"""
import copy
import hashlib
import json
from pathlib import Path
import uuid

from activity_layout import artifact, version
from . import chat, chronicles
from .storage import SafetyError, checked_path, fingerprint, read_json, write_json, write_bytes
from .recording_policy import RecordingInterruption


NO_SOURCE_WARNING = 'No registered native source; direct chat capture remains available'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def state_path(root, base):
    return artifact(root, base, 'recording.json') if version(root, base) == 1 else base + '/system/recording.json'


def empty(ident):
    return {'recording_format_version': 1, 'activity_id': ident, 'sources': [], 'migration': None, 'warnings': []}


def load(root, base, ident):
    path = checked_path(root, state_path(root, base))
    fp = fingerprint(path)
    data = read_json(path) if fp else empty(ident)
    if (not isinstance(data, dict) or set(data) != set(empty(ident))
            or type(data['recording_format_version']) is not int or data['recording_format_version'] != 1
            or data['activity_id'] != ident or not isinstance(data['sources'], list)
            or not isinstance(data['warnings'], list)):
        raise SafetyError('Invalid unified recording state')
    migration = data['migration']
    if migration is not None:
        required = {'status','backup','files','chat_prefix_bytes','chat_prefix_sha256'}
        if (not isinstance(migration,dict) or set(migration) != required
                or migration['status'] not in ('importing','retiring','complete')
                or migration['backup'] not in ('history/recording/before-unified-v1', base+'/history/recording/before-unified-v1')
                or type(migration['chat_prefix_bytes']) is not int or migration['chat_prefix_bytes'] < 0
                or not isinstance(migration['chat_prefix_sha256'],str) or len(migration['chat_prefix_sha256']) != 64
                or not isinstance(migration['files'],dict)):
            raise SafetyError('Invalid recording migration manifest')
        for relative, hash_value in migration['files'].items():
            if (not isinstance(relative,str) or not relative.startswith(('chronicles/','system/chronicles/'))
                    or not isinstance(hash_value,str) or len(hash_value) != 64):
                raise SafetyError('Migration can retire only its old managed transcript files')
            checked_path(root, base+'/'+relative)
    messages, raw, _ = chat.load(root, artifact(root, base, 'chat.jsonl'), ident)
    indexed = {m['message_id']: m for m in messages}
    sessions = set()
    for source in data['sources']:
        b = chronicles.assignment(root, source['binding'])
        if b['session_id'] in sessions: raise SafetyError('Duplicate recording source')
        sessions.add(b['session_id'])
        if not isinstance(source['index'], list): raise SafetyError('Invalid recording message references')
        for ref in source['index']:
            m = indexed.get(ref['chat_message_id'])
            if m is None or digest(m['text'].encode('utf-8')) != ref['sha256'] or m.get('source') != ref['source'] or m.get('source_message_id') != ref['native_key'] or m.get('role') != ('human' if ref['role'] == 'user' else 'assistant') or m.get('delivery_status') != ('received' if ref['role'] == 'user' else 'delivered'):
                raise SafetyError('Retained conversation changed or source reference disappeared')
    return data, fp, messages, raw


def assignment(root, value):
    value = copy.deepcopy(value)
    value['enabled_intervals'] = [{'start': chronicles.occurrence(value['session_id'], value['start_position']),
        'end': chronicles.occurrence(value['session_id'], value['end_position']) if value.get('end_position') is not None else None,
        'provenance': 'Authorized Activity source range; unified conversation recording is always enabled'}]
    return chronicles.assignment(root, value)


def source_key(session, message, epoch="0"):
    identity = ('message:' + message['message_id']) if message.get('message_id') else (
        'position:' + epoch + ':' + str(message['source_position']))
    return 'native:' + session + ':' + identity


def import_message(root, base, ident, b, original, stamp, apply, changed, key=None):
    relative = artifact(root, base, 'chat.jsonl')
    messages, raw, fp = chat.load(root, relative, ident)
    key = key or source_key(b['session_id'], original)
    source = {'session_id': b['session_id'], 'position': original['source_position'],
              'timestamp': original.get('timestamp'), 'message_id': original.get('message_id'),
              'turn_id': original.get('turn_id')}
    role = 'human' if original['role'] == 'user' else 'assistant'
    previous = next((m for m in messages if m.get('source_message_id') == key), None)
    if previous:
        if previous['text'] != original['text'] or previous.get('role') != role:
            raise SafetyError('Source identity conflicts with retained conversation')
        # Positions may change after verified source representation changes.
        source = previous['source']
        message = previous
    else:
        message = {'chat_format_version': 2, 'activity_id': ident, 'message_id': str(uuid.uuid4()),
            'sequence': len(messages) + 1, 'created_at': stamp, 'author': 'human-user' if role == 'human' else 'host-coordinator',
            'role': role, 'message_type': 'instruction' if role == 'human' else 'reply',
            'delivery_status': 'received' if role == 'human' else 'delivered',
            'text': original['text'], 'source_message_id': key, 'source': source,
            'provenance': {'source': 'Registered native session ' + b['session_id'],
                           'reason': 'Exact saved conversation occurrence; capture order differs from source order'}}
        if apply:
            if chat.append(root, relative, ident, message, raw, fp): changed.append(relative)
    return {'chat_message_id': message['message_id'], 'sha256': digest(original['text'].encode('utf-8')),
            'source': source, 'position': original['source_position'], 'native_key': key, 'role': original['role'], 'observed': {k: original[k] for k in ('timestamp','message_id','turn_id') if k in original}}


def previous_messages(source, messages):
    by_id = {m['message_id']: m for m in messages}
    return [dict(source_position=ref['position'], role=ref['role'], text=by_id[ref['chat_message_id']]['text'],
                 **ref.get('observed', {k:v for k,v in ref['source'].items() if k in ('timestamp','message_id','turn_id') and v is not None}))
            for ref in source['index']]


def inspect(root, base, source, messages, *, live=False):
    """Recheck every retained occurrence, not merely a tail cursor."""
    active = read_json(checked_path(root, artifact(root, base, 'state.json'), allow_missing=False))['lifecycle'] == 'active'
    b = copy.deepcopy(source.get('closure_binding') or source['binding']) if active or live else copy.deepcopy(source['binding'])
    try:
        raw, extracted, current = chronicles.read_assigned(b, root=root, base=base, include_commentary=True)
    except SafetyError as exc:
        from path_contract import foreign_absolute, native_source_path
        if foreign_absolute(b['path']) or not native_source_path(b['path']).exists():
            raise RecordingInterruption('Assigned source unavailable; retained chat is preserved: ' + str(exc)) from exc
        raise
    if source.get('original_started_at') is not None and extracted['original_started_at'] != source['original_started_at']:
        raise SafetyError('Original recording source start identity changed')
    previous = previous_messages(source, messages)
    rewrite = (source.get('prefix_bytes', 0) > len(raw)
        or digest(raw[:source.get('prefix_bytes', 0)]) != source.get('prefix_sha256', digest(b'')))
    if previous:
        if rewrite:
            from .source_continuity import indexed_matches
            matched = indexed_matches(previous, extracted['messages'])
            if any(not m.get('message_id') and not m.get('turn_id') for m in previous):
                raise RecordingInterruption('Changed source lacks stable message identities; retained chat is preserved')
            if (b['end_position'] is not None or len(b['enabled_intervals']) != 1
                    or b['enabled_intervals'][0]['end'] is not None):
                raise RecordingInterruption('Closed/discontinuous source rewrite needs explicit range reconciliation')
            lo, hi = matched[0]['source_position'], matched[-1]['source_position']
            if [m for m in extracted['messages'] if lo <= m['source_position'] <= hi] != matched:
                raise SafetyError('Inserted or reordered exchanges inside retained source')
            b['start_position'] = lo; b['enabled_intervals'][0]['start']['source_position'] = lo
            # Re-extract from the verified rebased assignment; no guessed history.
            raw, extracted, current = chronicles.read_assigned(b, root=root, base=base, include_commentary=True)
            extracted['retained_keys'] = {m['source_position']:ref['native_key'] for ref,m in zip(source['index'],matched)}
            extracted['coordinate_epoch'] = digest(json.dumps([source.get('coordinate_epoch','0'), source['prefix_sha256'], sorted(extracted['retained_keys'].items())], sort_keys=True).encode())[:20]
        else:
            from .source_continuity import snapshot
            by_position = {m['source_position']: m for m in snapshot(current)}
            if any(by_position.get(m['source_position']) != m for m in previous):
                raise SafetyError('Previously retained source message changed or disappeared')
    extracted.setdefault('coordinate_epoch', source.get('coordinate_epoch','0'))
    return b, raw, extracted, current


def check_overlaps(root, base, bindings):
    chronicles.check_overlaps(root, base, bindings)
    for child in checked_path(root, str(Path(base).parent).replace('\\', '/'), allow_missing=False).iterdir():
        if not child.is_dir() or child == root / base: continue
        otherbase = child.relative_to(root).as_posix()
        path = checked_path(root, state_path(root, otherbase))
        if not path.exists(): continue
        other = read_json(path)
        state = read_json(checked_path(root, artifact(root, otherbase, 'state.json'), allow_missing=False))
        other, _, messages, _ = load(root, otherbase, state['activity_id'])
        for source in other['sources']:
            b = source['binding']
            for new in bindings:
                if b['session_id'] != new['session_id']: continue
                # Source coordinates must still refer to the same native prefix.
                _, raw, _, _ = inspect(root, otherbase, source, messages)
                if len(raw) < source['prefix_bytes'] or digest(raw[:source['prefix_bytes']]) != source['prefix_sha256']:
                    raise SafetyError('Related Activity source changed; explicit boundary review required')
                if max(b['start_position'],new['start_position']) <= min(b['end_position'] if b['end_position'] is not None else float('inf'),new['end_position'] if new['end_position'] is not None else float('inf')):
                    raise SafetyError('Conversation assignment overlaps another Activity')


def synchronize(root, base, ident, request, stamp, apply, *, finalize=False):
    data, fp, messages, _ = load(root, base, ident)
    legacy = checked_path(root, artifact(root, base, 'chronicles/core.json'))
    if legacy.exists() and data['migration'] is None:
        raise SafetyError('Legacy transcripts require explicit recording migrate before unified synchronization')
    if data['migration'] and data['migration'].get('status') != 'complete':
        raise SafetyError('Recording migration is incomplete; resume recording migrate')
    owner_path = artifact(root, base, 'state.json')
    owner_fp = fingerprint(checked_path(root, owner_path, allow_missing=False))
    from environment_paths import STATE
    environment_fp = fingerprint(checked_path(root, STATE, allow_missing=False))
    def owner_fresh():
        if fingerprint(checked_path(root, STATE, allow_missing=False)) != environment_fp:
            raise SafetyError('Environment changed during recording')
        if fingerprint(checked_path(root, owner_path, allow_missing=False)) != owner_fp:
            raise SafetyError('Owning Activity changed during recording')
    candidate = copy.deepcopy(data); changed = []; warnings = []
    supplied = request.get('sources', [])
    if not isinstance(supplied, list): raise ValueError('sources must be a list')
    for value in supplied:
        b = assignment(root, value)
        existing = next((s for s in candidate['sources'] if s['binding']['session_id'] == b['session_id']), None)
        if existing:
            if existing['binding'] != b: raise SafetyError('Registered source assignment cannot silently change')
        else:
            candidate['sources'].append({'binding': b, 'index': [], 'prefix_bytes': 0, 'prefix_sha256': digest(b'')})
    if not candidate['sources']:
        warnings.append({'reason': NO_SOURCE_WARNING})
    check_overlaps(root, base, [s['binding'] for s in candidate['sources']])
    try:
        if apply and candidate['sources'] != data['sources']:
            intent = copy.deepcopy(candidate)
            intent['warnings'] = [{'reason': 'Synchronization pending; replay checks all registered sources'}]
            write_json(root, state_path(root, base), intent, fp); changed.append(state_path(root, base))
            fp = fingerprint(checked_path(root, state_path(root, base)))
        for source in candidate['sources']:
            # Reload messages after each append/source to retain all current references.
            retained, _, _ = chat.load(root, artifact(root, base, 'chat.jsonl'), ident)
            try:
                b, raw, extracted, current = inspect(root, base, source, retained)
            except (RecordingInterruption, FileNotFoundError) as exc:
                warnings.append({'session_id': source['binding']['session_id'], 'reason': str(exc)}); continue
            refs = []
            epoch = extracted['coordinate_epoch']
            if len({source_key(b['session_id'],m,epoch) for m in current}) != len(current):
                raise SafetyError('Ambiguous duplicate native message identities')
            retained_keys = extracted.get('retained_keys', {r['position']: r['native_key'] for r in source['index']})
            for m in current:
                owner_fresh()
                refs.append(import_message(root, base, ident, b, m, stamp, apply, changed, retained_keys.get(m['source_position'], source_key(b['session_id'],m,epoch))))
            chronicles.assert_fresh(b, raw, current, extracted['gaps'], include_commentary=True)
            warnings.extend(dict(g, session_id=b['session_id']) for g in extracted['gaps'])
            source['closure_binding'] = None
            if finalize and b['end_position'] is None:
                source['closure_binding'] = copy.deepcopy(b)
                positions = [m['source_position'] for m in current] + [g['source_position'] for g in extracted['gaps']]
                if positions:
                    b['end_position'] = max(positions)
                    b['enabled_intervals'] = [dict(i, end=chronicles.occurrence(b['session_id'], min(i['end']['source_position'], b['end_position']) if i['end'] else b['end_position'])) for i in b['enabled_intervals'] if i['start']['source_position'] <= b['end_position']]
            source.update(binding=b, index=refs, prefix_bytes=len(raw), prefix_sha256=digest(raw), coordinate_epoch=epoch, original_started_at=extracted['original_started_at'])
        candidate['warnings'] = warnings
        owner_fresh()
        if apply:
            if candidate != data or changed:
                write_json(root, state_path(root, base), candidate, fp); changed.append(state_path(root, base))
            load(root, base, ident)
        return {'status': 'recorded_with_gaps' if warnings else 'verified', 'coverage': 'partial' if warnings else 'complete',
                'warnings': warnings, 'source_count': len(candidate['sources']),
                'message_count': sum(len(s['index']) for s in candidate['sources']),
                'unsealed_sources': [s['binding']['session_id'] for s in candidate['sources'] if finalize and s['binding']['end_position'] is None],
                'chat_path': artifact(root, base, 'chat.jsonl'), 'recording_path': state_path(root, base)}, list(dict.fromkeys(changed))
    except Exception as exc:
        raise SafetyError(str(exc), list(dict.fromkeys(changed + getattr(exc, 'changed_files', [])))) from exc


def verify(root, base, ident, *, closing=False):
    data, _, messages, _ = load(root, base, ident)
    legacy = checked_path(root, artifact(root, base, 'chronicles/core.json'))
    if legacy.exists() and data['migration'] is None:
        raise SafetyError('Legacy transcripts require explicit recording migrate')
    warnings = []; missing = []; pending = False
    if data['migration'] and data['migration'].get('status') != 'complete':
        raise SafetyError('Recording migration is incomplete')
    if not data['sources']: warnings.append({'reason': NO_SOURCE_WARNING})
    keys = {m.get('source_message_id') for m in messages}
    for source in data['sources']:
        try:
            b, _, extracted, current = inspect(root, base, source, messages, live=closing)
        except (RecordingInterruption, FileNotFoundError) as exc:
            warnings.append({'session_id': source['binding']['session_id'], 'reason': str(exc)}); continue
        indexed = {r['native_key'] for r in source['index']}
        retained_keys = extracted.get('retained_keys', {r['position']: r['native_key'] for r in source['index']})
        expected = [retained_keys.get(m['source_position'], source_key(b['session_id'],m,extracted['coordinate_epoch'])) for m in current]
        pending = pending or any(k not in indexed for k in expected) or bool(extracted.get('retained_keys'))
        missing.extend(k for k in expected if k not in keys)
        warnings.extend(dict(g, session_id=b['session_id']) for g in extracted['gaps'])
    return {'status': 'needs_synchronization' if missing or pending else 'recorded_with_gaps' if warnings else 'verified',
            'coverage': 'partial' if missing or pending or warnings else 'complete', 'missing_messages': missing,
            'warnings': warnings, 'message_count': len(messages), 'activity_id': ident}


def migrate(root, base, ident, request, stamp, apply):
    """Preserve all old bytes, import indexed text, then retire old managed files.

    Interrupted imports replay by source identity. Predecessors remain until an
    exact backup and imported-message verification has succeeded.
    """
    from .workflow_artifacts import mkdirs
    if version(root, base) != 2: raise SafetyError('Run activity migrate-layout before recording migrate')
    data, fp, _, chat_before = load(root, base, ident)
    owner = artifact(root, base, 'state.json')
    owner_fp = fingerprint(checked_path(root, owner, allow_missing=False))
    def owner_fresh():
        if fingerprint(checked_path(root, owner, allow_missing=False)) != owner_fp:
            raise SafetyError('Owning Activity changed during migration')
    if data['migration'] and data['migration']['status'] in ('retiring', 'complete'):
        changed = []
        if apply and data['migration']['backup'].startswith(base+'/'):
            data['migration']['backup'] = data['migration']['backup'][len(base)+1:]
            write_json(root, state_path(root, base), data, fp); changed.append(state_path(root, base))
        finish_retirement(root, base, ident, data, apply, changed)
        backup = data['migration']['backup']
        return {'status': 'unchanged' if not changed else 'migrated', 'backup_path': backup if backup.startswith(base+'/') else base+'/'+backup}, changed
    old, _ = chronicles.load(root, base, ident)
    if old is None: raise SafetyError('No legacy recording ledger to migrate')
    if any('message_index' not in s for s in old['sources']):
        raise SafetyError('Legacy transcript without a proven message index requires explicit adoption; no text discarded')
    originals = []
    for relative in ('chronicles', 'system/chronicles'):
        directory = checked_path(root, base + '/' + relative)
        if directory.exists():
            for path in directory.rglob('*'):
                checked_path(root, path.relative_to(root).as_posix(), allow_missing=False)
                if path.is_file(): originals.append(path.relative_to(root).as_posix())
    backup = base + '/history/recording/before-unified-v1'
    if not apply:
        return {'status': 'planned', 'backup_path': backup, 'files': originals,
                'messages': sum(len(s['message_index']) for s in old['sources'])}, []
    changed = []
    try:
        for original in originals:
            relative = original[len(base)+1:]; target = backup + '/' + relative
            mkdirs(root, str(Path(target).parent).replace('\\', '/'), changed)
            payload = checked_path(root, original, allow_missing=False).read_bytes()
            p = checked_path(root, target)
            if p.exists():
                if p.read_bytes() != payload: raise SafetyError('Migration backup differs from retained original')
            else: write_bytes(root, target, payload); changed.append(target)
        owner_fresh()
        initial_chat = backup + '/chat-before.jsonl'
        if not checked_path(root, initial_chat).exists():
            write_bytes(root, initial_chat, chat_before); changed.append(initial_chat)
        original_chat = checked_path(root, initial_chat, allow_missing=False).read_bytes()
        if not chat_before.startswith(original_chat): raise SafetyError('Chat prefix changed during migration')
        candidate = copy.deepcopy(data)
        candidate['migration'] = {'status': 'importing', 'backup': 'history/recording/before-unified-v1', 'chat_prefix_bytes':len(original_chat), 'chat_prefix_sha256':digest(original_chat), 'files': {original[len(base)+1:]: digest(checked_path(root, original, allow_missing=False).read_bytes()) for original in originals}}
        write_json(root, state_path(root, base), candidate, fp); changed.append(state_path(root, base))
        for source in old['sources']:
            owner_fresh()
            fresh, _ = chronicles.load(root, base, ident)
            if fresh != old: raise SafetyError('Legacy evidence changed during migration')
            b = assignment(root, source['binding'])
            refs = [import_message(root, base, ident, b, m, stamp, True, changed) for m in source['message_index']]
            candidate['sources'] = [s for s in candidate['sources'] if s['binding']['session_id'] != b['session_id']]
            candidate['sources'].append({'binding': b, 'index': refs, 'prefix_bytes': source['prefix_bytes'], 'prefix_sha256': source['prefix_sha256'], 'original_started_at':source['original_started_at']})
        candidate['migration']['status'] = 'retiring'
        # Keep current sources until publication and readback are verified.
        write_json(root, state_path(root, base), candidate, fingerprint(checked_path(root, state_path(root, base))))
        load(root, base, ident)
        owner_fresh()
        finish_retirement(root, base, ident, candidate, True, changed)
        return {'status': 'migrated', 'backup_path': backup,
                'message_count': sum(len(s['index']) for s in candidate['sources'])}, list(dict.fromkeys(changed))
    except Exception as exc:
        raise SafetyError(str(exc), list(dict.fromkeys(changed + getattr(exc, 'changed_files', [])))) from exc


def finish_retirement(root, base, ident, data, apply, changed):
    migration = data['migration']
    backup_base = base + '/history/recording/before-unified-v1'
    _, raw, _ = chat.load(root, artifact(root, base, 'chat.jsonl'), ident)
    if digest(raw[:migration['chat_prefix_bytes']]) != migration['chat_prefix_sha256']:
        raise SafetyError('Migration must preserve the exact existing chat prefix')
    for relative, expected in migration['files'].items():
        backup = checked_path(root, backup_base + '/' + relative, allow_missing=False)
        original = checked_path(root, base + '/' + relative)
        if digest(backup.read_bytes()) != expected:
            raise SafetyError('Migration predecessor backup changed')
        if original.exists() and digest(original.read_bytes()) != expected:
            raise SafetyError('Original changed during migration; both versions preserved')
    if not apply: return
    for relative in migration['files']:
        path = checked_path(root, base + '/' + relative)
        if path.exists(): path.unlink(); changed.append(base + '/' + relative)
    for relative in ('chronicles', 'system/chronicles'):
        directory = checked_path(root, base + '/' + relative)
        if directory.exists():
            for sub in sorted(directory.rglob('*'), key=lambda x: len(x.parts), reverse=True):
                checked_path(root, sub.relative_to(root).as_posix(), allow_missing=False)
                if sub.is_dir(): sub.rmdir()
            directory.rmdir()
    if migration['status'] != 'complete':
        migration['status'] = 'complete'
        write_json(root, state_path(root, base), data, fingerprint(checked_path(root, state_path(root, base))))
        changed.append(state_path(root, base))

    # Retire the global optional switch only after the Activity evidence is safe.
    from environment_paths import STATE
    state_file = checked_path(root, STATE, allow_missing=False)
    before = fingerprint(state_file); state = read_json(state_file)
    if 'chronicles' in state['features']:
        original = backup_base + '/environment-state.json'
        if not checked_path(root, original).exists():
            write_bytes(root, original, state_file.read_bytes()); changed.append(original)
        state['features'].pop('chronicles')
        write_json(root, STATE, state, before); changed.append(STATE)


def check_closure(root, base, ident, expected):
    """While still active, verify the original live assignment through rename."""
    result = verify(root, base, ident, closing=True)
    if result['status'] == 'needs_synchronization' or result['warnings'] != expected['warnings']:
        raise SafetyError('Source gained missing conversation or changed after closure cutoff; synchronize again')
