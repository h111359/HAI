"""Allocate Activity-local working folders; the host owns actual AI-agent dispatch."""
import re
import uuid
from pathlib import PurePosixPath
from activity_layout import artifact, invocation_path

from .storage import SafetyError, checked_path, fingerprint, read_json, write_json

ROLE = re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z')


def prepare(root, base, activity_id, request, stamp):
    role = request.get('role')
    if not isinstance(role, str) or len(role) > 64 or not ROLE.fullmatch(role):
        raise ValueError('role must be a lower-case role name of at most 64 characters')
    invocation_id = str(uuid.uuid4())
    relative = invocation_path(root, base, role, invocation_id)
    suffix = relative[len(base) + 1:]
    parents = []
    parent = PurePosixPath(relative).parent
    while parent.as_posix() != base:
        parents.append(parent.as_posix()); parent = parent.parent
    for parent in reversed(parents):
        path = checked_path(root, parent)
        if path.exists() and not path.is_dir():
            raise SafetyError('Invocation parent must be a directory: ' + parent)
    if checked_path(root, relative).exists():
        raise SafetyError('Invocation allocation collision; existing material was preserved')
    metadata = {
        'invocation_format_version': 2, 'activity_id': activity_id,
        'invocation_id': invocation_id, 'role': role, 'created_at': stamp,
        'provenance': {key: request['provenance'][key] for key in ('source', 'reason')},
    }
    return {'allocated': False, 'activity_id': activity_id,
            'invocation_id': invocation_id, 'role': role,
            'path': relative, 'activity_relative_path': suffix,
            'metadata_path': relative + '/invocation.json', 'metadata': metadata}


def allocate(root, base, result, expected_state):
    """Called under the runtime lock. Preserve and report all partial creations."""
    changed = []
    try:
        state_path = artifact(root, base, 'state.json')
        if fingerprint(checked_path(root, state_path, allow_missing=False)) != expected_state:
            raise SafetyError('Activity changed before invocation allocation')
        parents = []
        parent = PurePosixPath(result['path'])
        while parent.as_posix() != base:
            parents.append(parent.as_posix()); parent = parent.parent
        for relative in reversed(parents):
            path = checked_path(root, relative)
            if relative == result['path'] or not path.exists():
                path.mkdir()  # Exclusive: never overlay, retry or reuse an invocation.
                changed.append(relative)
            elif not path.is_dir():
                raise SafetyError('Invocation parent must be a directory: ' + relative)
        directory = checked_path(root, result['path'], allow_missing=False)
        identity = (directory.stat().st_dev, directory.stat().st_ino)
        write_json(root, result['metadata_path'], result['metadata'])
        changed.append(result['metadata_path'])
        if fingerprint(checked_path(root, state_path, allow_missing=False)) != expected_state:
            raise SafetyError('Activity changed during invocation allocation')
        directory = checked_path(root, result['path'], allow_missing=False)
        if not directory.is_dir() or (directory.stat().st_dev, directory.stat().st_ino) != identity:
            raise SafetyError('Invocation directory changed before readback')
        if read_json(checked_path(root, result['metadata_path'], allow_missing=False)) != result['metadata']:
            raise SafetyError('Invocation metadata readback mismatch')
        return {**result, 'allocated': True}, changed
    except (SafetyError, OSError, UnicodeError) as exc:
        changed.extend(path for path in getattr(exc, 'changed_files', []) if path not in changed)
        raise SafetyError(str(exc), changed) from exc
