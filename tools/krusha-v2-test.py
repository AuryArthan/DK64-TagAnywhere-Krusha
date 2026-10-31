#!/usr/bin/python3
"""Controller tests for Krusha's gun, mesh state, barrel entry and saved option."""
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('driver', Path(__file__).with_name('krusha-test.py'))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
d.REPORT_NAME = 'krusha-v2-tests.json'
d.results = {'rom_sha256': d.DIGEST, 'fixtures': 'Same-build native checkpoint and logged positions only', 'checks': []}

def gun():
    p = int(d.status()['player_pointer'], 16)
    return {'gun': d.mem(p+0x20C,'u8'), 'mesh': d.mem(p+0x146,'u16') & 3,
            'status': d.status()}

def gun_check(name, drawn):
    g = gun()
    d.check(name, g['gun']==int(drawn) and g['mesh']==(1 if drawn else 2), g)

def bazooka():
    d.press('1',.1,.1); d.press('F7',.1,2)
    d.check('same-build state reload', d.status()['character']==5 and d.status()['map']==34,d.status())
    d.place([2940,500,2220],2048,wait=1)
    gun_check('Krusha selected with unarmed mesh',False)
    d.cmd(record='krusha-v2-bazooka')
    d.combo('j',wait=.8,shot='v2-bazooka-equipped')
    gun_check('bazooka equips with armed mesh',True)
    ammo = d.status()['inventory'][0]
    # Inspect before screenshot capture lets the fast projectile hit a wall.
    d.press('Control_L',.1,0)
    d.cmd(tap='p',wait=0)
    after=d.status()['inventory'][0]
    actors=[a for a in d.scene('v2-bazooka-projectile')['actors'] if a['type']==171]
    d.check('bazooka fires native projectile and consumes one shared round',after==ammo-1 and bool(actors),{'before':ammo,'after':after,'projectiles':actors})
    d.cmd(shot='v2-bazooka-firing')
    d.cmd(tap='p',wait=0)
    d.cmd(wait=1)
    d.combo('j',wait=.8,shot='v2-bazooka-holstered')
    gun_check('bazooka holsters with unarmed mesh',False)
    d.combo('k',wait=.8)
    d.check('unarmed camera enters',d.status()['player']['state']==4,d.status())
    d.press('i',wait=1)
    gun_check('unarmed camera exit keeps unarmed mesh',False)
    d.combo('j',wait=.8)
    d.press('i',wait=.8)
    d.check('bazooka enters first-person aim',d.status()['player']['state']==2,d.status())
    d.press('i',wait=1)
    gun_check('first-person aim exit restores bazooka mesh',True)
    d.press('d',wait=.8); d.press('a',wait=.8,shot='v2-retag-unarmed')
    gun_check('retagging Krusha clears previous armed state',False)
    d.cmd(stop_record=True)

def barrel():
    d.place([2773,500,2320],0,wait=1)
    d.press('c',.7,.2)
    d.cmd(keys=['Up','Shift_L'],seconds=.4,wait=1,shot='v2-tag-barrel-entry')
    s=d.status()
    d.check('Krusha enters tag barrel without identity spoof',s['character']==5 and s['player']['state']==0x42,s)
    d.press('Right',.25,1.3) # Sixth slot Krusha -> DK.
    d.press('Shift_L',wait=2,shot='v2-tag-barrel-exit')
    s=d.status()
    d.check('tag barrel selects native Kong and exits safely',s['character']==0 and s['player']['state']!=0x42,s)
    d.place([2780,500,2260],2048,wait=1)
    d.press('a',wait=1)
    gun_check('Krusha available after barrel selection',False)
    # Exercise the two new features together: enter while the bazooka is out,
    # rotate the native selector, and leave as a different original Kong.
    d.combo('j',wait=.8)
    d.place([2773,500,2320],0,wait=1)
    d.press('c',.7,.2)
    d.cmd(keys=['Up','Shift_L'],seconds=.4,wait=1)
    s=d.status()
    d.check('armed Krusha enters tag barrel safely',s['character']==5 and s['player']['state']==0x42,s)
    d.press('Right',.25,1.3)
    d.press('Right',.25,2,shot='v2-tag-barrel-rotate')
    d.press('Shift_L',wait=2)
    s=d.status()
    d.check('native barrel carousel selects another Kong after armed entry',s['character'] in (1,2,3,4) and s['player']['state']!=0x42,s)
    d.place([2780,500,2260],2048,wait=1)
    for i in range(6):
        if d.status()['character']==5: break
        d.press('d',wait=.8)
    gun_check('returning from armed barrel entry starts Krusha unarmed',False)
    d.check('final checkpoint is ordinary adventure movement',d.status()['player']['state']==12,d.status())
    d.checkpoint(5,'krusha-v2-ready-to-play')

def barrel_checkpoint():
    d.press('6',.1,.1);d.press('F7',.1,2)
    actors=d.scene('barrel-checkpoint-reload')['actors']
    b=next(a for a in actors if a['type'] in (98,136,137) and a['state']==1)
    data=d.mem(int(b['pointer'],16)+0x174)
    d.check('open sixth-slot checkpoint reloads after emulator restart',d.status()['player']['state']==0x42 and d.mem(data+6,'u8')==5,d.status())
    d.press('Shift_L',.2,3)
    d.check('restored barrel checkpoint selects Krusha',d.status()['character']==5 and d.status()['player']['actor']==7,d.status())
    d.place([2780,500,2260],2048,wait=1)
    actors=d.scene('barrel-checkpoint-cleanup')['actors']
    d.check('restored sixth-slot checkpoint cleans up previews and spotlight',not any(a['type'] in (310,316,317) for a in actors))

try:
    d.start()
    barrel_checkpoint()
    bazooka()
    barrel()
    d.results['complete']=True
    (d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
    print('GUN_AND_BARREL_CHECKS_COMPLETE; interactive controller ready',flush=True)
except Exception as exc:
    d.results['error']=str(exc)
    (d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
    print(json.dumps({'test_error':str(exc)}),flush=True)
    try:d.cmd(shot='v2-test-failure')
    except Exception:pass
    print('INTERACTIVE_CONTROLLER_READY',flush=True)
d.interactive()
