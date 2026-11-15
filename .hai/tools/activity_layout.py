"""One Activity path contract shared by discovery, runtime and host tools."""
from runtime.storage import SafetyError, checked_path, read_json

SYSTEM_FILES = {'state.json', 'log.md', 'chat.jsonl', 'usage.md', 'usage.json'}
BUCKETS = {'results', 'evidence', 'history', 'work', 'system', 'chronicles', 'workflow-runs'}


def version(root, base):
    legacy = checked_path(root, base + '/state.json')
    current = checked_path(root, base + '/system/state.json')
    if legacy.exists() and current.exists():
        raise SafetyError('Mixed Activity layouts require explicit reconciliation')
    if current.exists():
        state = read_json(current)
        marker = state.get('activity_layout_version') if isinstance(state, dict) else None
        if type(marker) is not int or marker != 2:
            raise SafetyError('Unsupported Activity layout version in system/state.json')
        return 2
    if legacy.exists():
        state = read_json(legacy)
        marker = state.get('activity_layout_version', 1) if isinstance(state, dict) else None
        if type(marker) is not int or marker != 1:
            raise SafetyError('Unsupported Activity layout version in legacy state.json')
    return 1


def artifact(root, base, name):
    if version(root, base) == 1:
        return base + '/' + name
    if name in ('input.md', 'outcome.md'):
        raise SafetyError(name + ' has no layout-2 alias; use typed chat or README.md')
    if name in SYSTEM_FILES:
        return base + '/system/' + name
    if name.startswith('chronicles/') and not name.endswith('.md'):
        return base + '/system/' + name
    # Historical transcript copies remain with recording recovery metadata.
    if name.startswith('chronicles/history/'):
        return base + '/system/' + name
    if name in {'definition.md', 'analysis.md', 'decisions.md', 'plan.md', 'requirements.md'}:
        return base + '/results/' + name
    return base + '/' + name


def invocation_root(root, base, agent=None):
    if version(root, base) == 1:
        return base + '/files/agent-invocations'
    if not agent:
        return base + '/work/agents'
    # Callers validate the role identifier before selecting its owned directory.
    checked_path(root, base + '/work/agents/' + agent)
    return base + '/work/agents/' + agent


def invocation_path(root, base, agent, invocation_id):
    return invocation_root(root, base, agent) + '/' + invocation_id


def revision_root(root, base, document):
    return base + ('/history/' if version(root, base) == 2 else '/files/revisions/') + document
