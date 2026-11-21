"""Explicit local skill installation and direct installed capability lookup."""
from pathlib import Path
import sys, shutil, uuid
from .storage import SafetyError, checked_path, fingerprint, lock
from .activities import envelope, provenance, rename_exclusive, rename_preflight
from .packages import snapshot
from . import package_content
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills'))
import skill_tools as skills


def handle(operation,workspace,request,apply):
    root=Path(workspace).resolve(strict=True); changed=[]
    if operation=='migrate':
        from .capability_migration import handle as migrate
        return migrate(root,request,apply)
    try:
        allowed={'validate':{'definition'},'list':set(),'resolve':{'name'},'install':{'source','name','replace','reviewed_differences','source_mappings','provenance'}}
        if operation not in allowed or not isinstance(request,dict) or set(request)-allowed[operation]: raise ValueError('Unsupported skill operation or fields')
        if operation!='validate':
            from role_state import require_ready
            require_ready(root)
        if apply and operation in ('validate','resolve','list'): raise ValueError('Skill inspection is read-only')
        if operation=='validate':
            result=skills.validate(root,request.get('definition')); return envelope(operation,'ok' if result['ok'] else 'blocked',result,issues=result['issues'])
        if operation=='resolve':
            result=skills.resolve(root,request.get('name')); return envelope(operation,'ok' if result['ok'] else 'blocked',result,issues=result['issues'])
        if operation=='list':
            if apply: raise ValueError('List is read-only')
            result=skills.inventory(root)
            return envelope(operation,'ok' if not result['issues'] else 'blocked',result,issues=result['issues'])
        provenance(request)
        name=request.get('name'); source=request.get('source')
        if not isinstance(name,str) or not skills.roles.NAMES.fullmatch(name) or len(name)>64: raise ValueError('Invalid skill name')
        src=checked_path(root,source,allow_missing=False); dest=f'.hai_env/skills/{name}'; target=checked_path(root,dest)
        if src.name!=name or src==target or src in target.parents or target in src.parents: raise SafetyError('Source identity or package separation is invalid')
        result=skills.validate(root,source+'/SKILL.md')
        if not result['ok']: raise SafetyError(str(result['issues']))
        before=snapshot(root,source,entry='SKILL.md'); previous=snapshot(root,dest,entry='SKILL.md') if target.exists() else None
        candidate,relocated,unresolved=package_content.prepare(root,source,dest,before,request.get('source_mappings'))
        candidate_hashes=package_content.hashes(candidate)
        differences=[k for k in sorted(set(candidate)|set(previous or {})) if k not in candidate_hashes or k not in (previous or {}) or candidate_hashes[k]!=(previous or {})[k][-1]]
        replace=request.get('replace',False)
        if type(replace) is not bool: raise ValueError('replace must be Boolean')
        if previous is not None and (not replace or request.get('reviewed_differences')!=differences): raise SafetyError('Replacement requires exact reviewed differences and explicit replace')
        result={'source':source,'destination':dest,'differences':differences,'relocated_files':relocated,'unresolved_references':unresolved,'execution_readiness':'not_checked'}
        if not apply: return envelope(operation,'planned',result)
        from .startup import require_mutation_context
        require_mutation_context(root)
        with lock(root):
            if snapshot(root,source,entry='SKILL.md')!=before or (snapshot(root,dest,entry='SKILL.md') if target.exists() else None)!=previous: raise SafetyError('Package changed since inspection')
            rename_preflight(); base=checked_path(root,'.hai_env/skills'); base.mkdir(exist_ok=True)
            stage=f'.hai_env/skills/.hai-stage-{uuid.uuid4().hex}'; container=checked_path(root,stage); container.mkdir(); changed.append(stage)
            staged=container/name; shutil.copytree(src,staged); changed.append(stage+'/'+name)
            if {k:v[-1] for k,v in snapshot(root,stage+'/'+name,entry='SKILL.md').items()}!={k:v[-1] for k,v in before.items()}: raise SafetyError('Staged skill differs from source')
            for filename,data in candidate.items():
                p=checked_path(root,stage+'/'+request['name']+'/'+filename,allow_missing=False)
                if p.read_bytes()!=data:p.write_bytes(data)
            if {k:v[-1] for k,v in snapshot(root,stage+'/'+request['name'],entry='SKILL.md').items()}!=candidate_hashes:raise SafetyError('Transformed stage differs from reviewed candidate')
            package_content.validate(root,dest,candidate)
            if snapshot(root,source,entry='SKILL.md')!=before or (snapshot(root,dest,entry='SKILL.md') if target.exists() else None)!=previous: raise SafetyError('Source or destination changed during staging')
            if previous is not None:
                backup=f'.hai_env/skills/.hai-backup-{uuid.uuid4().hex}'; rename_exclusive(target,checked_path(root,backup)); changed.append(backup); result['backup']=backup
            if target.exists(): raise SafetyError('Destination appeared before publication')
            rename_exclusive(staged,target); changed.append(dest)
        return envelope(operation,result=result,changed=changed)
    except (ValueError,TypeError,skills.roles.Invalid,skills.roles.UnsupportedYAML,SafetyError,OSError) as exc:
        changed.extend(x for x in getattr(exc,'changed_files',[]) if x not in changed)
        return envelope(operation,'partial' if changed else 'blocked',changed=changed,issues=[str(exc)])
