#!/usr/bin/python3
"""Sixth-slot animations, every selection, locked Kongs and a second map."""
import importlib.util
import json
from pathlib import Path

spec=importlib.util.spec_from_file_location('driver',Path(__file__).with_name('krusha-test.py'))
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
d.REPORT_NAME='krusha-barrel-extra-tests.json'
d.results={'rom_sha256':d.DIGEST,'fixtures':'Same-build checkpoint; positions/loading zones; temporary unlock flags restored. No selector, character, animation or code writes.','checks':[]}

def scene(name='barrel-extra'):
    return d.scene(name)['actors']

def enter(position=(2773,500,2330)):
    # A closer, ordinary approach also catches Diddy's earlier jump apex.
    # A missed jump is a fixture failure, not an absent/crashed barrel.
    attempts=[]
    for attempt in range(3):
        d.place(list(position),0,wait=1)
        d.press('c',.7,.2)
        d.cmd(keys=['Up','Shift_L'],seconds=.4,wait=1.5)
        for _ in range(4):
            actors=scene()
            active=[a for a in actors if a['type'] in (98,136,137) and a['state']==1]
            if active:return d.mem(int(active[0]['pointer'],16)+0x174),actors
            if d.status()['player']['state']!=0x42:break
            d.cmd(wait=.3)
        attempts.append(d.status())
        d.results.setdefault('entry_fixture_retries',[]).append({'position':position,'attempt':attempt,'status':attempts[-1]})
    raise RuntimeError('Barrel approach missed after three controller jumps: '+json.dumps(attempts))

def choose(data,index):
    for i in range(6):
        if d.mem(data+6,'u8')==index:break
        d.press('Right',.2,1.1)
    d.check('cursor reaches slot '+str(index),d.mem(data+6,'u8')==index)

def cleanup():
    d.place([2780,500,2260],2048,wait=1)
    remaining=[a for a in scene('barrel-cleanup') if a['type'] in (310,316,317)]
    d.check('all previews and the real spotlight deleted',not remaining,remaining)

def animation():
    data,actors=enter()
    k=next(int(a['pointer'],16) for a in actors if a['type']==316 and d.mem(d.mem(int(a['pointer'],16)+0x174),'u16')==7)
    metadata=d.mem(k)
    model=[d.mem(0x807FB630+i*12,'u16') for i in range(d.mem(0x807FBB30,'u16')+1) if d.mem(0x807FB634+i*12)==metadata]
    d.check('sixth preview uses actual Krusha model DB and holstered mesh',model==[0xDB] and d.mem(k+0x146,'u16')&3==2,model)
    anim=d.mem(k+4)
    d.check('Krusha waiting animation',d.mem(anim+0x64,'u16')==0x1DC,d.mem(anim+0x64,'u16'))
    d.press('Left',.2,1.2)
    d.check('Krusha selected animation uses his own multiplayer victory',d.mem(anim+0x64,'u16')==0x43A,d.mem(anim+0x64,'u16'))
    channel=d.mem(anim)
    before=d.mem(channel+4,'f32'); d.cmd(wait=.35);after=d.mem(channel+4,'f32')
    d.check('Krusha animation advances rather than holding a static pose',after!=before,[before,after])
    d.cmd(shot='barrel-krusha-animated')
    d.press('Right',.2,1.2)
    d.check('Krusha deselection returns to his own waiting animation',d.mem(anim+0x64,'u16')==0x1DC,d.mem(anim+0x64,'u16'))
    d.press('Shift_L',.2,3)
    cleanup()

def all_selections():
    for index in range(6):
        data,actors=enter();choose(data,index)
        button=('Shift_L','Control_L','z')[index%3]
        d.press(button,.2,3)
        s=d.status()
        d.check('barrel exits as character '+str(index),s['character']==index and s['player']['actor']==index+2 and s['player']['state']!=0x42,{'button':button,'status':s})
        cleanup()

def flag_base():
    file=d.mem(0x807467C8,'u8')
    slots=[d.mem(0x807EDEA8+i,'u8') for i in range(4)]
    count=d.mem(0x807ECEA0,'u16')
    size=((((count+0x6B7)&~63)+0x27)&~7)//8
    return 0x807ECEA8+slots.index(file)*size

def locked():
    d.press('d',wait=1) # Krusha -> DK.
    base=flag_base(); original={}
    for flag in (6,70,66,117):
        a=base+flag//8;original[a]=d.mem(a,'u8')
    changed=original.copy()
    for flag in (6,70,66,117):changed[base+flag//8]&=~(1<<(flag&7))
    speed=d.mem(0x8074452C,'u8')
    d.cmd(tap='p',wait=0)
    d.cmd(write=[{'address':a,'type':'u8','value':v} for a,v in changed.items()]+[{'address':0x8074452C,'type':'u8','value':0}])
    d.cmd(tap='p',wait=.2)
    try:
        data,actors=enter()
        models=[a for a in actors if a['type'] in (316,317)]
        ids=[d.mem(d.mem(int(a['pointer'],16)+0x174),'u16') for a in models if a['type']==316]
        d.check('locked Kongs retain four question marks; Krusha remains unlocked',len(models)==6 and sorted(ids)==[2,7],{'unlocked':ids,'locked':sum(a['type']==317 for a in models)})
        # Native barrels auto-scroll past locked question-mark slots. Wait for
        # all four transitions instead of trying to hold a cursor on one.
        d.press('Right',.2,4)
        d.check('barrel skips the four locked slots and reaches Krusha',d.mem(data+6,'u8')==5 and d.status()['character']==0 and d.status()['player']['state']==0x42,{'cursor':d.mem(data+6,'u8'),'status':d.status()})
        d.press('Right',.2,1.3)
        d.check('unlocked barrel cursor wraps Krusha to DK',d.mem(data+6,'u8')==0)
        d.press('Left',.2,1.3);d.press('Shift_L',.2,3)
        d.check('Krusha selectable in barrel with speed mode off and others locked',d.status()['character']==5,d.status())
        cleanup()
    finally:
        d.cmd(tap='p',wait=0)
        d.cmd(write=[{'address':a,'type':'u8','value':v} for a,v in original.items()]+[{'address':0x8074452C,'type':'u8','value':speed}])
        d.cmd(tap='p',wait=.2)
    # Persist restored native progress through DK's ordinary save path before
    # loading another map; these unlock edits belong only to this test fixture.
    d.press('d',wait=1)
    data,actors=enter();d.press('Shift_L',.2,3);cleanup()
    d.press('a',wait=1)

def second_map():
    d.go(7)
    # Setup actor 98 at (1642.88,315.23,1519.13) is created on approach,
    # rather than immediately when the level loads.
    d.place([1643,280,1479],0,wait=2)
    bars=[a for a in scene('japes-barrels') if a['type'] in (98,136,137)]
    d.check('Japes native barrel exists',bool(bars),bars)
    b=bars[0];x,y,z=b['xyz']
    data,actors=enter((x,y-30,z-40))
    d.check('Japes barrel has six character previews',sum(a['type'] in (316,317) for a in actors)==6)
    choose(data,5);d.press('Shift_L',.2,3)
    d.check('Japes barrel selects Krusha safely',d.status()['map']==7 and d.status()['character']==5,d.status())
    d.go(34);d.place([2780,500,2260],2048,wait=1)
    d.checkpoint(5,'six-barrel-ready-to-play')

try:
    d.start();d.press('0',.1,.1);d.press('F7',.1,2)
    animation();all_selections();locked();second_map()
    d.results['complete']=True
    (d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
    print('BARREL_EXTRA_CHECKS_COMPLETE; interactive controller ready',flush=True)
except Exception as exc:
    d.results['error']=str(exc)
    (d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
    print(json.dumps({'test_error':str(exc)}),flush=True)
    try:d.cmd(shot='barrel-extra-failure')
    except Exception:pass
    print('INTERACTIVE_CONTROLLER_READY',flush=True)
d.interactive()
