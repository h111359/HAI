"""Explicit cleanup of declared disposable work after host reconciliation."""
import shutil
from pathlib import PurePosixPath
from activity_layout import version
from .storage import SafetyError, checked_path
from .workflow_artifacts import observe


def cleanup(root, base, request, apply):
    if version(root, base) != 2:
        raise SafetyError('Migrate the Activity before using layout-2 work cleanup')
    if request.get('writers_ended') is not True or request.get('evidence_retained') is not True:
        raise SafetyError('Cleanup requires verified ended writers and retained meaningful evidence')
    paths = request.get('paths')
    if not isinstance(paths, list) or not paths or any(not isinstance(p, str) for p in paths):
        raise ValueError('Cleanup paths must be a nonempty list of Activity-relative work paths')
    selected = []
    for relative in paths:
        parts = PurePosixPath(relative).parts
        if len(parts) < 2 or parts[0] != 'work' or parts[1] not in ('coordinator', 'test-work', 'agents'):
            raise SafetyError('Cleanup can target only declared disposable work')
        path = checked_path(root, base + '/' + relative, allow_missing=False)
        if not path.resolve().is_relative_to(root.resolve()):
            raise SafetyError('Cleanup target escapes workspace')
        observation = observe(root, base + '/' + relative)
        names = [path.name] if observation['kind'] == 'file' else [row['path'].split('/')[-1] for row in observation['manifest']]
        if any(name.casefold() == 'invocation.json' for name in names):
            raise SafetyError('Invocation allocation manifests must be retained')
        key = relative.casefold().rstrip('/')
        if any(key == old or key.startswith(old + '/') or old.startswith(key + '/') for old, _, _ in selected):
            raise ValueError('Cleanup paths overlap')
        selected.append((key, relative, observation))
    changed = []
    try:
        if apply:
            for _, relative, expected in selected:
                if observe(root, base + '/' + relative) != expected:
                    raise SafetyError('Disposable work changed after inspection')
                path = checked_path(root, base + '/' + relative, allow_missing=False)
                changed.append(base + '/' + relative)
                if path.is_dir(): shutil.rmtree(path)
                else: path.unlink()
    except (OSError, SafetyError) as exc:
        raise SafetyError(str(exc), changed + getattr(exc, 'changed_files', [])) from exc
    return {'paths': paths, 'writers_ended': True, 'evidence_retained': True}, changed
