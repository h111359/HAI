"""Single-record conversation preservation, reconciliation and lifecycle coverage."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from runtime import activities, recording, chronicles, conversation, chat, environment, startup
from runtime.storage import fingerprint, checked_path, SafetyError
import test_chronicles as legacy_tests


class ConversationTests(unittest.TestCase):
    save_state = legacy_tests.CoreChronicleTests.save_state
    record = legacy_tests.CoreChronicleTests.record
    message = legacy_tests.CoreChronicleTests.message
    save = legacy_tests.CoreChronicleTests.save
    sync = legacy_tests.CoreChronicleTests.sync
    close = legacy_tests.CoreChronicleTests.close
    tearDown = legacy_tests.CoreChronicleTests.tearDown

    def setUp(self):
        legacy_tests.CoreChronicleTests.setUp(self)
        result = activities.handle('migrate-layout', self.root, {'activity_id':self.ident,
            'summary':'Conversation fixture','provenance':self.prov}, True)
        self.assertTrue(result['ok'], result)
        for n, line in enumerate(self.lines):
            if line['type'] == 'event_msg': line['payload']['id'] = 'message-' + str(n)
        self.lines = self.lines[:4]  # Progress capture is tested explicitly below.
        self.save()

    def messages(self):
        return chat.load(self.root, (self.base/'system/chat.jsonl').relative_to(self.root).as_posix(), self.ident)[0]

    def native(self): return [m for m in self.messages() if 'source' in m]

    def test_exact_messages_single_store_idempotent_and_append_prefix(self):
        before=(self.base/'system/chat.jsonl').read_bytes()
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        self.assertEqual([m['text'] for m in self.native()], [self.lines[2]['payload']['message'], self.lines[3]['payload']['message']])
        raw=(self.base/'system/chat.jsonl').read_bytes();self.assertTrue(raw.startswith(before))
        self.assertTrue(self.sync()['ok']);self.assertEqual(raw,(self.base/'system/chat.jsonl').read_bytes())
        self.assertFalse((self.base/'chronicles').exists())
        state=json.loads((self.base/'system/recording.json').read_text())
        self.assertNotIn('text',state['sources'][0]['index'][0])
        self.assertTrue(recording.handle('verify',self.root,{'activity_id':self.ident},False)['ok'])

    def test_always_enabled_and_disabled_setting_rejected(self):
        self.state['features']['chronicles']['enabled']=False;self.save_state()
        self.assertTrue(self.sync(sources=[self.assignment])['ok']);self.assertEqual(len(self.native()),2)
        with self.assertRaises(ValueError):
            environment.handle('environment/configure',self.root,{'changes':{'features.chronicles.enabled':False},'provenance':self.prov},True)

    def test_backfill_every_missing_occurrence_not_only_tail(self):
        self.lines.append(self.message('user_message','again',id='a'));self.lines.append(self.message('user_message','again',id='b'));self.save()
        self.assertTrue(self.sync(sources=[self.assignment])['ok']);self.assertEqual(len(self.native()),4)
        self.lines.insert(3,self.record('event_msg',{'type':'future_chat','message':'unknown'}));self.save()
        # Stable identities still match across a changed source representation.
        result=self.sync();self.assertTrue(result['ok'],result)
        self.assertEqual(len(self.native()),4)
        self.assertEqual(result['result']['coverage'],'partial')
        self.lines.append(self.message('agent_message','new delivered',phase='final_answer',id='new'));self.save()
        result=recording.handle('verify',self.root,{'activity_id':self.ident},False)
        self.assertEqual(result['result']['status'],'needs_synchronization')
        self.assertTrue(self.sync()['ok']);self.assertEqual(self.native()[-1]['text'],'new delivered')

    def test_unknown_records_do_not_suppress_known(self):
        self.lines.insert(3,self.record('future','unknown'));self.save()
        result=self.sync(sources=[self.assignment]);self.assertTrue(result['ok'],result)
        self.assertEqual(result['result']['coverage'],'partial');self.assertEqual(len(self.native()),2)

    def test_append_before_state_failure_replays_without_duplicates(self):
        original=conversation.write_json
        calls=[]
        def fail_final(*args,**kwargs):
            calls.append(True)
            if len(calls)==2:raise OSError('state publish failed')
            return original(*args,**kwargs)
        with mock.patch('runtime.conversation.write_json',side_effect=fail_final):
            result=self.sync(sources=[self.assignment])
        self.assertFalse(result['ok']);self.assertEqual(len(self.native()),2)
        result=self.sync();self.assertTrue(result['ok'],result);self.assertEqual(len(self.native()),2)

    def test_two_sessions_can_share_native_message_id(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        second=self.root/'second.jsonl';lines=copy.deepcopy(self.lines);lines[0]['payload']['id']='two'
        second.write_text(''.join(json.dumps(x)+'\n' for x in lines))
        b=copy.deepcopy(self.assignment);b['path']=str(second);b['session_id']='two';b['enabled_intervals'][0]['start']['source_session_id']='two'
        result=self.sync(sources=[b]);self.assertTrue(result['ok'],result);self.assertEqual(len(self.native()),4)
        self.assertEqual(len({m['source_message_id'] for m in self.native()}),4)

    def test_unavailable_source_does_not_suppress_other_source(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        b=copy.deepcopy(self.assignment);b['session_id']='unavailable';b['path']=str(self.root/'missing.jsonl');b['enabled_intervals'][0]['start']['source_session_id']='unavailable'
        self.lines.append(self.message('agent_message','present',phase='final_answer',id='present'));self.save()
        with mock.patch('runtime.source_discovery.resolve',side_effect=FileNotFoundError('unavailable')):
            result=self.sync(sources=[b])
        self.assertTrue(result['ok'],result);self.assertEqual(len(self.native()),3);self.assertTrue(result['result']['warnings'])

    def test_retained_chat_tampering_is_detected(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        path=self.base/'system/chat.jsonl';path.write_bytes(path.read_bytes().replace(b'Exact answer',b'Wrong answer'))
        result=self.sync();self.assertFalse(result['ok']);self.assertIn('changed',str(result['issues']))

    def test_migration_preserves_all_bytes_even_without_native_source(self):
        base=self.base.relative_to(self.root).as_posix()
        chronicles.synchronize(self.root,base,self.ident,{'sources':[self.assignment],'provenance':self.prov},activities.now(),True,fingerprint(self.base/'system/state.json'))
        files={p.relative_to(self.base).as_posix():p.read_bytes() for parent in ('chronicles','system/chronicles') for p in (self.base/parent).rglob('*') if p.is_file()}
        before=(self.base/'system/chat.jsonl').read_bytes();self.source.unlink()
        result=recording.handle('migrate',self.root,{'activity_id':self.ident,'provenance':self.prov},True)
        self.assertTrue(result['ok'],result);self.assertEqual(len(self.native()),2)
        self.assertTrue((self.base/'system/chat.jsonl').read_bytes().startswith(before))
        backup=self.root/result['result']['backup_path']
        for relative,raw in files.items():self.assertEqual((backup/relative).read_bytes(),raw)
        self.assertFalse((self.base/'chronicles').exists());self.assertFalse((self.base/'system/chronicles').exists())
        self.assertTrue(recording.handle('migrate',self.root,{'activity_id':self.ident,'provenance':self.prov},True)['ok'])

    def test_close_flushes_missing_messages_and_seals_assignment(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        self.lines.append(self.message('agent_message','last reply',phase='final_answer',id='last'));self.save()
        result=self.close();self.assertTrue(result['ok'],result)
        archived=self.root/result['result']['archive_path']
        messages=chat.load(self.root,(archived/'system/chat.jsonl').relative_to(self.root).as_posix(),self.ident)[0]
        self.assertEqual(messages[-1]['text'],'last reply')
        data=json.loads((archived/'system/recording.json').read_text());self.assertIsNotNone(data['sources'][0]['binding']['end_position'])

    def test_turn_identity_recovers_changed_native_ids_without_duplicate_text(self):
        for line in self.lines[2:4]:line['payload']['turn_id']='turn'
        self.save();self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        for line in self.lines[2:4]:line['payload']['id']+='-rewritten'
        self.save();result=self.sync();self.assertTrue(result['ok'],result);self.assertEqual(len(self.native()),2)
        self.assertTrue(self.sync()['ok']);self.assertEqual(len(self.native()),2)
        self.assertTrue(self.sync()['ok']);self.assertEqual(len(self.native()),2)

    def test_old_enablement_intervals_do_not_disable_capture(self):
        self.assignment['enabled_intervals'][0]['end']={'source_session_id':'one','source_position':2}
        result=self.sync(sources=[self.assignment]);self.assertTrue(result['ok'],result);self.assertEqual(len(self.native()),2)

    def test_post_automatically_imports_missing_saved_reply(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        self.lines.append(self.message('agent_message','missing delivered reply',phase='final_answer',id='new'));self.save()
        result=activities.handle('chat-post',self.root,{'activity_id':self.ident,'author':'human','role':'human','message_type':'instruction','text':'next request','provenance':self.prov},True)
        self.assertTrue(result['ok'],result);self.assertEqual(self.native()[-1]['text'],'missing delivered reply')

    def test_mandatory_closure_stores_known_messages_before_reporting_gaps(self):
        self.lines.insert(3,self.record('future',{}));self.save()
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        result=self.close(recording_requirement={'enabled':True,'mandatory':True})
        self.assertFalse(result['ok']);self.assertTrue(self.base.exists());self.assertEqual(len(self.native()),2)

    def test_unavailable_registered_source_prevents_unbounded_archive(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok']);self.source.unlink()
        with mock.patch('runtime.source_discovery.resolve',side_effect=FileNotFoundError('unavailable')):
            result=self.close()
        self.assertFalse(result['ok']);self.assertTrue(self.base.exists());self.assertIn('boundaries',str(result['issues']))

    def test_direct_verify_requires_legacy_migration(self):
        base=self.base.relative_to(self.root).as_posix()
        chronicles.synchronize(self.root,base,self.ident,{'sources':[self.assignment],'provenance':self.prov},activities.now(),True,fingerprint(self.base/'system/state.json'))
        result=recording.handle('verify',self.root,{'activity_id':self.ident},False)
        self.assertFalse(result['ok']);self.assertIn('migrate',str(result['issues']))

    def test_migration_retries_after_import_publication_failure_without_losing_prefix(self):
        base=self.base.relative_to(self.root).as_posix()
        chronicles.synchronize(self.root,base,self.ident,{'sources':[self.assignment],'provenance':self.prov},activities.now(),True,fingerprint(self.base/'system/state.json'))
        before=(self.base/'system/chat.jsonl').read_bytes()
        original=conversation.write_json
        def fail_retiring(root,path,value,*args,**kwargs):
            if value.get('migration',{}).get('status')=='retiring':raise OSError('interrupted import publication')
            return original(root,path,value,*args,**kwargs)
        with mock.patch('runtime.conversation.write_json',side_effect=fail_retiring):
            result=recording.handle('migrate',self.root,{'activity_id':self.ident,'provenance':self.prov},True)
        self.assertFalse(result['ok']);self.assertEqual(len(self.native()),2);self.assertTrue((self.base/'chronicles').exists())
        result=recording.handle('migrate',self.root,{'activity_id':self.ident,'provenance':self.prov},True)
        self.assertTrue(result['ok'],result);self.assertEqual(len(self.native()),2)
        self.assertTrue((self.base/'system/chat.jsonl').read_bytes().startswith(before))

    def test_owning_activity_change_during_read_stops_publication(self):
        original=conversation.inspect
        def mutate(*args,**kwargs):
            result=original(*args,**kwargs)
            p=self.base/'system/state.json';state=json.loads(p.read_text());state['steps']['analysis']='completed';p.write_text(json.dumps(state))
            return result
        with mock.patch('runtime.conversation.inspect',side_effect=mutate):
            result=self.sync(sources=[self.assignment])
        self.assertFalse(result['ok']);self.assertEqual(len(self.native()),0)

    def test_prepared_reply_is_not_claimed_delivered(self):
        result=activities.handle('chat-post',self.root,{'activity_id':self.ident,'author':'host-coordinator','role':'assistant','message_type':'reply','delivery_status':'prepared','text':'not delivered yet','provenance':self.prov},True)
        self.assertTrue(result['ok'],result);self.assertEqual(self.messages()[-1]['delivery_status'],'prepared')
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        prepared=[m for m in self.messages() if m['text']=='not delivered yet'];self.assertEqual(len(prepared),1);self.assertEqual(prepared[0]['delivery_status'],'prepared')

    def test_newly_recognized_middle_occurrence_is_backfilled(self):
        self.lines.insert(3,self.record('future',{}));self.save()
        self.assertTrue(self.sync(sources=[self.assignment])['ok']);self.assertEqual(len(self.native()),2)
        from chronicles import read_codex_source
        original=read_codex_source.read_source
        def recognized(*args,**kwargs):
            data=original(*args,**kwargs)
            data['messages'].append({'source_position':3,'role':'user','text':'newly supported middle message','timestamp':'2026-11-07T00:00:00Z','message_id':'middle','source_session_id':'one'})
            data['messages'].sort(key=lambda m:m['source_position']);data['gaps']=[]
            return data
        with mock.patch('chronicles.read_codex_source.read_source',side_effect=recognized):
            result=recording.handle('verify',self.root,{'activity_id':self.ident},False)
            self.assertTrue(result['ok'],result);self.assertEqual(result['result']['status'],'needs_synchronization')
            result=self.sync();self.assertTrue(result['ok'],result)
            self.assertEqual(len(self.native()),3);self.assertEqual(self.native()[-1]['text'],'newly supported middle message')

    def test_visible_commentary_is_recorded_but_internal_analysis_is_not(self):
        self.lines.append(self.message('agent_message','visible progress',phase='commentary',id='progress'))
        self.lines.append(self.message('agent_message','private analysis',phase='analysis',id='analysis'));self.save()
        result=self.sync(sources=[self.assignment]);self.assertTrue(result['ok'],result)
        self.assertIn('visible progress',[m['text'] for m in self.native()]);self.assertNotIn('private analysis',[m['text'] for m in self.native()])

    def test_reply_arriving_during_close_is_caught_and_imported_on_retry(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        from runtime import usage
        original=usage.update
        def late_reply(*args,**kwargs):
            result=original(*args,**kwargs)
            self.lines.append(self.message('agent_message','late delivered reply',phase='final_answer',id='late'));self.save()
            return result
        with mock.patch('runtime.usage.update',side_effect=late_reply):result=self.close()
        self.assertFalse(result['ok']);self.assertTrue(self.base.exists())
        result=self.sync();self.assertTrue(result['ok'],result);self.assertEqual(self.native()[-1]['text'],'late delivered reply')
        self.assertTrue(self.close()['ok'])

    def test_rebased_fallback_position_cannot_collide_with_new_message(self):
        for n,line in enumerate(self.lines[2:4]):
            line['payload'].pop('id',None);line['payload']['turn_id']='old-turn-'+str(n)
        self.save();self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        self.lines.pop(1);self.save()
        result=self.sync();self.assertTrue(result['ok'],result);self.assertEqual(len(self.native()),2)
        self.lines.append(self.message('user_message','new occurrence reusing old position',turn_id='new-turn'));self.save()
        result=self.sync();self.assertTrue(result['ok'],result);self.assertEqual(len(self.native()),3)
        self.assertEqual(self.native()[-1]['text'],'new occurrence reusing old position')
        self.assertTrue(self.sync()['ok']);self.assertEqual(len(self.native()),3)

    def test_original_session_start_change_is_not_a_format_rewrite(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        self.lines[0]['payload']['timestamp']='2026-11-08T00:00:00Z';self.save()
        result=self.sync();self.assertFalse(result['ok']);self.assertEqual(len(self.native()),2)

    def test_empty_saved_reply_is_preserved_exactly(self):
        self.lines[3]['payload']['message']='';self.save()
        result=self.sync(sources=[self.assignment]);self.assertTrue(result['ok'],result)
        self.assertEqual(self.native()[-1]['text'],'');self.assertTrue(self.sync()['ok'])

    def test_completed_item_commentary_and_auto_representation_are_captured(self):
        self.assignment['representation']='auto'
        self.lines.append(self.record('event_msg',{'type':'item_completed','item':{'type':'AgentMessage','id':'completed-progress','phase':'commentary','content':[{'type':'Text','text':'completed visible progress'}]}}));self.save()
        result=self.sync(sources=[self.assignment]);self.assertTrue(result['ok'],result)
        self.assertEqual(self.native()[-1]['text'],'completed visible progress');self.assertEqual(len(self.native()),3)

    def test_migration_references_survive_activity_archival(self):
        base=self.base.relative_to(self.root).as_posix()
        chronicles.synchronize(self.root,base,self.ident,{'sources':[self.assignment],'provenance':self.prov},activities.now(),True,fingerprint(self.base/'system/state.json'))
        result=recording.handle('migrate',self.root,{'activity_id':self.ident,'provenance':self.prov},True)
        self.assertTrue(result['ok'],result);self.assertTrue(self.sync()['ok'])
        result=self.close();self.assertTrue(result['ok'],result)
        archived=self.root/result['result']['archive_path'];state=json.loads((archived/'system/recording.json').read_text())
        self.assertTrue((archived/state['migration']['backup']/'system/chronicles/core.json').is_file())
        checked=recording.handle('verify',self.root,{'activity_id':self.ident},False);self.assertTrue(checked['ok'],checked)

    def test_migration_manifest_cannot_retire_chat(self):
        self.assertTrue(self.sync(sources=[self.assignment])['ok'])
        path=self.base/'system/recording.json';data=json.loads(path.read_text())
        data['migration']={'status':'complete','backup':'history/recording/before-unified-v1','files':{'system/chat.jsonl':'0'*64},'chat_prefix_bytes':0,'chat_prefix_sha256':'0'*64}
        path.write_text(json.dumps(data));before=(self.base/'system/chat.jsonl').read_bytes()
        result=recording.handle('migrate',self.root,{'activity_id':self.ident,'provenance':self.prov},True)
        self.assertFalse(result['ok']);self.assertEqual(before,(self.base/'system/chat.jsonl').read_bytes())
