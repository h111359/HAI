"""Read-only native skill inspection and installed-only dependency resolution.

Skills are free-form methods. They do not carry role/model execution policy.
The safe YAML reader reports unsupported syntax rather than silently misreading it.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'roles'))
import role_tools as roles
from runtime.storage import checked_path, SafetyError


def read_definition(path, workspace, *, metadata_only=False):
    path = Path(path)
    checked_path(workspace, path.relative_to(workspace).as_posix(), allow_missing=False)
    if path.name != 'SKILL.md' or not path.is_file():
        raise roles.Invalid('A skill requires a readable SKILL.md')
    if metadata_only:
        lines = []
        with path.open('rb') as stream:
            first = stream.readline(9)
            if first.decode('utf-8-sig').rstrip('\r\n') != '---':
                raise roles.Invalid('Skill requires YAML frontmatter')
            lines.append('---')
            size = len(first)
            while True:
                raw = stream.readline(65536 - size + 1)
                size += len(raw)
                if size > 65536:
                    raise roles.Invalid('Discovery frontmatter exceeds 64 KiB')
                if not raw:
                    break
                line = raw.decode('utf-8').rstrip('\r\n')
                lines.append(line)
                if line == '---':
                    break
    else:
        lines = path.read_text(encoding='utf-8-sig').split('\n')
    if not lines or lines[0] != '---': raise roles.Invalid('Skill requires YAML frontmatter')
    try: end = lines.index('---', 1)
    except ValueError as exc: raise roles.Invalid('Unterminated skill frontmatter') from exc
    fields = roles.parse_frontmatter('\n'.join(lines[1:end]) + '\n')
    if set(fields) - {'name','description','license','compatibility','metadata','allowed-tools'}:
        raise roles.Invalid('Skill uses unsupported frontmatter fields')
    name = fields.get('name'); description = fields.get('description')
    if not isinstance(name,str) or len(name)>64 or not roles.NAMES.fullmatch(name) or name != path.parent.name:
        raise roles.Invalid('Skill name must match its canonical folder')
    if not isinstance(description,str) or not description.strip() or len(description)>1024:
        raise roles.Invalid('Skill requires a description of at most 1024 characters')
    for key in ('license','compatibility','allowed-tools'):
        if key in fields and (not isinstance(fields[key],str) or not fields[key].strip()):
            raise roles.Invalid(key + ' must be a nonblank string')
    if len(fields.get('compatibility',''))>500: raise roles.Invalid('Compatibility exceeds 500 characters')
    metadata = fields.get('metadata',{})
    if not isinstance(metadata,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in metadata.items()):
        raise roles.Invalid('Skill metadata keys and values must be strings')
    if not metadata_only and not '\n'.join(lines[end+1:]).strip(): raise roles.Invalid('Skill instructions are empty')
    return fields


def validate(workspace, definition):
    root=Path(workspace).resolve(strict=True)
    try:
        path=checked_path(root,definition,allow_missing=False)
        fields=read_definition(path,root)
        return {'ok':True,'definition':definition,'skill':fields['name'],'description':fields['description'],'issues':[]}
    except (roles.Invalid, roles.UnsupportedYAML, SafetyError, OSError, UnicodeError, ValueError) as exc:
        return {'ok':False,'definition':definition,'issues':[{'code':'skill','message':str(exc)}]}


def inventory(workspace):
    """Read installed entry metadata only; isolate optional discovery failures."""
    root = Path(workspace).resolve(strict=True)
    entries, issues = [], []
    try:
        base = checked_path(root, '.hai_env/skills')
        children = sorted(base.iterdir()) if base.exists() else []
        for child in children:
            if child.name.startswith('.'):
                continue
            definition = f'.hai_env/skills/{child.name}/SKILL.md'
            try:
                path = checked_path(root, definition, allow_missing=False)
                fields = read_definition(path, root, metadata_only=True)
                entries.append({'ok': True, 'skill': fields['name'],
                                'description': fields['description'],
                                'definition': definition, 'issues': []})
            except (roles.Invalid, roles.UnsupportedYAML, SafetyError, OSError, UnicodeError, ValueError) as exc:
                issue = {'code': 'skill', 'path': definition, 'message': str(exc)}
                issues.append(issue)
                entries.append({'ok': False, 'definition': definition, 'issues': [issue]})
    except (SafetyError, OSError, ValueError) as exc:
        issues.append({'code': 'skills', 'path': '.hai_env/skills', 'message': str(exc)})
    return {'status': 'partial' if issues and entries else 'unavailable' if issues else 'available',
            'skills': entries, 'issues': issues}


def names(fields):
    value=fields.get('metadata',{}).get('hai-skills','')
    if not value: return []
    result=[x.strip() for x in value.split(',')]
    if any(not roles.NAMES.fullmatch(x) or len(x)>64 for x in result) or len(result)!=len(set(result)):
        raise roles.Invalid('hai-skills must be distinct comma-separated canonical skill names')
    return result


def dependencies(workspace, role_path, fields):
    root=Path(workspace).resolve(strict=True); path=Path(role_path)
    base='.hai_env/skills'  # Source inspection never infers a workspace library.
    result=[]
    for name in names(fields):
        definition=f'{base}/{name}/SKILL.md'; checked=validate(root,definition)
        if not checked['ok']: raise roles.Invalid('Unavailable required skill '+name+': '+str(checked['issues']))
        result.append({'name':name,'definition':definition})
    return result


def resolve(workspace,name):
    root=Path(workspace).resolve(strict=True)
    from role_state import require_ready
    require_ready(root)
    if not isinstance(name,str) or not roles.NAMES.fullmatch(name) or len(name)>64:
        raise roles.Invalid('A canonical skill name is required')
    definition=f'.hai_env/skills/{name}/SKILL.md'; checked=validate(root,definition)
    if not checked['ok']: return checked
    fields=read_definition(root/definition,root)
    result={**checked,'authority':'unchanged; skill selection grants no permissions'}
    owner=fields.get('metadata',{}).get('hai-settings-owner')
    if owner:
        if not roles.NAMES.fullmatch(owner): raise roles.Invalid('Invalid settings owner')
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'configuration'))
        import configuration_tools as config
        contract_path=checked_path(root,f'.hai_env/roles/{owner}/configuration/contract.json',allow_missing=False)
        contract=config.load_contract(contract_path,owner)
        configuration=config.read_configuration(root,owner,contract)
        result['configuration_owner']=owner; result['configuration']=configuration
        if configuration['status'] not in ('configured','defaulted'):
            result['ok']=False; result['issues']=configuration['issues']
    return result
