"""Direct capability/reuse/settings/migration behavior; fixtures require a workspace path."""
import json,os,shutil,sys,tempfile,unittest
from pathlib import Path
from unittest import mock
TOOLS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TOOLS));sys.path.insert(0,str(TOOLS/'roles'));sys.path.insert(0,str(TOOLS/'skills'))
import role_tools,skill_tools
from runtime import skills,packages,activities,capability_migration
class SkillTests(unittest.TestCase):
    def setUp(self):
        parent=Path(os.environ.get('HAI_TEST_TMP',tempfile.gettempdir())).resolve()
        workspace=next(p for p in TOOLS.parents if (p/'.hai').is_dir())
        if not parent.is_relative_to(workspace):raise RuntimeError('Skill test temporary parent must be explicitly workspace-contained')
        self.temp=tempfile.TemporaryDirectory(prefix='hai-skill-',dir=parent);self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.prov={'source':'fixture','reason':'verify skills'}
    def write(self,rel,text):
        p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8');return p
    def skill(self,base='skills',name='inspect',metadata=''):
        return self.write(f'{base}/{name}/SKILL.md',f'---\nname: {name}\ndescription: Inspect supplied material.\n'+metadata+'---\n\nRead requested material and return actual findings.\n')
    def role(self,name,base='.hai_env/roles'):
        return self.write(f'{base}/{name}/ROLE.md',f'---\nname: {name}\ndescription: Review assigned work.\nmetadata:\n  hai-model-class: "standard"\n  hai-reasoning-effort: "high"\n  hai-skills: "inspect"\n---\n\n## Purpose\n\nReview authorized work.\n\n## Scope\n\nAssigned review.\n\n## Out of Scope\n\nUnauthorized edits.\n\n## Rules\n\n- **Authority.** The reviewer MUST stay within task authority.\n\n## Skills\n\nSelect declared methods.\n\n## References\n\nCaller instructions.\n')
    def migration(self):
        self.write('.hai_env/config/agent_instructions.md','');self.write('.hai_env/config/state.json',json.dumps({'state_format_version':3,'activities':{'location':'.hai_env/activities'},'features':{'chronicles':{'enabled':False}}}))
        p=self.root/'.hai/templates';p.mkdir(parents=True);shutil.copy2(TOOLS.parent/'templates/state.json',p/'state.json');(self.root/'.hai_env/activities').mkdir()
        result=activities.handle('create',self.root,{'layout_version':2,'initial_input':'Skill test','provenance':self.prov},True);self.assertTrue(result['ok'],result)
        candidate=result['result']['path']+'/work/agents/fixture/id/candidates';self.skill(candidate+'/skills')
        return {'activity_id':result['result']['state']['activity_id'],'candidate_workspace':candidate,'packages':['skills/inspect'],'writers_ended':True,'provenance':self.prov}
    def test_native_freeform_has_no_role_requirement(self):
        p=self.skill();self.assertTrue(skill_tools.validate(self.root,p.relative_to(self.root).as_posix())['ok']);self.assertFalse((self.root/'.hai_env/roles').exists())
    def test_installed_resolution_never_falls_back_to_source(self):
        self.skill();self.assertFalse(skills.handle('resolve',self.root,{'name':'inspect'},False)['ok']);self.skill('.hai_env/skills');self.assertTrue(skills.handle('resolve',self.root,{'name':'inspect'},False)['ok'])
    def test_direct_and_two_role_selection_share_one_method(self):
        self.skill('.hai_env/skills')
        for name in ['software-developer','quality-assurance']:
            self.role(name);result=packages.handle('skills',self.root,{'definition':f'.hai_env/roles/{name}/ROLE.md'},False);self.assertTrue(result['ok'],result);self.assertEqual(result['result']['skills'][0]['definition'],'.hai_env/skills/inspect/SKILL.md')
        self.assertTrue(skills.handle('resolve',self.root,{'name':'inspect'},False)['ok'])
    def test_missing_dependency_blocks_source_role_and_install(self):
        self.role('worker',base='roles');self.assertFalse(role_tools.validate(self.root,'roles/worker/ROLE.md')['ok'])
        self.assertFalse(packages.handle('install',self.root,{'source':'roles/worker','name':'worker','provenance':self.prov},False)['ok']);self.assertFalse((self.root/'.hai_env/roles/worker').exists())
    def test_flat_source_validation_is_independent(self):
        self.skill();self.role('worker',base='roles');self.assertTrue(role_tools.validate(self.root,'roles/worker/ROLE.md')['ok'])
    def test_direct_owner_configuration_is_chosen_once(self):
        self.skill('.hai_env/skills',metadata='metadata:\n  hai-settings-owner: "service-owner"\n');self.write('.hai_env/roles/service-owner/configuration/contract.json',json.dumps({'contract_format_version':3,'role':'service-owner','current_config_format_version':1,'supported_config_format_versions':[1],'settings':{'enabled':{'type':'boolean','default':False}}}))
        p=self.write('.hai_env/config/roles/service-owner.json',json.dumps({'config_format_version':1,'settings':{'enabled':True},'custom':'retain'}));before=p.read_bytes();result=skills.handle('resolve',self.root,{'name':'inspect'},False);self.assertTrue(result['ok'],result);self.assertTrue(result['result']['configuration']['settings']['enabled']);self.assertEqual(p.read_bytes(),before);self.assertFalse((p.parent/'inspect.json').exists())
    def test_preview_apply_preserves_original_and_blocks_retry(self):
        request=self.migration();p=self.skill();candidate=p.read_bytes();p.write_bytes(candidate+b'Local custom method.\n');original=p.read_bytes();preview=skills.handle('migrate',self.root,request,False);self.assertTrue(preview['ok'],preview);self.assertEqual(p.read_bytes(),original)
        request['expected_preview']=preview['result']['preview_sha256'];result=skills.handle('migrate',self.root,request,True);self.assertTrue(result['ok'],result);backup=self.root/result['result']['backup_base']/'originals/skills/inspect/SKILL.md';self.assertEqual(backup.read_bytes(),original);self.assertEqual(p.read_bytes(),candidate);self.assertFalse(skills.handle('migrate',self.root,request,True)['ok'])
    def test_stale_preview_and_unsafe_destination_preserve_bytes(self):
        request=self.migration();p=self.skill();preview=skills.handle('migrate',self.root,request,False);request['expected_preview']=preview['result']['preview_sha256'];p.write_bytes(p.read_bytes()+b'Changed.\n');before=p.read_bytes();self.assertFalse(skills.handle('migrate',self.root,request,True)['ok']);self.assertEqual(p.read_bytes(),before);request['packages']=['.hai'];self.assertFalse(skills.handle('migrate',self.root,request,False)['ok'])
    def test_partial_install_retains_backups_and_marker(self):
        request=self.migration();self.skill();preview=skills.handle('migrate',self.root,request,False);request['expected_preview']=preview['result']['preview_sha256'];original=capability_migration.rename_exclusive;counter=0
        def interrupt(a,b):
            nonlocal counter
            counter+=1
            if counter==2:raise OSError('injected interruption')
            return original(a,b)
        with mock.patch.object(capability_migration,'rename_exclusive',side_effect=interrupt):result=skills.handle('migrate',self.root,request,True)
        self.assertEqual(result['status'],'partial',result);self.assertTrue((self.root/capability_migration.MARKER).exists());self.assertFalse(skills.handle('migrate',self.root,request,True)['ok'])
        self.assertFalse(skills.handle('resolve',self.root,{'name':'inspect'},False)['ok'])
        self.assertFalse(packages.handle('skills',self.root,{'definition':'.hai_env/roles/worker/ROLE.md'},False)['ok'])

    def test_install_rechecks_target_after_staging(self):
        self.environment_only();self.skill();target=self.skill('.hai_env/skills');before=target.read_bytes();original=skills.shutil.copytree
        def changed(*args,**kwargs):
            result=original(*args,**kwargs);target.write_bytes(before+b'Concurrent change.\n');return result
        request={'source':'skills/inspect','name':'inspect','replace':True,'reviewed_differences':[],'provenance':self.prov}
        with mock.patch.object(skills.shutil,'copytree',side_effect=changed):result=skills.handle('install',self.root,request,True)
        self.assertEqual(result['status'],'partial',result);self.assertEqual(target.read_bytes(),before+b'Concurrent change.\n');self.assertFalse(list(target.parent.parent.glob('.hai-backup-*')))
    def environment_only(self):
        self.write('.hai_env/config/agent_instructions.md','');self.write('.hai_env/config/state.json',json.dumps({'state_format_version':3,'activities':{'location':'.hai_env/activities'},'features':{'chronicles':{'enabled':False}}}))
        p=self.root/'.hai/templates';p.mkdir(parents=True);shutil.copy2(TOOLS.parent/'templates/state.json',p/'state.json');(self.root/'.hai_env/activities').mkdir()
    def test_readonly_skill_operations_reject_apply(self):
        self.skill('.hai_env/skills')
        for operation,request in [('resolve',{'name':'inspect'}),('list',{}),('validate',{'definition':'.hai_env/skills/inspect/SKILL.md'})]:self.assertFalse(skills.handle(operation,self.root,request,True)['ok'])
    def test_linked_installed_skill_cannot_fall_back_to_source(self):
        self.skill();base=self.root/'.hai_env/skills';base.mkdir(parents=True)
        try:(base/'inspect').symlink_to(self.root/'skills/inspect',target_is_directory=True)
        except OSError:self.skipTest('Host cannot create symlink fixtures')
        self.assertFalse(skills.handle('resolve',self.root,{'name':'inspect'},False)['ok'])
    def test_missing_owner_and_invalid_settings_block_direct_dependency(self):
        self.skill('.hai_env/skills',metadata='metadata:\n  hai-settings-owner: "service-owner"\n')
        self.assertFalse(skills.handle('resolve',self.root,{'name':'inspect'},False)['ok'])


    def test_role_install_uses_installed_dependencies_without_source_collection(self):
        self.skill('.hai_env/skills');self.role('worker',base='incoming')
        result=packages.handle('install',self.root,{'source':'incoming/worker','name':'worker','provenance':self.prov},False)
        self.assertTrue(result['ok'],result);self.assertFalse((self.root/'skills').exists())
    def test_settings_free_configuration_needs_no_empty_contract(self):
        from runtime import environment
        self.role('worker')
        result=environment.handle('configuration/read',self.root,{'role':'worker'},False)
        self.assertTrue(result['ok'],result);self.assertEqual(result['status'],'not_required');self.assertFalse((self.root/'.hai_env/config/roles/worker.json').exists())
    def test_existing_settings_block_role_replacement_without_owner_contract(self):
        self.skill('.hai_env/skills');self.role('worker',base='incoming');saved=self.write('.hai_env/config/roles/worker.json',json.dumps({'config_format_version':1,'settings':{'chosen':True}}));before=saved.read_bytes()
        result=packages.handle('install',self.root,{'source':'incoming/worker','name':'worker','provenance':self.prov},False)
        self.assertFalse(result['ok'],result);self.assertEqual(saved.read_bytes(),before);self.assertFalse((self.root/'.hai_env/roles/worker').exists())


    def test_real_flat_sources_install_with_resolved_links_then_sources_absent(self):
        from runtime import package_content
        self.environment_only();repo=TOOLS.parent.parent
        shutil.copytree(repo/'.hai',self.root/'.hai',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(repo/'roles',self.root/'roles');shutil.copytree(repo/'skills',self.root/'skills')
        self.write('.hai_env/roles/catalogue.md','# Role catalogue\n\n| Role | Selection guide | Definition |\n| --- | --- | --- |\n')
        original={p.relative_to(self.root).as_posix():p.read_bytes() for directory in ['roles','skills'] for p in (self.root/directory).rglob('*') if p.is_file()}
        for source in sorted((self.root/'skills').iterdir()):
            if not source.is_dir():continue
            request={'source':source.relative_to(self.root).as_posix(),'name':source.name,'provenance':self.prov}
            result=skills.handle('install',self.root,request,True);self.assertTrue(result['ok'],result)
        self.assertFalse(skills.handle('resolve',self.root,{'name':'git-operations'},False)['ok'])
        for source in sorted((self.root/'roles').iterdir()):
            if not source.is_dir():continue
            request={'source':source.relative_to(self.root).as_posix(),'name':source.name,'provenance':self.prov}
            result=packages.handle('install',self.root,request,True);self.assertTrue(result['ok'],result)
        self.assertEqual(original,{p.relative_to(self.root).as_posix():p.read_bytes() for directory in ['roles','skills'] for p in (self.root/directory).rglob('*') if p.is_file()})
        (self.root/'roles').rename(self.root/'retained-source-roles');(self.root/'skills').rename(self.root/'retained-source-skills')
        for base,entry in [('.hai_env/roles','ROLE.md'),('.hai_env/skills','SKILL.md')]:
            for package in (self.root/base).iterdir():
                if not package.is_dir() or package.name.startswith('.'):continue
                relative=package.relative_to(self.root).as_posix();manifest=packages.snapshot(self.root,relative,entry=entry);content={name:(package/name).read_bytes() for name in manifest}
                self.assertEqual(package_content.validate(self.root,relative,content),[],relative)
        for name in ['git-operations','quality-verification']:
            result=skills.handle('resolve',self.root,{'name':name},False);self.assertTrue(result['ok'],result)
        definition='.hai_env/roles/software-developer/ROLE.md';self.assertTrue(packages.handle('skills',self.root,{'definition':definition},False)['ok'])
        example=(self.root/'.hai_env/roles/backlog-manager/conventions/backlog_conv.md').read_text(encoding='utf-8');self.assertIn('[BL-0001](new/BL-0001.md)',example)
    def test_complete_backlog_role_operates_without_skills_or_source_collections(self):
        import subprocess
        self.environment_only();repo=TOOLS.parent.parent
        shutil.copytree(repo/'.hai',self.root/'.hai',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(repo/'roles/backlog-manager',self.root/'roles/backlog-manager')
        result=packages.handle('install',self.root,{'source':'roles/backlog-manager','name':'backlog-manager','provenance':self.prov},True)
        self.assertTrue(result['ok'],result)
        (self.root/'roles').rename(self.root/'retained-source-roles')
        self.assertFalse((self.root/'roles').exists());self.assertFalse((self.root/'skills').exists())
        self.assertFalse((self.root/'.hai_env/skills').exists())
        definition='.hai_env/roles/backlog-manager/ROLE.md'
        self.assertTrue(packages.handle('validate',self.root,{'definition':definition},False)['ok'])
        dependencies=packages.handle('skills',self.root,{'definition':definition},False)
        self.assertTrue(dependencies['ok'],dependencies);self.assertEqual(dependencies['result']['skills'],[])
        self.assertFalse(skills.handle('resolve',self.root,{'name':'backlog-management'},False)['ok'])
        for location in ['backlog','planning/team-backlog']:
            self.write(location+'/catalogue.md','# Backlog\n\n| ID | Title | Status | File |\n| --- | --- | --- | --- |\n')
            for folder in ['new','closed']:(self.root/location/folder).mkdir()
            if location!='backlog':
                self.write('.hai_env/config/roles/backlog-manager.json',json.dumps({'config_format_version':1,'settings':{'location':location}}))
            before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
            checked=subprocess.run([sys.executable,'-B',str(self.root/'.hai_env/roles/backlog-manager/scripts/audit_backlog.py'),'--workspace',str(self.root)],capture_output=True,text=True,timeout=30)
            self.assertEqual(checked.returncode,0,checked.stdout+checked.stderr)
            report=json.loads(checked.stdout);self.assertTrue(report['ok'],report);self.assertEqual(report['location'],location)
            self.assertEqual(before,{p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_complete_specification_role_operates_without_skills_or_source_collections(self):
        import subprocess
        self.environment_only();repo=TOOLS.parent.parent
        shutil.copytree(repo/'.hai',self.root/'.hai',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(repo/'roles/specification-manager',self.root/'roles/specification-manager')
        source=self.root/'roles/specification-manager'
        contracts={name:(source/name).read_bytes() for name in ['contract.json','configuration/contract.json']}
        result=packages.handle('install',self.root,{'source':'roles/specification-manager','name':'specification-manager','provenance':self.prov},True)
        self.assertTrue(result['ok'],result)
        (self.root/'roles').rename(self.root/'retained-source-roles')
        self.assertFalse((self.root/'roles').exists());self.assertFalse((self.root/'skills').exists())
        self.assertFalse((self.root/'.hai_env/skills').exists())
        definition='.hai_env/roles/specification-manager/ROLE.md'
        self.assertTrue(packages.handle('validate',self.root,{'definition':definition},False)['ok'])
        dependencies=packages.handle('skills',self.root,{'definition':definition},False)
        self.assertTrue(dependencies['ok'],dependencies);self.assertEqual(dependencies['result']['skills'],[])
        self.assertFalse(skills.handle('resolve',self.root,{'name':'specification-management'},False)['ok'])
        installed=self.root/'.hai_env/roles/specification-manager'
        self.assertEqual(contracts,{name:(installed/name).read_bytes() for name in contracts})
        for settings in [None,{'config_format_version':1,'settings':{'enabled':False,'location':'product/specification'}}]:
            if settings:self.write('.hai_env/config/roles/specification-manager.json',json.dumps(settings))
            before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
            checked=subprocess.run([sys.executable,'-B',str(installed/'scripts/specification_configuration.py'),'--workspace',str(self.root)],capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual(checked.returncode,0,checked.stdout+checked.stderr)
            report=json.loads(checked.stdout);self.assertTrue(report['ok'],report)
            self.assertFalse((self.root/'.hai_env/specifications').exists());self.assertFalse((self.root/'product/specification').exists())
            self.assertEqual(before,{p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_portable_skill_installs_and_resolves_independently_without_roles(self):
        self.environment_only()
        self.skill('incoming',name='portable-document')
        self.write('incoming/portable-document/references/format.md','# Document format\n\nCaller-supplied content and outputs.\n')
        before={p.relative_to(self.root/'incoming/portable-document'):p.read_bytes() for p in (self.root/'incoming/portable-document').rglob('*') if p.is_file()}
        result=skills.handle('install',self.root,{'source':'incoming/portable-document','name':'portable-document','provenance':self.prov},True)
        self.assertTrue(result['ok'],result)
        (self.root/'incoming').rename(self.root/'retained-sources')
        self.assertFalse((self.root/'.hai_env/roles').exists())
        result=skills.handle('resolve',self.root,{'name':'portable-document'},False)
        self.assertTrue(result['ok'],result);self.assertNotIn('configuration_owner',result['result'])
        self.assertEqual(before,{p.relative_to(self.root/'.hai_env/skills/portable-document'):p.read_bytes() for p in (self.root/'.hai_env/skills/portable-document').rglob('*') if p.is_file()})

    def test_role_local_procedure_is_validated_in_final_logical_location(self):
        from runtime import package_content
        self.environment_only();self.skill('.hai_env/skills');p=self.role('worker',base='roles')
        self.write('.hai/concepts/example.md','# Example\n\nMeaning.\n')
        text=p.read_text(encoding='utf-8').replace('## Skills\n','## Procedures\n\n| Procedure | Trigger | File |\n| --- | --- | --- |\n| Inspect | A task requires it. | [Inspect](procedures/inspect.md) |\n\n## Skills\n')
        self.write('roles/worker/ROLE.md',text)
        self.write('roles/worker/procedures/inspect.md','# Inspect\n\n## Description\n\nInspect the supplied artifact.\n\n## Inputs\n\n| Input | Meaning | Requirement | Source | If absent |\n| --- | --- | --- | --- | --- |\n| [input:artifact] | Explicit artifact | Mandatory | Caller | Report dependency. |\n\n## Prerequisites\n\nAuthorized [input:artifact].\n\n## Rules\n\nNone.\n\n## Steps\n\n1. Read [input:artifact] and return [output:finding].\n\n## Outputs\n\n| Output | Meaning | Completion criteria |\n| --- | --- | --- |\n| [output:finding] | Actual finding | Input inspected. |\n\n## References\n\n- [term:example] -> [Example](../../../.hai/concepts/example.md)\n')
        request={'source':'roles/worker','name':'worker','provenance':self.prov}
        result=packages.handle('install',self.root,request,True);self.assertTrue(result['ok'],result)
        installed=self.root/'.hai_env/roles/worker/procedures/inspect.md';self.assertIn('../../../../.hai/concepts/example.md',installed.read_text(encoding='utf-8'))


    def test_native_inline_code_link_syntax_is_preserved_during_install(self):
        self.environment_only();p=self.skill();self.write('.hai/concepts/method.md','# Method\n\nShared meaning.\n')
        literal='Use `[label](new/example.md)` or ``a ` [other](also/missing.md)`` as syntax.\n'
        original=p.read_text(encoding='utf-8')+literal+'[Actual core reference](../../.hai/concepts/method.md)\n'
        p.write_text(original,encoding='utf-8')
        result=skills.handle('install',self.root,{'source':'skills/inspect','name':'inspect','provenance':self.prov},True)
        self.assertTrue(result['ok'],result);installed=(self.root/'.hai_env/skills/inspect/SKILL.md').read_text(encoding='utf-8')
        self.assertIn(literal,installed);self.assertIn('(../../../.hai/concepts/method.md)',installed);self.assertEqual(p.read_text(encoding='utf-8'),original)

if __name__=='__main__':unittest.main()
