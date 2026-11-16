"""Narrow, deterministic transformations used only by explicit role migration."""
import json
import re

OLD_MANAGER = 'agent-definition-manager'
NEW_MANAGER = 'role-definition-manager'
PATHS = (
    ('hai_agents_library/agents', 'hai_roles_library/roles'),
    ('hai_agents_library', 'hai_roles_library'),
    ('.hai_env/config/agents', '.hai_env/config/roles'),
    ('.hai_env/agents', '.hai_env/roles'),
    ('.hai/tools/agents', '.hai/tools/roles'),
    ('../agents/agent_tools', '../roles/role_tools'),
    ('agent_tools.py', 'role_tools.py'),
    ('agent-configuration_conv.md', 'role-configuration_conv.md'),
    ('agent-configuration.md', 'role-configuration.md'),
    ('concepts/agent.md', 'concepts/role.md'),
    ('agent_conv.md', 'role_conv.md'),
    (OLD_MANAGER, NEW_MANAGER),
)


def identity(name):
    return NEW_MANAGER if name == OLD_MANAGER else name


def references(text, *, role_entry=False, package_names=(), self_entry='SKILL.md'):
    # Native AI-agent folders/instructions and genuine skills retain their names.
    for old, new in PATHS:
        text = text.replace(old, new)
    text = text.replace('Agent-definition-manager', 'Role-definition-manager')
    for old, new in (('New agents default to workspace origin', 'New roles default to workspace origin'),
                     ('[Agent convention]', '[Role convention]'), ('[Agent concept]', '[Role concept]'),
                     ('[Agent tools]', '[Role tools]'), ('SKILL Rules', 'ROLE Rules'), ('SKILL rules', 'ROLE rules'),
                     ('SKILL metadata', 'ROLE metadata'), ('agent-format', 'role-format')):
        text = text.replace(old, new)
    if 'Role-definition-manager' in text:
        for old, new in (('for every agent', 'for every role'), ('when the agent has no', 'when the role has no'), ('as an agent', 'as a role'), ('Distinct agent names', 'Distinct role names'), ('immediate agent-folder', 'immediate role-folder'), ('another agent', 'another role'), ('registers the agent', 'registers the role'), ('six SKILL headings', 'six ROLE.md headings'), ('six ordered SKILL headings', 'six ordered ROLE.md headings'), ('live in SKILL', 'live in ROLE.md'), ('shared agent convention', 'shared role convention'), ('a new agent', 'a new role'), ("applying host coordinator's exception when relevant", 'without declaring a built-in coordinator role')):
            text = text.replace(old, new)
    if role_entry:
        # Package-local entries and canonical HAI references, never skills/x/SKILL.md.
        def entry_link(match):
            label, target = match[1], match[2]
            path, separator, fragment = target.partition('#')
            canonical_entry = re.fullmatch(r'(?:\.hai_env/roles|hai_roles_library/roles)/[^/]+/SKILL\.md', path)
            role_target = (path == self_entry or canonical_entry or any(re.fullmatch(r'(?:\.\./)+' + re.escape(name) + r'/SKILL\.md', path) for name in package_names))
            if role_target and path.endswith('SKILL.md'):
                return '[' + label.replace('SKILL.md', 'ROLE.md') + '](' + path[:-8] + 'ROLE.md' + separator + fragment + ')'
            return match[0]
        text = re.sub(r'\[([^]\n]+)\]\(([^()\n]+)\)', entry_link, text)
        text = re.sub(r'(?<![\w/.[-])SKILL\.md(?![\w.-]|\]\()', 'ROLE.md', text)
        text = re.sub(r'((?:\.hai_env/roles|hai_roles_library/roles)/[^/\s)]+/)SKILL\.md', r'\1ROLE.md', text)
        for name in package_names:
            text = re.sub(r'((?:\.\./)+' + re.escape(name) + r'/)SKILL\.md', r'\1ROLE.md', text)
        text = text.replace('SKILL index', 'ROLE index')
    phrases = ('agent definition', 'agent package', 'agent configuration',
               'agent format', 'agent source library', 'agent catalogue',
               'agent-owned', 'workspace agent', 'installed agent',
               'registered agent', 'agent registration')
    for phrase in phrases:
        for old in (phrase, phrase.capitalize(), phrase.title()):
            text = text.replace(old, old.replace('Agent', 'Role').replace('agent', 'role'))
    return text


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate contract key: ' + key)
        result[key] = value
    return result


def transform(relative, raw, *, package_names=()):
    if relative.startswith('skills/') or '/skills/' in relative or (relative.endswith('/SKILL.md')):
        return raw
    if relative == 'configuration/contract.json':
        document = json.loads(raw, object_pairs_hook=_pairs,
                              parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Invalid JSON constant: ' + x)))
        if (not isinstance(document, dict) or type(document.get('contract_format_version')) is not int
                or document['contract_format_version'] not in (1, 2) or 'agent' not in document or 'role' in document):
            raise ValueError('Expected an unambiguous legacy role configuration contract')
        document['role'] = identity(document.pop('agent'))
        document['contract_format_version'] = 3
        return (json.dumps(document, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    # Arbitrary JSON/YAML/TOML files are data, not prose or HAI contracts.
    if relative.endswith(('.md', '.py')):
        text = references(raw.decode('utf-8'), role_entry=True, package_names=package_names, self_entry='../' * relative.count('/') + 'SKILL.md')
        if relative.endswith('.py'):
            text = text.replace('from agent_tools import ', 'from role_tools import ')
            text = text.replace("('hai_roles_library','agents')", "('hai_roles_library','roles')").replace("('.hai_env','agents')", "('.hai_env','roles')")
            text = text.replace(".get('agent_configurations',", ".get('role_configurations',")
            text = re.sub(r"(environment\.handle\('configuration/[^']+',\s*[^,]+,\s*\{)'agent'(?=\s*:)", r"\1'role'", text)
            # Embedded HAI contract fixtures only; ordinary business "agent" keys stay.
            text = re.sub(r"(['\"]contract_format_version['\"]\s*:\s*)[12](\s*,\s*)(['\"])agent\3(\s*:)", r"\g<1>3\2\3role\3\4", text)
        return text.encode('utf-8')
    return raw


def workflow(raw):
    text = raw.decode('utf-8')
    if len(re.findall(r'^workflow_format: 1\r?$', text, re.M)) != 1:
        raise ValueError('Expected workflow_format 1 for explicit migration')
    if len(re.findall(r'^revision: [0-9]+\r?$', text, re.M)) != 1:
        raise ValueError('Expected one workflow revision')
    text = re.sub(r'(?m)^workflow_format: 1(\r?)$', r'workflow_format: 2\1', text)
    text = re.sub(r'(?m)^#### Agent(\r?)$', r'#### Role\1', text)
    text = re.sub(r'(?m)^revision: ([0-9]+)(\r?)$', lambda m: 'revision: ' + str(int(m[1]) + 1) + m[2], text)
    return references(text).encode('utf-8')
