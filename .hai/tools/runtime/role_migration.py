"""Explicit, backed-up migration of live HAI package names; history stays immutable."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import uuid

from role_upgrade import identity, references, transform, workflow
from role_state import MARKER
from activity_layout import artifact
from .storage import SafetyError, checked_path, fingerprint, read_json, write_bytes, write_json, lock
from .workflow_artifacts import mkdirs
from .activities import envelope, provenance, now, store_path, discover, rename_exclusive

ROOTS = (('.hai_env/agents', '.hai_env/roles'),
         ('.hai_env/config/agents', '.hai_env/config/roles'))


def _manifest(root, relative):
    """Fingerprint the complete tree, including empty folders and physical aliases."""
    path = checked_path(root, relative)
    if not path.exists():
        return None
    rows = []
    def visit(target):
        rel = target.relative_to(root).as_posix()
        checked_path(root, rel, allow_missing=False)
        info = target.lstat()
        suffix = target.relative_to(path).as_posix()
        if stat.S_ISDIR(info.st_mode):
            before = (info.st_dev, info.st_ino, info.st_mtime_ns)
            names = sorted(child.name for child in target.iterdir())
            if len({name.casefold() for name in names}) != len(names):
                raise SafetyError('Case-insensitive path collision: ' + rel)
            rows.append([suffix, 'directory', info.st_dev, info.st_ino])
            for name in names:
                visit(target / name)
            after = target.lstat()
            if before != (after.st_dev, after.st_ino, after.st_mtime_ns):
                raise SafetyError('Directory changed during inspection: ' + rel)
        elif stat.S_ISREG(info.st_mode):
            rows.append([suffix, 'file', *fingerprint(target)])
        else:
            raise SafetyError('Unsupported filesystem object: ' + rel)
    visit(path)
    return rows


def _raw(root, relative):
    target = checked_path(root, relative, allow_missing=False)
    before = fingerprint(target)
    content = target.read_bytes()
    if fingerprint(target) != before:
        raise SafetyError('Source changed during reading: ' + relative)
    return content


def _workflow_states(root, location):
    """Unfinished runs pin live definitions/packages and require explicit resolution."""
    sources = {}
    store = checked_path(root, location, allow_missing=False)
    # Observe only execution state; archived artifacts and their hashes stay untouched.
    for activity in sorted(store.iterdir()):
        if not activity.is_dir():
            continue
        checked_path(root, activity.relative_to(root).as_posix(), allow_missing=False)
        runs = activity / 'workflow-runs'
        if not runs.exists():
            continue
        rel = runs.relative_to(root).as_posix()
        manifest = _manifest(root, rel)
        for run in runs.iterdir():
            if not run.is_dir() or not (run / 'state.json').is_file():
                raise SafetyError('Resolve partial workflow execution before role migration: ' + run.relative_to(root).as_posix())
        for row in manifest:
            if row[1] != 'file' or len(row[0].split('/')) != 2 or row[0].split('/')[-1] != 'state.json':
                continue
            relative = rel + '/' + row[0]
            data = read_json(checked_path(root, relative, allow_missing=False))
            if not isinstance(data, dict) or data.get('status') not in ('finished', 'cancelled'):
                raise SafetyError('Resolve unfinished workflow execution before role migration: ' + relative)
            executor = data.get('executor')
            if isinstance(executor, dict) and executor.get('writers_ended') is not True:
                raise SafetyError('Workflow executor still has unresolved writers: ' + relative)
            sources[relative] = _manifest(root, relative)
    legacy = checked_path(root, '.hai_env/workflow-runs')
    if legacy.exists():
        raise SafetyError('Relocate legacy external workflow runs before role migration')
    return sources


def _target_path(suffix, *, library=False, settings=False):
    parts = suffix.split('/')
    if library and parts[0] == 'agents':
        parts[0] = 'roles'
    if not settings:
        index = 1 if library and parts[0] in ('agents', 'roles') else 0
        if len(parts) > index:
            parts[index] = identity(parts[index])
    if parts[-1] == 'agent-definition-manager.json':
        parts[-1] = 'role-definition-manager.json'
    if not settings and parts[-1] == 'SKILL.md':
        # Only the package entrypoint, not genuine nested skill entrypoints.
        depth = 3 if library else 2
        if len(parts) == depth and (not library or parts[0] == 'roles'):
            parts[-1] = 'ROLE.md'
    return '/'.join(parts)


def _plan(root, legacy_source=None):
    if legacy_source not in (None, "hai_agents_library"):
        raise SafetyError("This historical converter accepts only the explicitly selected hai_agents_library source")
    marker = checked_path(root, MARKER)
    if marker.exists():
        data = read_json(marker)
        raise SafetyError('Role migration already has retained ' + str(data.get('status')) + ' evidence; inspect it instead of retrying')
    if checked_path(root, '.hai/agents').exists():
        raise SafetyError('Upgrade the HAI core before migrating optional packages')
    context = discover(root, store_path(root))
    if context.get('status') != 'current':
        raise SafetyError('Role migration requires one valid current Activity')
    location = store_path(root)
    observed = {'.hai': _manifest(root, '.hai'),
                '.hai_env/config/model_profiles.json': _manifest(root, '.hai_env/config/model_profiles.json'),
                '.hai_env/config/agent_instructions.md': _manifest(root, '.hai_env/config/agent_instructions.md'),
                '.hai_env/config/state.json': _manifest(root, '.hai_env/config/state.json'),
                artifact(root, context['path'], 'state.json'): _manifest(root, artifact(root, context['path'], 'state.json'))}
    observed.update(_workflow_states(root, location))
    moves, files, directories = [], {}, set()
    names = set()
    selected_roots = ROOTS + ((('hai_agents_library','hai_roles_library'),) if legacy_source else ())
    for source, destination in selected_roots:
        observed[source] = _manifest(root, source)
        observed[destination] = _manifest(root, destination)
        if observed[destination] is not None:
            raise SafetyError('Canonical destination already exists; resolve mixed layouts explicitly: ' + destination)
        if observed[source] is None:
            continue
        if observed[source][0][1] != 'directory':
            raise SafetyError('Legacy package root must be a directory: ' + source)
        moves.append({'source': source, 'destination': destination})
        if source != '.hai_env/config/agents':
            package_root = checked_path(root, source + ('/agents' if source == 'hai_agents_library' else ''))
            if not package_root.is_dir():
                raise SafetyError('Legacy source library requires an agents folder')
            for child in package_root.iterdir():
                if child.is_dir():
                    names.add(identity(child.name))
                    if not (child / 'SKILL.md').is_file() or (child / 'ROLE.md').exists():
                        raise SafetyError('Expected one legacy SKILL.md package entry: ' + child.relative_to(root).as_posix())
    if not moves:
        raise SafetyError('No legacy role packages or settings require migration')
    for move in moves:
        source, destination = move['source'], move['destination']
        library = source == 'hai_agents_library'
        settings = source == '.hai_env/config/agents'
        nested_skills = []
        if not settings:
            for row in observed[source]:
                parts = row[0].split('/')
                entry_depth = 3 if library else 2
                if row[1] == 'file' and parts[-1] == 'SKILL.md' and len(parts) > entry_depth:
                    nested_skills.append(row[0].rsplit('/', 1)[0])
        for row in observed[source]:
            suffix, kind = row[:2]
            if suffix == '.':
                directories.add(destination)
                continue
            target = destination + '/' + _target_path(suffix, library=library, settings=settings)
            if target.casefold() in {key.casefold() for key in files} or target.casefold() in {key.casefold() for key in directories}:
                raise SafetyError('Transformed path collision: ' + target)
            if kind == 'directory':
                directories.add(target)
                continue
            raw = _raw(root, source + '/' + suffix)
            package_relative = suffix
            parts = suffix.split('/')
            in_package = (library and len(parts) >= 3 and parts[0] == 'agents') or (not library and not settings and len(parts) >= 2)
            if in_package and not any(suffix.startswith(prefix + '/') for prefix in nested_skills):
                package_relative = '/'.join(parts[2:] if library else parts[1:])
                raw = transform(package_relative, raw, package_names=names)
            elif not settings and not in_package and suffix.endswith('.md'):
                text = references(raw.decode('utf-8'), role_entry=False)
                if suffix == 'catalogue.md':
                    text = text.replace('| Agent |', '| Role |')
                    text = re.sub(r'\[SKILL\.md\]\(([^/()]+)/SKILL\.md\)', r'[ROLE.md](\1/ROLE.md)', text)
                if library and suffix == 'README.md':
                    text = re.sub(r'(?<![\w/])agents/', 'roles/', text)
                    text = text.replace('SKILL.md', 'ROLE.md').replace('HAI agent source library', 'HAI role source library').replace('individual agent versions', 'individual role versions').replace('agent version', 'role version')
                    text = text.replace('Environment-manager', 'runtime').replace('Leader', 'host coordinator')
                if library:
                    text = re.sub(r'(?<=\()agents/([^/()]+)/SKILL\.md(?=\))', r'roles/\1/ROLE.md', text)
                raw = text.encode('utf-8')
            files[target] = raw
    definition_root = checked_path(root, '.hai_env/workflows')
    observed['.hai_env/workflows'] = _manifest(root, '.hai_env/workflows')
    if definition_root.exists():
        for item in sorted(definition_root.iterdir()):
            relative = item.relative_to(root).as_posix()
            if not item.is_file() or item.suffix != '.md':
                raise SafetyError('Workflow definitions must be direct Markdown files: ' + relative)
            raw = _raw(root, relative)
            if re.search(rb'(?m)^workflow_format: 1\r?$', raw):
                files[relative] = workflow(raw)
                moves.append({'source': relative, 'destination': relative})
            elif not re.search(rb'(?m)^workflow_format: [234]\r?$', raw):
                raise SafetyError('Unsupported reusable workflow format: ' + relative)
    serial = {'observed': observed, 'moves': moves,
              'files': {path: hashlib.sha256(raw).hexdigest() for path, raw in sorted(files.items())},
              'directories': sorted(directories)}
    snapshot = hashlib.sha256(json.dumps(serial, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'expected_snapshot': snapshot, 'activity_id': context['activity_id'], 'activity_path': context['path'], 'activity_layout_version': context['state'].get('activity_layout_version', 1),
            'observed': observed, 'moves': moves, 'files': files, 'directories': sorted(directories)}


def _validate_stage(candidate, plan):
    from roles.role_tools import read_definition, audit
    from workflows.definition import parse_definition
    for origin in ('.hai_env/roles',) + (('hai_roles_library/roles',) if 'hai_agents_library' in plan['observed'] else ()):
        folder = candidate / origin
        if not folder.exists():
            continue
        for package in sorted(folder.iterdir()):
            if package.is_dir():
                read_definition(package / 'ROLE.md', candidate)
    report = audit(candidate)
    if not report['ok']:
        raise SafetyError('Staged role validation failed: ' + json.dumps(report['issues'], ensure_ascii=True))
    for path, raw in plan['files'].items():
        if path.startswith('.hai_env/workflows/'):
            parse_definition(raw, path)


def _recheck(root, plan):
    for relative, expected in plan['observed'].items():
        if _manifest(root, relative) != expected:
            raise SafetyError('Migration source or destination changed: ' + relative)


def _recheck_dependencies(root, plan):
    changing = {item['source'] for item in plan['moves']} | {item['destination'] for item in plan['moves']} | {'.hai_env/workflows'}
    old_workflows = plan['observed'].get('.hai_env/workflows')
    current_workflows = _manifest(root, '.hai_env/workflows')
    migrated = {item['source'].rsplit('/', 1)[1] for item in plan['moves'] if item['source'].startswith('.hai_env/workflows/')}
    remaining = lambda rows: [row for row in rows or [] if row[0] not in migrated]
    if remaining(old_workflows) != remaining(current_workflows):
        raise SafetyError('Reusable workflow definitions changed during migration')
    for relative, expected in plan['observed'].items():
        if relative not in changing and _manifest(root, relative) != expected:
            raise SafetyError('Migration dependency changed: ' + relative)


def _stage(root, relative, plan, changed):
    mkdirs(root, relative, changed)
    # Copy the inspected core, never old optional packages or historical Activities.
    for row in plan['observed']['.hai']:
        suffix, kind = row[:2]
        target = relative + '/.hai' + ('' if suffix == '.' else '/' + suffix)
        if kind == 'directory':
            mkdirs(root, target, changed)
        else:
            changed.append(write_bytes(root, target, _raw(root, '.hai/' + suffix)))
    for path in plan['directories']:
        mkdirs(root, relative + '/' + path, changed)
    for path, raw in sorted(plan['files'].items()):
        target = relative + '/' + path
        mkdirs(root, target.rsplit('/', 1)[0], changed)
        changed.append(write_bytes(root, target, raw))
    profiles = '.hai_env/config/model_profiles.json'
    if plan['observed'][profiles] is not None:
        mkdirs(root, relative + '/.hai_env/config', changed)
        changed.append(write_bytes(root, relative + '/' + profiles, _raw(root, profiles)))
    _validate_stage(checked_path(root, relative, allow_missing=False), plan)


def _apply(root, request, plan, changed):
    if request.get('writers_ended') is not True:
        raise SafetyError('Apply requires actual host attestation writers_ended:true after all package/configuration/definition writers have ended')
    if request.get('expected_snapshot') != plan['expected_snapshot']:
        raise SafetyError('Migration snapshot does not match; preview the current workspace again')
    migration_id = str(uuid.uuid4())
    base = plan['activity_path']
    if plan['activity_layout_version'] == 2:
        stage = base + '/work/coordinator/role-migration/' + migration_id + '/candidate'
        backup = base + '/history/role-migration/' + migration_id
    else:
        owned = base + '/files/role-migration/' + migration_id
        stage = owned + '/work/candidate'
        backup = owned + '/history'
    _stage(root, stage, plan, changed)
    _recheck(root, plan)
    stage_manifests = {move['destination']: _manifest(root, stage + '/' + move['destination']) for move in plan['moves']}
    evidence = {'role_migration_format_version': 1, 'migration_id': migration_id, 'status': 'prepared',
                'activity_id': plan['activity_id'], 'activity_layout_version': plan['activity_layout_version'], 'expected_snapshot': plan['expected_snapshot'],
                'created_at': now(), 'provenance': request['provenance'], 'writers_ended': True,
                'stage_path': stage, 'backup_path': backup, 'mappings': [], 'changed_files': [],
                'original_manifests': {move['source']: _manifest(root, move['source']) for move in plan['moves']}}
    for move in plan['moves']:
        evidence['mappings'].append({**move, 'backup': backup + '/originals/' + move['source'], 'published': False, 'original_retained': False})
    mkdirs(root, backup, changed)
    evidence_path = backup + '/evidence.md'
    text = '# HAI role migration evidence\n\nMigration: ' + migration_id + '\n\nSnapshot: ' + plan['expected_snapshot'] + '\n\n'
    text += '| Original | New location | Exact original retained at |\n| --- | --- | --- |\n'
    text += ''.join('| ' + item['source'] + ' | ' + item['destination'] + ' | ' + item['backup'] + ' |\n' for item in evidence['mappings'])
    changed.append(write_bytes(root, evidence_path, text.encode('utf-8')))
    marker_written = False
    marker_fp = None
    def save(status):
        nonlocal marker_written, marker_fp
        evidence['status'] = status
        evidence['changed_files'] = list(dict.fromkeys(changed + [MARKER]))
        changed.append(write_json(root, MARKER, evidence, marker_fp))
        marker_fp = fingerprint(checked_path(root, MARKER))
        marker_written = True
    try:
        save('prepared')
        for item in evidence['mappings']:
            source, destination = item['source'], item['destination']
            _recheck_dependencies(root, plan)
            if _manifest(root, stage + '/' + destination) != stage_manifests[destination]:
                raise SafetyError('Validated candidate changed before publication: ' + destination)
            # A previous move cannot authorize a stale next source or a new destination.
            expected = plan['observed'].get(source)
            if source.startswith('.hai_env/workflows/'):
                expected = next(row for row in plan['observed']['.hai_env/workflows'] if row[0] == source.rsplit('/', 1)[1])
                if fingerprint(checked_path(root, source)) != tuple(expected[2:]):
                    raise SafetyError('Workflow changed before publication: ' + source)
            elif _manifest(root, source) != expected:
                raise SafetyError('Package changed before publication: ' + source)
            if destination != source and _manifest(root, destination) is not None:
                raise SafetyError('Destination appeared before publication: ' + destination)
            mkdirs(root, item['backup'].rsplit('/', 1)[0], changed)
            rename_exclusive(checked_path(root, source, allow_missing=False), checked_path(root, item['backup']))
            changed.extend([source, item['backup']])
            item['original_retained'] = True
            save('prepared')
            mkdirs(root, destination.rsplit('/', 1)[0], changed) if '/' in destination else None
            _recheck_dependencies(root, plan)
            if _manifest(root, stage + '/' + destination) != stage_manifests[destination]:
                raise SafetyError('Validated candidate changed before publication: ' + destination)
            rename_exclusive(checked_path(root, stage + '/' + destination, allow_missing=False), checked_path(root, destination))
            changed.extend([stage + '/' + destination, destination])
            item['published'] = True
            save('prepared')
        _recheck_dependencies(root, plan)
        for item in evidence['mappings']:
            if item['source'] != item['destination'] and _manifest(root, item['source']) is not None:
                raise SafetyError('Legacy source reappeared during migration: ' + item['source'])
            if _manifest(root, item['backup']) != evidence['original_manifests'][item['source']]:
                raise SafetyError('Retained original changed during migration: ' + item['backup'])
            if _manifest(root, item['destination']) != stage_manifests[item['destination']]:
                raise SafetyError('Published candidate changed before completion: ' + item['destination'])
        evidence['completed_at'] = now()
        save('completed')
        return evidence
    except Exception as exc:
        changed.extend(getattr(exc, 'changed_files', []))
        if marker_written:
            evidence['failure'] = str(exc)
            try:
                save('partial')
            except Exception as marker_error:
                changed.extend(getattr(marker_error, 'changed_files', []))
        raise SafetyError(str(exc), list(dict.fromkeys(changed))) from exc


def _require_supported_core(root):
    from .startup import startup_context
    core = startup_context.check(root)
    if core['environment'] != 'valid' or core['instructions_status'] != 'loaded' or core.get('state_format_version') not in (2, 3):
        raise SafetyError('Role migration requires valid supported core state 2 or 3 and readable mandatory instructions')


def handle(workspace, request, apply=False):
    """Preview without writes; apply exactly one inspected, explicit migration."""
    changed = []
    try:
        if not isinstance(request, dict) or set(request) - {'provenance', 'expected_snapshot', 'writers_ended', 'legacy_source'}:
            raise ValueError('Migration accepts only provenance, expected_snapshot, writers_ended and optional legacy_source')
        provenance(request)
        root = Path(workspace).resolve(strict=True)
        if apply:
            _require_supported_core(root)
            with lock(root):
                _require_supported_core(root)
                plan = _plan(root, request.get('legacy_source'))
                result = _apply(root, request, plan, changed)
            return envelope('roles.migrate', result=result, changed=list(dict.fromkeys(changed)))
        plan = _plan(root, request.get('legacy_source'))
        return envelope('roles.migrate', 'planned', result={key: plan[key] for key in ('expected_snapshot', 'activity_id', 'activity_layout_version', 'moves')})
    except (SafetyError, ValueError, OSError, RuntimeError, UnicodeError) as exc:
        changed.extend(getattr(exc, 'changed_files', []))
        return envelope('roles.migrate', 'partial' if changed else 'blocked', changed=list(dict.fromkeys(changed)), issues=[{'code': 'role_migration', 'message': str(exc)}])
