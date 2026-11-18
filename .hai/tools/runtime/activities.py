"""Activity lifecycle operations. All caller-supplied narrative remains attributed."""
from environment_paths import STATE, PROFILES, INSTRUCTIONS, LEGACY
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import re
import os
import sys
import uuid
from activity_layout import artifact, version as layout_version, revision_root
from .workflow_artifacts import mkdirs
from .storage import SafetyError, checked_path, fingerprint, read_json, write_bytes, write_json, lock

_TOOLS = Path(__file__).resolve().parents[1]
for _part in ('roles', 'startup', 'activities'):
    sys.path.insert(0, str(_TOOLS / _part))
from discovery import discover, _validate_state, STEPS, STEP_VALUES

CURRENT = '00000000_000000_active'
ARTIFACTS = {'definition.md', 'analysis.md', 'decisions.md', 'plan.md', 'requirements.md'}
MUTATIONS = ('create', 'record', 'close', 'supplement', 'chat-post', 'invocation-allocate', 'usage-update', 'migrate-layout', 'work-cleanup')

def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def envelope(op, status='ok', result=None, changed=None, issues=None):
    return {'ok': status in ('ok', 'planned'), 'status': status, 'operation': op,
            'result': result or {}, 'changed_files': changed or [], 'issues': issues or []}

def required_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + ' must be nonempty text')
    return value

def provenance(request):
    p = request.get('provenance')
    if not isinstance(p, dict): raise ValueError('provenance is required')
    return 'source: ' + required_text(p.get('source'), 'provenance.source') + '; reason: ' + required_text(p.get('reason'), 'provenance.reason')

def store_path(root):
    state = read_json(checked_path(root, STATE, allow_missing=False))
    location = state.get('activities', {}).get('location')
    path = checked_path(root, location)
    if path.exists() and not path.is_dir(): raise SafetyError('Activity store is not a directory')
    for reserved in ('.hai', '.git', '.hai_env/roles', '.hai_env/skills', 'roles', 'skills', 'workflows', '.hai_env/agents', 'hai_roles_library', 'hai_agents_library', '.hai_env/config', '.hai_env/workflows',
                     '.hai_env/workflow-runs', STATE, INSTRUCTIONS, PROFILES, *LEGACY.values()):
        candidate, protected = (location.casefold(), reserved.casefold()) if os.name == 'nt' else (location, reserved)
        if candidate == protected or candidate.startswith(protected + '/') or protected.startswith(candidate + '/'):
            raise SafetyError('Activity store overlaps a protected path')
    return location

def rename_preflight():
    import ctypes, os, sys
    if os.name == 'nt': return 'windows'
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform.startswith('linux') and hasattr(libc, 'renameat2'):
        import errno
        probe = libc.renameat2
        probe.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        probe.restype = ctypes.c_int
        probe(-100, b'', -100, b'', 1)
        if ctypes.get_errno() in (errno.ENOSYS, errno.EINVAL): raise SafetyError('Atomic no-replace rename is unsupported by this system')
        return 'linux'
    if sys.platform == 'darwin' and hasattr(libc, 'renamex_np'): return 'darwin'
    raise SafetyError('Atomic no-replace rename is unavailable on this platform')

def rename_exclusive(source, destination):
    import ctypes, os
    platform = rename_preflight()
    if platform == 'windows':
        os.rename(source, destination)  # Windows rename fails when destination exists.
        return
    libc = ctypes.CDLL(None, use_errno=True)
    if platform == 'linux':
        func = libc.renameat2
        func.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        args = (-100, os.fsencode(source), -100, os.fsencode(destination), 1)
    else:
        func = libc.renamex_np
        func.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        args = (os.fsencode(source), os.fsencode(destination), 4)  # RENAME_EXCL
    func.restype = ctypes.c_int
    if func(*args):
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), str(destination))

def check_recording_files(root, base, proof, paths):
    """Compare fresh, safe workspace file hashes against supplied proof snapshots."""
    if not isinstance(paths, dict): raise SafetyError('Recording source and artifact paths required')
    evidence = proof['evidence']
    for kind, snapshot_key in (('sources','source_snapshots'), ('artifacts','artifact_snapshots')):
        mapping = paths.get(kind); expected = evidence.get(snapshot_key)
        if not isinstance(mapping,dict) or not isinstance(expected,dict) or set(mapping) != set(expected):
            raise SafetyError('Recording path mapping does not match evidence')
        for key, relative in mapping.items():
            if kind == 'artifacts':
                if not isinstance(relative,str) or not relative.startswith(base + '/'): raise SafetyError('Recording artifact must be inside the selected Activity')
            path = checked_path(root,relative,allow_missing=False)
            current = fingerprint(path)
            if current is None or current[-1] != expected[key]: raise SafetyError('Recording file changed or does not match proof: ' + relative)

def append_bytes(existing, text):
    return existing + (b'\n' if existing and not existing.endswith(b'\n') else b'') + text.encode('utf-8') + b'\n'

def handle(operation, workspace, request, apply):
    op = operation.split('.')[-1].split('/')[-1]
    root = Path(workspace).resolve(strict=True)
    changed = []
    try:
        fields = {'discover':set(), 'show':{'activity_id'}, 'create':{'initial_input','summary','layout_version','provenance'}, 'record':{'activity_id','steps','implementation_start','artifacts','input_append','log','provenance'}, 'close':{'activity_id','outcome','archive_label','outcome_text','recording','recording_requirement','recording_proof','recording_paths','provenance'}, 'supplement':{'activity_id','text','provenance'}}
        fields['chat-read'] = {'activity_id', 'after_sequence', 'limit'}
        fields['chat-post'] = {'activity_id', 'author', 'text', 'role', 'message_type', 'source_message_id', 'delivery_status', 'provenance'}
        fields['migrate-layout'] = {'activity_id', 'summary', 'allow_closed', 'provenance'}
        fields['work-cleanup'] = {'activity_id', 'paths', 'writers_ended', 'evidence_retained', 'provenance'}
        fields['invocation-allocate'] = {'activity_id', 'role', 'provenance'}
        fields['usage-read'] = {'activity_id'}
        fields['usage-update'] = {'activity_id', 'sources', 'pricing', 'reported_spend', 'provenance'}
        if not isinstance(request,dict) or (op in fields and set(request) - fields[op]): raise ValueError('Unknown or invalid request fields')
        location = store_path(root)
        def run():
            if apply and op in MUTATIONS:
                from .startup import require_mutation_context
                require_mutation_context(root)
            d = discover(root, location)
            if d['status'] == 'invalid': raise SafetyError('Activity store invalid: ' + str(d['issues']))
            if op == 'discover': return envelope(operation, result=d)
            if op in ('show', 'chat-read', 'usage-read'):
                if op in ('chat-read', 'usage-read') and apply:
                    raise ValueError(op + ' is read-only; omit --apply')
                ident = required_text(request.get('activity_id'), 'activity_id')
                matches = []
                for child in checked_path(root, location).iterdir():
                    state = read_json(checked_path(root, artifact(root, child.relative_to(root).as_posix(), 'state.json'), allow_missing=False))
                    if state.get('activity_id') == ident: matches.append((child, state))
                if len(matches) != 1: raise SafetyError('Activity ID not uniquely found')
                child, state = matches[0]
                if op == 'usage-read':
                    from . import usage
                    return envelope(operation, result=usage.read(root, child.relative_to(root).as_posix(), ident))
                if op == 'chat-read':
                    from . import chat
                    return envelope(operation, result=chat.read(root, child.relative_to(root).as_posix(), ident, request))
                return envelope(operation, result={'path': child.relative_to(root).as_posix(), 'state': state})
            prov = provenance(request)
            stamp = now()
            if op == 'migrate-layout':
                allow_closed = request.get('allow_closed', False)
                if type(allow_closed) is not bool: raise ValueError('allow_closed must be Boolean')
                selected = required_text(request.get('activity_id'), 'activity_id')
                if allow_closed and selected != d.get('activity_id'):
                    if d['status'] != 'current':
                        raise SafetyError('Closed-record migration needs an active owning work Activity')
                    matches = []
                    for child in checked_path(root, location).iterdir():
                        state = read_json(checked_path(root, artifact(root, child.relative_to(root).as_posix(), 'state.json'), allow_missing=False))
                        if state.get('activity_id') == selected and state.get('lifecycle') == 'closed': matches.append(child)
                    if len(matches) != 1: raise SafetyError('Closed Activity not uniquely selected')
                    from .activity_migration import migrate
                    result, created = migrate(root, matches[0].relative_to(root).as_posix(), selected,
                        request['provenance'], stamp, apply, request.get('summary'), allow_closed=True)
                    return envelope(operation, 'ok' if apply else 'planned', result, created)
            if op == 'create':
                initial = request.get('initial_input')
                if not isinstance(initial, str): raise ValueError('initial_input must be text')
                layout = request.get('layout_version', 2)
                if type(layout) is not int or layout not in (1, 2):
                    raise ValueError('layout_version must be 1 or 2')
                summary = request.get('summary')
                if summary is not None: required_text(summary, 'summary')
                if d['status'] != 'absent': raise SafetyError('A current Activity already exists')
                base = f'{location}/{CURRENT}'
                state = {'activity_id': str(uuid.uuid4()), 'lifecycle': 'active', 'created_at': stamp,
                         'closed_at': None, 'outcome': None, 'implementation_started_at': None,
                         'steps': {k: 'not_started' for k in sorted(STEPS)}}
                message = None
                if layout == 2:
                    from . import chat, activity_documents
                    if initial.strip(): message = chat.initial_message(state['activity_id'], initial, request['provenance'], stamp)
                    state.update(activity_layout_version=2, initial_message_id=message['message_id'] if message else None)
                    paths = [base + '/system/state.json', base + '/README.md', base + '/system/log.md', base + '/system/chat.jsonl']
                    payloads = [None, activity_documents.initial(state, summary),
                                f'# Activity log\n\n- {stamp} Created Activity ({prov}).\n'.encode(),
                                chat.encode(message) if message else b'']
                else:
                    paths = [base + '/' + n for n in ('state.json', 'input.md', 'log.md')]
                    payloads = [None, initial.encode(), f'# Activity log\n\n- {stamp} Created Activity ({prov}).\n'.encode()]
                if not apply: return envelope(operation, 'planned', {'state': state, 'paths': paths})
                store = checked_path(root, location)
                if not store.exists():
                    store.mkdir(parents=True); changed.append(location)
                checked_path(root, base).mkdir(); changed.append(base)
                if layout == 2: mkdirs(root, base + '/system', changed)
                for path, data in zip(paths, payloads):
                    if data is None: write_json(root, path, state)
                    else: write_bytes(root, path, data)
                    changed.append(path)
                if layout == 2:
                    readme = checked_path(root, base + '/README.md', allow_missing=False)
                    write_bytes(root, base + '/README.md', activity_documents.navigation(root, base, readme.read_bytes()), fingerprint(readme))
                if discover(root,location)['activity_id'] != state['activity_id']: raise SafetyError('Created Activity readback failed')
                return envelope(operation, result={'state': state, 'path': base}, changed=changed)
            ident = required_text(request.get('activity_id'), 'activity_id')
            if op == 'supplement':
                found = []
                for child in checked_path(root, location).iterdir():
                    s = read_json(checked_path(root, artifact(root, child.relative_to(root).as_posix(), 'state.json'), allow_missing=False))
                    if s.get('activity_id') == ident and s.get('lifecycle') == 'closed': found.append(child)
                if len(found) != 1: raise SafetyError('Closed Activity ID not uniquely found')
                text = required_text(request.get('text'), 'text')
                path = artifact(root, found[0].relative_to(root).as_posix(), 'log.md'); target = checked_path(root, path, allow_missing=False); old = fingerprint(target)
                data = append_bytes(target.read_bytes(), f'\n- {stamp} — Supplement ({prov}): {text}')
                if apply: write_bytes(root, path, data, old); changed.append(path)
                return envelope(operation, 'ok' if apply else 'planned', {'path': path}, changed)
            if d['status'] != 'current' or d['activity_id'] != ident: raise SafetyError('Selected ID is not the sole current Activity')
            base = d['path']; state_path = artifact(root, base, 'state.json'); state_target = checked_path(root, state_path, allow_missing=False)
            state_fp = fingerprint(state_target); state = read_json(state_target); _validate_state(state)
            if op == 'migrate-layout':
                from .activity_migration import migrate
                result, created = migrate(root, base, ident, request['provenance'], stamp, apply, request.get('summary'), allow_closed=request.get('allow_closed', False))
                return envelope(operation, 'ok' if apply else 'planned', result, created)
            if op == 'work-cleanup':
                from .activity_work import cleanup
                result, created = cleanup(root, base, request, apply)
                return envelope(operation, 'ok' if apply else 'planned', result, created)
            if op == 'usage-update':
                from . import usage
                result, created = usage.update(root, base, ident, request, stamp, apply, state_fp)
                return envelope(operation, 'ok' if apply else 'planned', result, created)
            if op == 'invocation-allocate':
                from . import invocations
                result = invocations.prepare(root, base, ident, request, stamp)
                if not apply:
                    return envelope(operation, 'planned', result)
                result, created = invocations.allocate(root, base, result, state_fp)
                return envelope(operation, result=result, changed=created)
            if op == 'chat-post':
                from . import chat
                relative, message, raw, expected = chat.prepare(root, base, ident, request, stamp)
                if not apply:
                    return envelope(operation, 'planned', {'path': relative, 'message': message})
                appended = chat.append(root, relative, ident, message, raw, expected)
                posted_changes = [] if appended is False else [relative]
                if layout_version(root, base) == 2 and state.get('initial_message_id') is None and message.get('role') == 'human':
                    state['initial_message_id'] = message['message_id']
                    write_json(root, state_path, state, state_fp); posted_changes.append(state_path)
                return envelope(operation, result={'path': relative, 'message': message, 'replayed': appended is False}, changed=posted_changes)
            if op == 'record':
                steps = request.get('steps', {})
                if not isinstance(steps, dict) or any(k not in STEPS or v not in STEP_VALUES for k,v in steps.items()): raise ValueError('invalid steps')
                start = request.get('implementation_start', False)
                if type(start) is not bool: raise ValueError('implementation_start must be boolean')
                if start and state['implementation_started_at'] is None: state['implementation_started_at'] = stamp
                state['steps'].update(steps); _validate_state(state)
                artifacts = request.get('artifacts', [])
                if not isinstance(artifacts, list): raise ValueError('artifacts must be a list')
                staged = []
                seen = set()
                for item in artifacts:
                    if not isinstance(item, dict): raise ValueError('invalid artifact')
                    candidate = item.get('name')
                    if layout_version(root, base) == 2:
                        allowed = isinstance(candidate, str) and (candidate == 'README.md' or candidate in ARTIFACTS or
                                  re.fullmatch(r'(?:results|evidence)/(?:[a-z0-9][a-z0-9._-]*/)*[a-z0-9][a-z0-9._-]*', candidate))
                    else: allowed = candidate in ARTIFACTS
                    if not allowed: raise ValueError('invalid artifact')
                    name = item['name']; text = required_text(item.get('text'), 'artifact.text'); reason = required_text(item.get('reason'), 'artifact.reason')
                    path = artifact(root, base, name); target = checked_path(root, path); fp = fingerprint(target)
                    key = path.casefold()
                    if any(key == old or key.startswith(old + '/') or old.startswith(key + '/') for old in seen):
                        raise ValueError('Artifact destinations overlap or alias')
                    seen.add(key)
                    if fp:
                        revdir = revision_root(root, base, name[:-3]); checked_path(root, revdir)
                        seq = 1
                        while checked_path(root, f'{revdir}/{stamp.replace("-", "").replace(":", "").replace("T", "_").removesuffix("Z")}_{seq:02}.md').exists(): seq += 1
                        rev = f'{revdir}/{stamp.replace("-", "").replace(":", "").replace("T", "_").removesuffix("Z")}_{seq:02}.md'
                        staged.append((rev, target.read_bytes(), None, True))
                    payload = text.encode('utf-8') if layout_version(root, base) == 2 else (text + f'\n\nRevision provenance: {prov}; reason: {reason}; recorded {stamp}.\n').encode()
                    staged.append((path, payload, fp, False))
                input_append = request.get('input_append')
                if input_append is not None:
                    if not isinstance(input_append, str): raise ValueError('input_append must be text')
                    if layout_version(root, base) == 2:
                        raise ValueError('Use typed chat-post for original human messages; input_append is legacy-only')
                    ipath = base + '/input.md'; it = checked_path(root, ipath, allow_missing=False); ifp = fingerprint(it)
                    staged.append((ipath, it.read_bytes() + input_append.encode('utf-8'), ifp, False))
                log = required_text(request.get('log'), 'log'); logpath = artifact(root, base, 'log.md'); lt = checked_path(root, logpath, allow_missing=False); lfp = fingerprint(lt)
                details = '; '.join(str(item['name']) + ': ' + str(item['reason']) for item in artifacts)
                staged.append((logpath, append_bytes(lt.read_bytes(), f'\n- {stamp} — {log} ({prov}).' + (' Artifacts: ' + details if details else '')), lfp, False))
                if not apply: return envelope(operation, 'planned', {'state': state, 'paths': [x[0] for x in staged] + [state_path]})
                for path,data,fp,revision in staged:
                    if revision or layout_version(root, base) == 2:
                        mkdirs(root, PurePosixPath(path).parent.as_posix(), changed)
                    write_bytes(root, path, data, fp); changed.append(path)
                write_json(root, state_path, state, state_fp); changed.append(state_path)
                if layout_version(root, base) == 2:
                    from .activity_documents import navigation
                    path = base + '/README.md'; target = checked_path(root, path, allow_missing=False)
                    updated = navigation(root, base, target.read_bytes())
                    if updated != target.read_bytes():
                        write_bytes(root, path, updated, fingerprint(target)); changed.append(path)
                if read_json(checked_path(root,state_path,allow_missing=False)) != state: raise SafetyError('State readback mismatch')
                return envelope(operation, result={'state': state}, changed=changed)
            if op == 'close':
                from .workflows import assert_activity_closable
                assert_activity_closable(root, ident)
                outcome = request.get('outcome'); label = request.get('archive_label'); text = required_text(request.get('outcome_text'), 'outcome_text'); rec = request.get('recording')
                if outcome not in ('completed','cancelled','stopped') or not isinstance(label,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+){0,4}',label): raise ValueError('invalid outcome or archive_label')
                if not isinstance(rec,dict) or rec.get('status') not in ('disabled','verified','pending','unavailable') or not isinstance(rec.get('details'),str): raise ValueError('explicit recording status and details required')
                enabled = read_json(checked_path(root, STATE, allow_missing=False)).get('features', {}).get('chronicles', {}).get('enabled')
                if type(enabled) is not bool: raise SafetyError('Recording enablement is unverified')
                requirement = request.get('recording_requirement', {'enabled': enabled, 'mandatory': False})
                if not isinstance(requirement,dict) or type(requirement.get('mandatory')) is not bool or type(requirement.get('enabled')) is not bool or requirement['enabled'] != enabled: raise ValueError('invalid or inconsistent recording_requirement')
                if rec.get('mandatory') is True: requirement = {**requirement, 'mandatory': True}
                from .recording_policy import effective, recoverable
                policy = effective(read_json(checked_path(root, STATE, allow_missing=False)), requirement['mandatory'])
                core_recording = (requirement['enabled'] or requirement['mandatory']) and not (rec['status'] == 'verified' and request.get('recording_proof') is not None)
                if rec['status'] == 'verified' and not core_recording:
                    from .recording import assess_closure
                    proof = request.get('recording_proof')
                    if not isinstance(proof,dict) or proof.get('recording_requirement') != requirement or not isinstance(proof.get('operation'),dict) or proof['operation'].get('activity_id') != ident or not assess_closure(proof)['ok'] or not (requirement['enabled'] or requirement['mandatory']):
                        raise SafetyError('Recording verification evidence is missing or insufficient')
                    check_recording_files(root, base, proof, request.get('recording_paths'))
                elif core_recording:
                    from . import chronicles
                    try:
                        core_result, _ = chronicles.synchronize(root, base, ident, {'provenance': request['provenance']}, stamp, False, state_fp, finalize=True)
                        rec = {'status': 'verified', 'details': 'Core chronicles synchronized and freshly verified through assigned completed source'}
                    except SafetyError as exc:
                        if policy['required'] or not recoverable(exc):
                            raise
                        # Only a failed read-only preparation can be downgraded.
                        # Partial writes, damaged artifacts and unsafe paths remain blockers.
                        core_recording = False
                        rec = {'status': 'unavailable', 'details': 'Recording interrupted; retained evidence preserved; coverage gap: ' + str(exc)}
                name = stamp.replace('-','').replace(':','').replace('T','_').removesuffix('Z') + '_' + label; dest = location + '/' + name; n = 2
                while checked_path(root,dest).exists(): dest = location + '/' + name + f'_{n:02}'; n += 1
                new_layout = layout_version(root, base) == 2
                outcome_path = base + ('/README.md' if new_layout else '/outcome.md')
                outcome_target = checked_path(root, outcome_path)
                outcome_fp = fingerprint(outcome_target)
                if not new_layout and outcome_fp is not None: raise SafetyError('outcome already exists')
                if new_layout and outcome_fp is None: raise SafetyError('Layout-2 Activity requires README.md before closure')
                prior_readme = outcome_target.read_bytes() if new_layout else b''
                state.update(lifecycle='closed',closed_at=stamp,outcome=outcome); _validate_state(state)
                if not apply: return envelope(operation,'planned',{'archive_path':dest,'state':state,'recording':rec})
                rename_preflight()
                if core_recording:
                    core_result, core_changed = chronicles.synchronize(root, base, ident, {'provenance': request['provenance']}, stamp, True, state_fp, finalize=True)
                    changed.extend(core_changed)
                    chronicles.verify(root, base, ident, closing=True)
                # Refresh registered usage before any lifecycle writes. Missing data
                # is recorded as unavailable; invalid state/partial writes stop closure.
                from . import usage
                usage_result, usage_changed = usage.update(root, base, ident, {'provenance': request['provenance']}, stamp, True, state_fp)
                changed.extend(usage_changed)
                if rec['status'] == 'verified' and not core_recording: check_recording_files(root, base, proof, request.get('recording_paths'))
                if core_recording: chronicles.verify(root, base, ident, closing=True)
                logpath = artifact(root, base, 'log.md'); logtarget = checked_path(root,logpath,allow_missing=False); logfp = fingerprint(logtarget)
                write_bytes(root,logpath,append_bytes(logtarget.read_bytes(), f'\n- {stamp} — Closed as {outcome}; Activity path moved from {base} to {dest} ({prov}).'),logfp); changed.append(logpath)
                report = (f'{"## Final outcome" if new_layout else "# Outcome"}\n\n{text}\n\nRecording: {rec["status"]} — {rec["details"]}\n\nProvenance: {prov}\n').encode()
                if new_layout:
                    revdir = revision_root(root, base, 'readme')
                    mkdirs(root, revdir, changed)
                    rev = revdir + '/' + stamp.replace('-', '').replace(':', '').replace('T', '_').removesuffix('Z') + '-before-closure.md'
                    write_bytes(root, rev, prior_readme); changed.append(rev)
                    report = prior_readme.rstrip() + b'\n\n' + report
                    from .activity_documents import navigation
                    report = navigation(root, base, report)
                write_bytes(root,outcome_path,report,outcome_fp); changed.append(outcome_path)
                if rec['status'] == 'verified' and not core_recording: check_recording_files(root, base, proof, request.get('recording_paths'))
                if core_recording: chronicles.verify(root, base, ident, closing=True)
                write_json(root,state_path,state,state_fp); changed.append(state_path)
                final_fingerprints = {p: fingerprint(checked_path(root,p,allow_missing=False)) for p in (state_path, outcome_path, logpath)}
                # Rename only to a newly reserved name, with no overwrite.
                import os
                if checked_path(root,dest).exists(): raise SafetyError('Archive destination appeared')
                if rec['status'] == 'verified' and not core_recording: check_recording_files(root, base, proof, request.get('recording_paths'))
                if core_recording: chronicles.verify(root, base, ident, closing=True)
                if any(fingerprint(checked_path(root,p,allow_missing=False)) != fp for p,fp in final_fingerprints.items()): raise SafetyError('Closure files changed before archival')
                rename_exclusive(checked_path(root,base,allow_missing=False), checked_path(root,dest)); changed.append(dest)
                if read_json(checked_path(root,artifact(root, dest, 'state.json'),allow_missing=False)) != state or discover(root,location)['status'] != 'absent': raise SafetyError('Closure readback mismatch')
                usage_result.update(path=artifact(root, dest, 'usage.md'), checkpoint_path=artifact(root, dest, 'usage.json'))
                return envelope(operation,result={'archive_path':dest,'state':state,'recording':rec,'usage':usage_result},changed=changed)
            raise ValueError('unsupported Activity operation')
        if apply and op in MUTATIONS:
            with lock(root): return run()
        return run()
    except (ValueError, TypeError, KeyError) as exc:
        return envelope(operation,'partial' if changed else 'input_error',changed=changed,issues=[str(exc)])
    except (SafetyError, OSError, UnicodeError) as exc:
        changed.extend(x for x in getattr(exc, 'changed_files', []) if x not in changed)
        return envelope(operation,'partial' if changed else 'blocked',changed=changed,issues=[str(exc)])
