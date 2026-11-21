"""Read-only readiness gate for the explicit HAI role naming migration."""
from pathlib import Path
from runtime.storage import SafetyError, checked_path, read_json

MARKER = ".hai_env/config/role-migration.json"
LEGACY_ROOTS = (".hai_env/agents", ".hai_env/config/agents", ".hai/agents")
ROLE_ROOTS = (".hai_env/roles", ".hai_env/config/roles")


def status(workspace):
    """Report naming readiness without changing core environment validity."""
    root = Path(workspace).resolve(strict=True)
    issues, legacy, canonical = [], [], []
    marker_status = None
    try:
        for relative in LEGACY_ROOTS:
            path = checked_path(root, relative)
            if path.exists():
                if not path.is_dir():
                    raise SafetyError(f"Role migration root must be a directory: {relative}")
                legacy.append(relative)
        for relative in ROLE_ROOTS:
            path = checked_path(root, relative)
            if path.exists():
                if not path.is_dir():
                    raise SafetyError(f"Role root must be a directory: {relative}")
                canonical.append(relative)
        capability = checked_path(root, '.hai_env/config/capability-migration-v1.json')
        if capability.exists():
            cap = read_json(capability)
            if not isinstance(cap,dict) or cap.get('migration_format_version')!=1 or cap.get('status')!='complete':
                raise SafetyError('Incomplete capability migration; inspect retained marker and backups before explicit recovery')
        marker = checked_path(root, MARKER)
        if marker.exists():
            data = read_json(marker)
            marker_status = data.get("status") if isinstance(data, dict) else None
            if marker_status not in ("prepared", "partial", "completed"):
                raise SafetyError("Role migration marker has an invalid status")
    except (SafetyError, OSError, RuntimeError) as exc:
        issues.append({"code": "role_migration", "message": str(exc)})
        return {"status": "partial", "legacy_paths": legacy, "issues": issues}
    if marker_status in ("prepared", "partial"):
        current = "partial"
        message = "Incomplete role migration; inspect its marker and retained recovery files before explicit recovery"
    elif legacy:
        current = "partial" if canonical or marker_status == "completed" else "migration_required"
        message = "Legacy or mixed agent package names remain; explicitly run roles migrate before using roles"
    else:
        return {"status": "ready", "legacy_paths": [], "issues": []}
    issues.append({"code": "role_migration", "paths": legacy, "message": message})
    return {"status": current, "legacy_paths": legacy, "issues": issues}


def require_ready(workspace):
    current = status(workspace)
    if current["status"] != "ready":
        raise SafetyError("; ".join(issue["message"] for issue in current["issues"]))
