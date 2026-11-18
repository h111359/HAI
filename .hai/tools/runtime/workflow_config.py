"""Explicit workflow installation and environment-owned destination settings."""
from pathlib import Path
import uuid
from .storage import SafetyError, checked_path, fingerprint, read_json, write_bytes, write_json, lock
from .workflow_artifacts import digest, mkdirs
from .activities import envelope, provenance, store_path


def config_path(name):
    return '.hai_env/config/workflows/' + name + '.json'


def canonical_spelling(root, relative):
    cursor = Path(root)
    for part in relative.split('/'):
        if cursor.is_dir():
            aliases = [p.name for p in cursor.iterdir() if p.name.casefold() == part.casefold()]
            if aliases and aliases != [part]:
                raise SafetyError('Workflow path has a case alias: ' + relative)
        cursor /= part


def validate_locations(root, parsed, values):
    if not isinstance(values, dict) or set(values) != set(parsed['locations']):
        raise SafetyError('Required workflow locations missing or unknown; ask the human for all declared bases')
    protected = ('.hai', '.hai_env/config', '.hai_env/roles', '.hai_env/skills', '.hai_env/workflows', '.hai_env/workflow-runs', '.hai_env/.runtime.lock', '.git', '.aws', '.codex', '.agents', 'roles', 'skills', 'workflows', 'hai_roles_library', 'hai_agents_library', store_path(root))
    prior = []
    literals = {}
    for name, value in values.items():
        path = checked_path(root, value)
        folded = value.casefold()
        if any(folded == p.casefold() or folded.startswith(p.casefold() + '/') or p.casefold().startswith(folded + '/') for p in protected):
            raise SafetyError('Workflow output base overlaps protected/source metadata: ' + value)
        if path.exists() and not path.is_dir():
            raise SafetyError('Workflow output base is not a directory: ' + value)
        canonical_spelling(root, value)
        if folded in literals and literals[folded] != value:
            raise SafetyError('Workflow bases use case aliases')
        literals[folded] = value
        for other in prior:
            if folded != other and (folded.startswith(other + '/') or other.startswith(folded + '/')):
                raise SafetyError('Nested workflow bases are ambiguous; use one identical shared base or distinct bases')
        prior.append(folded)
    return dict(values)


def load(root, parsed):
    canonical_spelling(root, config_path(parsed['name']))
    path = checked_path(root, config_path(parsed['name']), allow_missing=False)
    before = fingerprint(path)
    saved = read_json(path)
    if fingerprint(path) != before:
        raise SafetyError('Workflow configuration changed while reading')
    if (not isinstance(saved, dict) or set(saved) != {'workflow_configuration_format', 'name', 'definition_sha256', 'locations'}
            or type(saved['workflow_configuration_format']) is not int or saved['workflow_configuration_format'] != 1
            or saved['name'] != parsed['name'] or saved['definition_sha256'] != parsed['sha256']):
        raise SafetyError('Workflow configuration is incompatible or installation is partial; inspect without automatic repair')
    validate_locations(root, parsed, saved['locations'])
    return saved


def install(operation, root, request, apply):
    from .workflows import definition
    changed = []
    try:
        if set(request) - {'definition', 'locations', 'expected_installed_sha256', 'provenance'}:
            raise ValueError('Unknown workflow installation fields')
        parsed, raw = definition(root, request.get('definition'), registered=False)
        if parsed['workflow_format'] != 3:
            raise SafetyError('Configurable installation requires workflow_format 3; historical formats require explicit authoring/migration')
        destination = '.hai_env/workflows/' + parsed['name'] + '.md'
        canonical_spelling(root, destination)
        canonical_spelling(root, config_path(parsed['name']))
        installed = checked_path(root, destination)
        existing_fp = fingerprint(installed)
        existing = installed.read_bytes() if existing_fp is not None else None
        if fingerprint(installed) != existing_fp:
            raise SafetyError('Installed workflow changed while reading')
        saved_path = checked_path(root, config_path(parsed['name']))
        saved_fp = fingerprint(saved_path)
        saved_raw = saved_path.read_bytes() if saved_fp is not None else None
        old_config = read_json(saved_path) if saved_fp is not None else None
        if fingerprint(saved_path) != saved_fp:
            raise SafetyError('Workflow settings changed while reading')
        if (existing is None) != (old_config is None):
            raise SafetyError('Partial workflow installation requires reconciliation; preserve existing bytes')
        values = request.get('locations')
        if existing is not None:
            from workflows.definition import parse_definition
            old_parsed = parse_definition(existing, source=destination)
            if old_parsed['workflow_format'] != 3:
                raise SafetyError('Existing historical workflow cannot be silently converted')
            load(root, old_parsed)
            if set(old_parsed['locations']) != set(parsed['locations']):
                raise SafetyError('Workflow location contract changed; explicit reviewed migration required; chosen settings preserved')
            if values is None:
                values = old_config['locations']
            elif values != old_config['locations']:
                raise SafetyError('Ordinary definition update preserves chosen locations; use an explicit reviewed configuration change')
            if existing != raw and request.get('expected_installed_sha256') != digest(existing):
                raise SafetyError('Definition update requires expected_installed_sha256 of inspected installed bytes')
        questions = [{'name': key, 'purpose': row['purpose'], 'contents': row['contents']} for key, row in parsed['locations'].items()]
        if values is None:
            if apply:
                raise SafetyError('Human-chosen workspace-relative workflow locations are required before apply')
            return envelope(operation, 'planned', {'definition': parsed['name'], 'questions': questions, 'ready': False,
                'missing_locations': list(parsed['locations']), 'starts_run': False})
        values = validate_locations(root, parsed, values)
        saved = {'workflow_configuration_format': 1, 'name': parsed['name'], 'definition_sha256': parsed['sha256'], 'locations': values}
        result = {'definition': destination, 'configuration': config_path(parsed['name']), 'locations': values,
                  'questions': questions, 'ready': True, 'starts_run': False}
        if not apply:
            return envelope(operation, 'planned', result)
        from .startup import require_mutation_context
        require_mutation_context(root)
        provenance(request)
        if existing == raw and old_config == saved:
            return envelope(operation, result={**result, 'reused': True})
        with lock(root):
            if fingerprint(installed) != existing_fp or fingerprint(saved_path) != saved_fp:
                raise SafetyError('Workflow installation inputs changed before apply')
            if existing is not None:
                backup = '.hai_env/config/workflows/history/' + parsed['name'] + '/' + str(uuid.uuid4())
                mkdirs(root, backup, changed)
                write_bytes(root, backup + '/definition.md', existing); changed.append(backup + '/definition.md')
                write_bytes(root, backup + '/configuration.json', saved_raw); changed.append(backup + '/configuration.json')
            mkdirs(root, '.hai_env/workflows', changed)
            mkdirs(root, '.hai_env/config/workflows', changed)
            write_bytes(root, destination, raw, existing_fp); changed.append(destination)
            write_json(root, config_path(parsed['name']), saved, saved_fp); changed.append(config_path(parsed['name']))
            load(root, parsed)
        return envelope(operation, result=result, changed=changed)
    except (SafetyError, OSError, ValueError, TypeError, KeyError) as exc:
        changed.extend(p for p in getattr(exc, 'changed_files', []) if p not in changed)
        return envelope(operation, 'partial' if changed else 'blocked', changed=changed, issues=[str(exc)])


def outputs(root, state, step, execution):
    # Validate the pinned contract on every preparation; current installation changes do not rewrite a run.
    parsed = {'locations': state['configuration']['locations']}
    validate_locations(root, parsed, state['configuration']['locations'])
    result = {}
    for name, row in step['outputs'].items():
        key, pattern = row['location'].split(':', 1)[1].split('/', 1)
        target = state['configuration']['locations'][key] + '/' + state['run_id'] + '/' + pattern.replace('{execution}', f'{execution:03}')
        if checked_path(root, target).exists():
            raise SafetyError('New workflow output already exists; preserve conflict: ' + target)
        if target.casefold() in {p['path'].casefold() for p in result.values()}:
            raise SafetyError('Shared workflow bases produce colliding output filenames')
        result[name] = {**row, 'path': target}
    return result
