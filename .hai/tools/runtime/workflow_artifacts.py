"""Format-independent, bounded workflow artifact snapshots and fingerprints."""
import hashlib
import os
import stat
from pathlib import Path, PurePosixPath

from .storage import SafetyError, checked_path, fingerprint, write_bytes


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def mkdirs(root, relative, changed):
    current = Path(root)
    for part in relative.split('/'):
        current /= part
        rel = current.relative_to(root).as_posix()
        checked_path(root, rel)
        if not current.exists():
            current.mkdir()
            changed.append(rel)
        elif not current.is_dir():
            raise SafetyError('Expected workflow directory: ' + rel)


def observe(root, relative):
    """Return byte/manifest evidence, rejecting aliases and unstable directory reads."""
    path = checked_path(root, relative, allow_missing=False)
    info = path.lstat()
    if stat.S_ISREG(info.st_mode):
        before = fingerprint(path)
        raw = path.read_bytes()
        if fingerprint(checked_path(root, relative, allow_missing=False)) != before:
            raise SafetyError('Workflow artifact changed while reading: ' + relative)
        return {'kind': 'file', 'sha256': digest(raw), 'bytes': len(raw)}
    if not stat.S_ISDIR(info.st_mode):
        raise SafetyError('Workflow artifacts must be files or directories: ' + relative)
    def manifest():
        rows = []
        for directory, dirs, files in os.walk(path, followlinks=False):
            for name in sorted(dirs + files):
                child = Path(directory) / name
                rel = child.relative_to(root).as_posix()
                checked_path(root, rel, allow_missing=False)
                mode = child.lstat().st_mode
                suffix = child.relative_to(path).as_posix()
                if stat.S_ISDIR(mode):
                    rows.append({'path': suffix, 'kind': 'directory'})
                elif stat.S_ISREG(mode):
                    before = fingerprint(child)
                    raw = child.read_bytes()
                    if fingerprint(child) != before:
                        raise SafetyError('Directory artifact changed while reading')
                    rows.append({'path': suffix, 'kind': 'file', 'sha256': digest(raw), 'bytes': len(raw)})
                else:
                    raise SafetyError('Unsupported workflow artifact entry: ' + rel)
        return sorted(rows, key=lambda r: r['path'])
    import json
    first = manifest()
    if manifest() != first:
        raise SafetyError('Workflow directory artifact changed while reading: ' + relative)
    return {'kind': 'directory', 'sha256': digest(json.dumps(first, sort_keys=True, separators=(',', ':')).encode()), 'manifest': first}


def copy_snapshot(root, source, destination, changed):
    before = observe(root, source)
    src = checked_path(root, source, allow_missing=False)
    if before['kind'] == 'file':
        mkdirs(root, PurePosixPath(destination).parent.as_posix(), changed)
        write_bytes(root, destination, src.read_bytes())
        changed.append(destination)
    else:
        mkdirs(root, destination, changed)
        for row in before['manifest']:
            target = destination + '/' + row['path']
            if row['kind'] == 'directory':
                mkdirs(root, target, changed)
            else:
                mkdirs(root, PurePosixPath(target).parent.as_posix(), changed)
                raw = checked_path(root, source + '/' + row['path'], allow_missing=False).read_bytes()
                write_bytes(root, target, raw)
                changed.append(target)
    if observe(root, source) != before or observe(root, destination) != before:
        raise SafetyError('Workflow input changed during snapshot creation', changed)
    return before
