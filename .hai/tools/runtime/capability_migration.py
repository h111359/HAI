"""Explicit previewed role/skill migration; never merge or recover partial states."""
from pathlib import Path
import hashlib,json,re,shutil,uuid
from .storage import SafetyError,checked_path,write_json,lock,fingerprint,read_json,json_bytes
from .activities import envelope,provenance,store_path,discover,rename_exclusive
from .role_migration import _manifest,_workflow_states
from .workflow_artifacts import mkdirs
from . import packages
ROOTS=('roles','skills','.hai_env/roles','.hai_env/skills')
MARKER='.hai_env/config/capability-migration-v1.json'

def _plan(root,request):
    from .startup import require_mutation_context
    require_mutation_context(root)
    if checked_path(root,MARKER).exists(): raise SafetyError('Retained capability migration marker exists; inspect completion or recover partial state explicitly')
    location=store_path(root); context=discover(root,location)
    activity_id=request.get('activity_id')
    if context['status']!='current' or context['activity_id']!=activity_id: raise SafetyError('Migration requires the current Activity')
    base=context['path']; candidate=request.get('candidate_workspace')
    if not isinstance(candidate,str) or not candidate.startswith(base+'/work/'): raise SafetyError('Candidate workspace must be in the current Activity work area')
    candidate_root=checked_path(root,candidate,allow_missing=False)
    if not candidate_root.is_dir(): raise SafetyError('Candidate workspace must be a directory')
    selected=request.get('packages')
    if not isinstance(selected,list) or not selected or any(not isinstance(x,str) for x in selected) or len(selected)!=len(set(selected)): raise ValueError('Provide distinct package destinations')
    snapshots={}; sources={}
    for relative in selected:
        if not any(re.fullmatch(re.escape(prefix)+r'/[a-z][a-z0-9]*(?:-[a-z0-9]+)*',relative) for prefix in ROOTS): raise SafetyError('Destination outside exact role/skill package allowlist')
        destination=checked_path(root,relative); source=checked_path(root,candidate+'/'+relative,allow_missing=False)
        if source==destination or source in destination.parents or destination in source.parents: raise SafetyError('Candidate aliases destination')
        entry='ROLE.md' if '/roles/' in '/'+relative+'/' else 'SKILL.md'
        packages.snapshot(root,candidate+'/'+relative,entry=entry)
        sources[relative]=_manifest(root,candidate+'/'+relative); snapshots[relative]=_manifest(root,relative)
        if entry=='ROLE.md': result=packages.roles.validate(candidate_root,relative+'/'+entry)
        else:
            import skill_tools
            result=skill_tools.validate(candidate_root,relative+'/'+entry)
        if not result['ok']: raise SafetyError('Invalid candidate '+relative+': '+str(result['issues']))
    retire=request.get('retire_legacy_source',False)
    if type(retire) is not bool: raise ValueError('retire_legacy_source must be Boolean')
    if retire:
        expected={p.name for p in checked_path(root,'hai_roles_library/roles',allow_missing=False).iterdir() if p.is_dir()}
        if any('roles/'+name not in selected for name in expected): raise SafetyError('Every legacy role needs an explicit candidate before container retirement')
        snapshots['hai_roles_library']=_manifest(root,'hai_roles_library')
    if request.get('writers_ended') is not True: raise SafetyError('Declare other affected-package writers ended before migration')
    details={'activity_id':activity_id,'candidate_workspace':candidate,'packages':sorted(selected),'retire_legacy_source':retire,'destinations':snapshots,'candidates':sources,'settings':_manifest(root,'.hai_env/config/roles'),'workflow_states':_workflow_states(root,location),'backup_base':base+'/history/capability-migration-v1'}
    digest=hashlib.sha256(json.dumps(details,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return details,digest,base

def handle(workspace,request,apply):
    root=Path(workspace).resolve(strict=True); changed=[]
    try:
        allowed={'activity_id','candidate_workspace','packages','retire_legacy_source','writers_ended','expected_preview','provenance'}
        if not isinstance(request,dict) or set(request)-allowed: raise ValueError('Unknown migration fields')
        provenance(request)
        def run():
            plan,digest,base=_plan(root,request)
            result={'preview_sha256':digest,'plan':plan,'recovery':'Stop affected writers; preserve new/partial destinations separately. Explicitly restore each original directory from backup_base/originals to its recorded destination using no-replace moves; remove only reviewed newly-created destinations. Restore hai_roles_library from its original backup if retired. Keep marker and evidence until an owner reconciles state; never retry or merge automatically.'}
            if not apply: return envelope('migrate','planned',result)
            if request.get('expected_preview')!=digest: raise SafetyError('Preview absent or stale; inspect a new preview')
            backup=plan['backup_base']
            if checked_path(root,backup).exists(): raise SafetyError('Backup destination exists; inspect partial state instead of merging')
            stage=str(Path(plan['candidate_workspace']).parent.as_posix())+'/capability-migration-stage-'+uuid.uuid4().hex
            mkdirs(root,stage,changed)
            stage_snapshots={}
            for relative in plan['packages']:
                source=checked_path(root,plan['candidate_workspace']+'/'+relative,allow_missing=False)
                destination=checked_path(root,stage+'/'+relative)
                mkdirs(root,destination.parent.relative_to(root).as_posix(),changed)
                shutil.copytree(source,destination); changed.append(stage+'/'+relative)
                entry='ROLE.md' if '/roles/' in '/'+relative+'/' else 'SKILL.md'
                before=packages.snapshot(root,plan['candidate_workspace']+'/'+relative,entry=entry)
                after=packages.snapshot(root,stage+'/'+relative,entry=entry)
                if {k:v[-1] for k,v in after.items()}!={k:v[-1] for k,v in before.items()}: raise SafetyError('Staged candidate differs')
                stage_snapshots[relative]=_manifest(root,stage+'/'+relative)
            fresh,fresh_digest,_=_plan(root,request)
            if fresh_digest!=digest: raise SafetyError('Inputs changed during staging; live roots preserved')
            mkdirs(root,backup+'/originals',changed)
            marker={'migration_format_version':1,'status':'applying','preview_sha256':digest,'plan':plan,'stage':stage,'provenance':request['provenance']}
            write_json(root,MARKER,marker); changed.append(MARKER)
            marker_fp=fingerprint(checked_path(root,MARKER))
            if marker_fp[-1]!=hashlib.sha256(json_bytes(marker)).hexdigest() or read_json(checked_path(root,MARKER))!=marker: raise SafetyError('Migration marker changed immediately after creation')
            for relative in plan['destinations']:
                target=checked_path(root,relative)
                if _manifest(root,relative)!=plan['destinations'][relative]: raise SafetyError('Destination changed before migration move: '+relative)
                if target.exists():
                    destination=checked_path(root,backup+'/originals/'+relative)
                    mkdirs(root,destination.parent.relative_to(root).as_posix(),changed)
                    rename_exclusive(target,destination); changed.extend([relative,backup+'/originals/'+relative])
                    if _manifest(root,backup+'/originals/'+relative)!=plan['destinations'][relative]: raise SafetyError('Backup identity differs after move: '+relative)
            for relative in plan['packages']:
                target=checked_path(root,relative); mkdirs(root,target.parent.relative_to(root).as_posix(),changed)
                if _manifest(root,stage+'/'+relative)!=stage_snapshots[relative]: raise SafetyError('Staged candidate changed before publication')
                if target.exists(): raise SafetyError('Destination appeared before publication')
                rename_exclusive(checked_path(root,stage+'/'+relative,allow_missing=False),target); changed.append(relative)
            for relative in plan['packages']:
                if _manifest(root,relative)!=stage_snapshots[relative]: raise SafetyError('Published candidate changed before completion: '+relative)
            if _manifest(root,'.hai_env/config/roles')!=plan['settings']: raise SafetyError('Chosen settings changed during migration')
            marker['status']='complete'; write_json(root,MARKER,marker,marker_fp)
            result.update(backup_base=backup,marker=MARKER)
            return envelope('migrate',result=result,changed=changed)
        if apply:
            with lock(root): return run()
        return run()
    except (SafetyError,ValueError,TypeError,OSError) as exc:
        changed.extend(x for x in getattr(exc,'changed_files',[]) if x not in changed)
        return envelope('migrate','partial' if changed else 'blocked',changed=changed,issues=[str(exc)])
