#!/usr/bin/python3
"""Native six-character barrel integration test; no character/selector writes."""
import importlib.util
import json
from pathlib import Path

spec=importlib.util.spec_from_file_location('driver',Path(__file__).with_name('krusha-test.py'))
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
d.REPORT_NAME='krusha-barrel-tests.json'
d.results={'rom_sha256':d.DIGEST,'cold_boot':True,'fixtures':'Player position only. Barrel navigation and selection use controller input.','checks':[]}

def barrel_data():
    bars=[a for a in d.scene('barrel-scene')['actors'] if a['type'] in (98,136,137) and a['state']==1]
    if not bars:raise RuntimeError('No active barrel selector')
    p=int(bars[0]['pointer'],16)
    return p,d.mem(p+0x174)

def previews():
    models=[a for a in d.scene('barrel-previews')['actors'] if a['type'] in (316,317)]
    for a in models:
        p=int(a['pointer'],16);data=d.mem(p+0x174)
        a['identity']=d.mem(data,'u16') if a['type']==316 else 'locked'
        a['mesh']=d.mem(p+0x146,'u16')&3
    return models

def enter():
    d.place([2773,500,2320],0,wait=1)
    d.press('c',.7,.2)
    d.cmd(keys=['Up','Shift_L'],seconds=.4,wait=1,shot='barrel-first-entry')
    d.check('native barrel entry',d.status()['player']['state']==0x42,d.status())

def run():
    d.cmd(down=['f'])
    for i in range(50):
        if d.status()['map']==80:break
        d.press('Return',.3,.8)
    d.cmd(up=['f'])
    d.cmd(wait=8)
    for i in range(10):
        d.press('Shift_L',.3,1.5)
        if d.status()['map']==34:break
    d.cmd(wait=3)
    d.check('cold boot into adventure',d.status()['map']==34 and d.status()['character']==0,d.status())
    d.place([2780,500,2260],2048,wait=1)
    d.checkpoint(0,'six-barrel-dk-isles')
    enter()
    p,data=barrel_data()
    models=previews()
    d.check('six native character models including Krusha',len(models)==6 and sorted(a['identity'] for a in models)==[2,3,4,5,6,7],models)
    d.cmd(record='six-character-tag-barrel')
    for key,expected in [('Right',[1,2,3,4,5,0]),('Left',[5,4,3,2,1,0])]:
        seen=[]
        for value in expected:
            d.press(key,.2,1.3,shot='barrel-'+key.lower()+'-'+str(value))
            seen.append(d.mem(data+6,'u8'))
        d.check('six-character barrel rotation '+key,seen==expected,seen)
    d.press('Left',.2,1.3,shot='barrel-krusha-selected')
    d.check('Krusha is sixth selectable slot',d.mem(data+6,'u8')==5)
    d.checkpoint(6,'six-barrel-krusha-selected')
    d.press('Shift_L',.2,3,shot='barrel-krusha-exit')
    s=d.status()
    d.check('barrel selects native adventure Krusha',s['character']==5 and s['player']['actor']==7 and s['player']['state']!=0x42,s)
    d.place([2780,500,2260],2048,wait=1)
    d.check('barrel preview actors cleaned up',not previews())
    enter()
    p,data=barrel_data()
    d.check('entering as Krusha starts on Krusha',d.mem(data+6,'u8')==5,d.mem(data+6,'u8'))
    d.press('Right',.2,1.3)
    d.press('Shift_L',.2,3)
    d.check('Krusha wraps to and selects DK',d.status()['character']==0,d.status())
    d.cmd(stop_record=True)
    d.place([2780,500,2260],2048,wait=1)
    d.press('a',wait=1)
    d.checkpoint(5,'six-barrel-ready-to-play')
    d.results['complete']=True
    (d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')

try:
    d.start();run()
    print('BARREL_CHECKS_COMPLETE; interactive controller ready',flush=True)
except Exception as exc:
    d.results['error']=str(exc)
    (d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
    print(json.dumps({'test_error':str(exc)}),flush=True)
    try:d.cmd(shot='barrel-test-failure')
    except Exception:pass
    print('INTERACTIVE_CONTROLLER_READY',flush=True)
d.interactive()
