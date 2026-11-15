import json,pathlib,sys,os,tempfile
root=pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0,str(root/'.hai/tools'));sys.path.insert(0,str(root/'.hai/tools/runtime/tests'))
from test_chronicles import CoreChronicleTests
from chronicles.read_codex_source import read_source
case=CoreChronicleTests();case.setUp()
try:
 case.state['features']['chronicles']['mode']='best_effort';case.save_state()
 assert case.sync(sources=[case.assignment])['ok']
 case.lines[0]['payload']['id']='different-session';case.save()
 result=case.close();print('wrong_identity_close',json.dumps({'ok':result['ok'],'result':result.get('result',{}).get('recording'),'issues':result.get('issues')}))
finally:case.tearDown()
case=CoreChronicleTests();case.setUp()
try:
 case.lines.append(case.record('event_msg',{'type':'future_user_message','text':'a hidden real user message'}));case.save()
 result=read_source(case.source,'auto','one');print('unknown_text_event',json.dumps({'ok':result['ok'],'issues':result['issues'],'texts':[m['text'] for m in result['messages']]}))
finally:case.tearDown()

from runtime import activities
case=CoreChronicleTests();case.setUp()
try:
 assert case.sync(sources=[case.assignment])['ok']
 closed=case.close();assert closed['ok'],closed
 case.lines[1:1]=[case.record('event_msg',{'type':'token_count'}) for _ in range(3)];case.save()
 created=activities.handle('create',case.root,{'initial_input':'new task','provenance':case.prov},True);assert created['ok'],created
 case.ident=created['result']['state']['activity_id'];case.base=case.root/created['result']['path']
 assignment={**case.assignment,'start_position':5,'enabled_intervals':[{'start':{'source_session_id':'one','source_position':5},'end':None,'provenance':'new fixture work'}]}
 result=case.sync(sources=[assignment]);print('shifted_archived_overlap',json.dumps({'ok':result['ok'],'issues':result.get('issues'),'message_count':result.get('result',{}).get('message_count')}))
finally:case.tearDown()
