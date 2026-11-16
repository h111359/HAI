"""Explicit selected-Activity migration. Caller holds the lock and stops writers."""
import copy
from pathlib import Path, PurePosixPath
import re
import uuid

from activity_layout import version
from . import activity_documents, chat
from .storage import SafetyError, checked_path, fingerprint, read_json, write_bytes, write_json
from .workflow_artifacts import observe, mkdirs

DOCUMENTS = {'definition.md', 'analysis.md', 'decisions.md', 'plan.md', 'requirements.md'}
BUCKETS = {'results', 'evidence', 'history', 'work', 'workflow-runs'}
ROLE = re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z')


def migrate(root, base, ident, provenance, stamp, apply, summary=None, allow_closed=False):
    """Plan or perform one legacy migration; partial destinations are never reused."""
    root = Path(root).resolve(strict=True)
    from .activities import rename_preflight
    rename_preflight()
    if version(root, base) != 1:
        raise SafetyError('Only a legacy Activity can be migrated')
    if type(allow_closed) is not bool:
        raise ValueError('allow_closed must be Boolean')
    if not isinstance(provenance, dict) or set(provenance) != {'source', 'reason'} or any(
            not isinstance(v, str) or not v.strip() for v in provenance.values()):
        raise ValueError('Migration requires source and reason provenance')
    from .usage import stamp as validate_stamp
    validate_stamp(stamp)
    if summary is not None and (not isinstance(summary, str) or not summary.strip()):
        raise ValueError('summary must be nonblank text')
    state = read_json(checked_path(root, base + '/state.json', allow_missing=False))
    if state.get('activity_id') != ident or state.get('lifecycle') not in ('active', 'closed'):
        raise SafetyError('Migration requires the matching valid Activity')
    closed = state['lifecycle'] == 'closed'
    if closed and not allow_closed:
        raise SafetyError('Closed Activity migration requires explicit allow_closed:true')
    original_outcome = None
    if closed:
        original_outcome = checked_path(root, base + '/outcome.md', allow_missing=False).read_bytes()
        original_outcome.decode('utf-8')
    from .workflows import runs
    for run, _, _, _ in runs(root, ident):
        if run.get('executor') and run['executor'].get('writers_ended') is not True:
            raise SafetyError('Workflow executor has unresolved writers; stop and record them before migration')
    history = 'history/migrations/' + stamp.replace('-', '').replace(':', '').replace('T', '_').removesuffix('Z')
    report = base + '/evidence/migrations/activity-layout.json'
    if checked_path(root, base + '/system').exists() or checked_path(root, report).exists():
        raise SafetyError('Mixed or previously attempted migration requires explicit reconciliation')
    if checked_path(root, base + '/' + history).exists():
        raise SafetyError('Migration history destination already exists')
    before = observe(root, base)
    existing_names = {row['path'].casefold(): row['path'] for row in before['manifest']}
    if len(existing_names) != len(before['manifest']):
        raise SafetyError('Case-aliased Activity paths require explicit reconciliation')
    inspected = {row['path']: fingerprint(checked_path(root, base + '/' + row['path'], allow_missing=False))
                 for row in before['manifest'] if row['kind'] == 'file'}
    moves = []

    def plan(source, target):
        src, dst = base + '/' + source, base + '/' + target
        parent = PurePosixPath(target)
        while parent.as_posix() != '.':
            folded = parent.as_posix().casefold()
            if folded in existing_names and existing_names[folded] != parent.as_posix():
                raise SafetyError('Case-aliased migration destination: ' + dst)
            parent = parent.parent
        if checked_path(root, dst).exists():
            raise SafetyError('Migration destination already exists: ' + dst)
        moves.append({'source': source, 'destination': target, 'artifact': observe(root, src)})

    # Required original input remains exact evidence, even when it is an empty file.
    original_input = checked_path(root, base + '/input.md', allow_missing=False).read_bytes()
    checked_path(root, base + '/log.md', allow_missing=False)
    context = chat.initial_message(ident, original_input.decode('utf-8'), provenance, stamp,
                                   role='system', message_type='legacy-input')
    messages, old_chat, _ = chat.load(root, base + '/chat.jsonl', ident)
    context['sequence'] = len(messages) + 1
    for path in sorted(checked_path(root, base, allow_missing=False).iterdir()):
        name = path.name
        canonical = BUCKETS | DOCUMENTS | {'state.json', 'input.md', 'outcome.md', 'README.md',
            'log.md', 'chat.jsonl', 'usage.md', 'usage.json', 'chronicles', 'files'}
        if name not in canonical and name.casefold() in {item.casefold() for item in canonical}:
            raise SafetyError('Noncanonical Activity artifact casing: ' + name)
        if name in BUCKETS:
            if not path.is_dir():
                raise SafetyError('Activity bucket is not a directory: ' + name)
            continue
        if name in ('state.json', 'input.md', 'README.md', 'outcome.md'):
            plan(name, history + '/' + name)
        elif name in ('log.md', 'chat.jsonl', 'usage.md', 'usage.json'):
            plan(name, 'system/' + name)
        elif name in DOCUMENTS:
            plan(name, 'results/' + name)
        elif name == 'chronicles':
            if not path.is_dir():
                raise SafetyError('Chronicles must be a directory')
            for child in sorted(path.iterdir()):
                if child.is_file() and child.suffix == '.md':
                    continue
                plan('chronicles/' + child.name, 'system/chronicles/' + child.name)
        elif name == 'files':
            if not path.is_dir():
                raise SafetyError('Legacy files must be a directory')
            for child in sorted(path.iterdir()):
                source = 'files/' + child.name
                if child.name == 'agent-invocations':
                    if not child.is_dir():
                        raise SafetyError('Legacy agent invocations must be a directory')
                    for invocation in sorted(child.iterdir()):
                        metadata = read_json(checked_path(root, base + '/' + source + '/' + invocation.name + '/invocation.json', allow_missing=False))
                        agent = metadata.get('role') if metadata.get('invocation_format_version') == 2 else metadata.get('agent')
                        try:
                            canonical_id = str(uuid.UUID(invocation.name)) == invocation.name
                        except ValueError:
                            canonical_id = False
                        if (not invocation.is_dir() or not canonical_id or type(metadata.get('invocation_format_version')) is not int
                                or metadata['invocation_format_version'] not in (1, 2)
                                or metadata.get('activity_id') != ident or metadata.get('invocation_id') != invocation.name
                                or not isinstance(agent, str) or not ROLE.fullmatch(agent) or len(agent) > 64):
                            raise SafetyError('Invalid invocation identity; preserve it for explicit inspection')
                        destination = ('history/legacy-material/agent-work/' if closed else 'work/agents/')
                        plan(source + '/' + invocation.name, destination + agent + '/' + invocation.name)
                elif child.name == 'revisions':
                    plan(source, 'history/legacy-revisions')
                elif child.name == 'test-work':
                    plan(source, 'work/test-work')
                else:
                    if child.name == 'questionnaires':
                        plan(source, 'results/questionnaires')
                    else:
                        plan(source, 'history/legacy-material/files/' + child.name)
        else:
            # Unknown material is retained under an explicit, reviewable mapping.
            plan(name, 'history/legacy-material/root/' + name)
    destinations = [row['destination'].casefold() for row in moves]
    if len(destinations) != len(set(destinations)):
        raise SafetyError('Migration has aliased destinations')
    container = None
    if checked_path(root, base + '/files').exists():
        container = {'source': 'files', 'destination': 'history/legacy-material/empty-files-containers'}
        if checked_path(root, base + '/' + container['destination']).exists():
            raise SafetyError('Migration legacy-container destination already exists')
    updated = copy.deepcopy(state)
    updated.update(activity_layout_version=2, initial_message_id=context['message_id'])
    result = {'activity_id': ident, 'layout_before': 1, 'layout_after': 2, 'history_path': base + '/' + history,
              'evidence_path': report, 'mapping': moves, 'status': 'planned' if not apply else 'completed'}
    result['container_relocation'] = container
    if not apply:
        return result, []
    changed = []
    manifest = {'activity_layout_migration_format': 1, 'activity_id': ident, 'recorded_at': stamp,
        'provenance': provenance, 'status': 'prepared', 'mapping': moves,
        'before_manifest': before['manifest'], 'after_manifest_excludes': ['evidence/migrations/activity-layout.json']}
    manifest['container_relocation'] = container
    report_fp = None
    try:
        if observe(root, base) != before:
            raise SafetyError('Activity changed after migration preflight')
        for relative, expected in inspected.items():
            if fingerprint(checked_path(root, base + '/' + relative, allow_missing=False)) != expected:
                raise SafetyError('Activity fingerprint changed after migration preflight: ' + relative)
        mkdirs(root, PurePosixPath(report).parent.as_posix(), changed)
        write_json(root, report, manifest); changed.append(report)
        report_fp = fingerprint(checked_path(root, report, allow_missing=False))
        for row in sorted(moves, key=lambda row: row['source'] == 'state.json'):
            # The original state moves last; no success has been published yet.
            if row['source'] == 'state.json':
                continue
            _move(root, base, row, changed, inspected)
        if container is not None:
            empty_tree = observe(root, base + '/files')
            if any(row['kind'] != 'directory' for row in empty_tree['manifest']):
                raise SafetyError('Unexpected content remains in legacy files; preserve partial migration for inspection')
            _move(root, base, {**container, 'artifact': empty_tree}, changed, {})
        new_chat = base + '/system/chat.jsonl'
        mkdirs(root, base + '/system', changed)
        chat.append(root, new_chat, ident, context, old_chat,
                    fingerprint(checked_path(root, new_chat)))
        changed.append(new_chat)
        state_move = next(row for row in moves if row['source'] == 'state.json')
        _move(root, base, state_move, changed, inspected)
        write_json(root, base + '/system/state.json', updated); changed.append(base + '/system/state.json')
        # Former legacy container directories are retained under history as well.
        readme = activity_documents.initial(updated, summary)
        readme = activity_documents.navigation(root, base, readme)
        if original_outcome is not None:
            readme += b'\n\n## Final outcome\n\n' + original_outcome
        write_bytes(root, base + '/README.md', readme); changed.append(base + '/README.md')
        for row in moves:
            expected = row['artifact']
            if row['destination'] == 'system/chat.jsonl':
                if checked_path(root, new_chat).read_bytes() != old_chat + chat.encode(context):
                    raise SafetyError('Migrated chat does not preserve the exact old prefix')
            elif observe(root, base + '/' + row['destination']) != expected:
                raise SafetyError('Migrated artifact differs from preserved original: ' + row['destination'])
        # Verify preserved buckets as well as moved entries; a concurrent change
        # to an untouched results/history file must not become migration evidence.
        remapping = sorted(moves + ([container] if container else []), key=lambda row: len(row['source']), reverse=True)
        for original in before['manifest']:
            old = original['path']
            mapping = next((row for row in remapping if old == row['source'] or old.startswith(row['source'] + '/')), None)
            target = mapping['destination'] + old[len(mapping['source']):] if mapping else old
            path = checked_path(root, base + '/' + target, allow_missing=False)
            if original['kind'] == 'directory':
                if not path.is_dir():
                    raise SafetyError('Preserved migration directory changed: ' + target)
            elif old != 'chat.jsonl':
                expected = {key: original[key] for key in ('kind', 'sha256', 'bytes')}
                if observe(root, base + '/' + target) != expected:
                    raise SafetyError('Preserved migration file changed: ' + target)
        final = observe(root, base)
        manifest.update(status='completed', after_manifest=[row for row in final['manifest']
            if row['path'] != 'evidence/migrations/activity-layout.json'])
        write_json(root, report, manifest, report_fp)
        result['state'] = updated
        return result, list(dict.fromkeys(changed))
    except Exception as exc:
        changed.extend(path for path in getattr(exc, 'changed_files', []) if path not in changed)
        # Preserve all partial changes. A retained report blocks a blind retry.
        if report_fp is not None:
            try:
                manifest.update(status='partial', error=str(exc))
                write_json(root, report, manifest, report_fp)
            except Exception:
                pass
        raise SafetyError(str(exc), list(dict.fromkeys(changed))) from exc


def _move(root, base, row, changed, inspected):
    source, target = base + '/' + row['source'], base + '/' + row['destination']
    if observe(root, source) != row['artifact']:
        raise SafetyError('Migration source changed: ' + source)
    for relative, expected in inspected.items():
        if relative == row['source'] or relative.startswith(row['source'] + '/'):
            if fingerprint(checked_path(root, base + '/' + relative, allow_missing=False)) != expected:
                raise SafetyError('Migration source fingerprint changed: ' + relative)
    mkdirs(root, PurePosixPath(target).parent.as_posix(), changed)
    destination = checked_path(root, target)
    if destination.exists():
        raise SafetyError('Migration destination appeared: ' + target)
    from .activities import rename_exclusive
    rename_exclusive(checked_path(root, source, allow_missing=False), destination)
    changed.extend([source, target])
    if observe(root, target) != row['artifact']:
        raise SafetyError('Migration move readback differs: ' + target)
