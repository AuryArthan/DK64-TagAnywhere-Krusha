#!/usr/bin/python3
"""Restart/checkpoint, orange, fairy-photo and locked-Kong integration checks."""
import importlib.util
import json
import math
from pathlib import Path

spec = importlib.util.spec_from_file_location('driver', Path(__file__).with_name('krusha-test.py'))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
d.REPORT_NAME = 'krusha-extra-tests.json'
d.results = {'rom_sha256':d.DIGEST, 'cold_boot':False, 'restart_then_native_state_load':True,
             'fixtures':'Logged positions, loading zones and temporary unlock flag setup; no character ID or move-code writes',
             'checks':[]}

def flag_base():
    file_id = d.mem(0x807467C8, 'u8')
    slots = [d.mem(0x807EDEA8+i, 'u8') for i in range(4)]
    slot = slots.index(file_id)
    count = d.mem(0x807ECEA0, 'u16')
    size = ((((count+0x6B7)&~63)+0x27)&~7)//8
    return 0x807ECEA8 + slot*size

def fairy_photo():
    d.place([564, 270, 2800], wait=2)
    d.press('c', .7, .2)
    d.combo('k', wait=.8)
    s = d.status()
    for attempt in range(2):
        if s['player']['state'] in (4,5): break
        # A dive/landing transition may consume the first camera input.
        d.cmd(wait=1)
        d.combo('k', wait=1)
        s = d.status()
    d.check('fairy camera near Japes fairy', s['player']['state'] in (4,5), s)
    d.wait_frames(40)
    actors = d.scene('fairy-before-photo')['actors']
    fairies = [a for a in actors if a['type']==248]
    d.check('native fairy present', bool(fairies), fairies)
    fairy = int(fairies[0]['pointer'],16)
    player = int(s['player_pointer'],16)
    paad = d.mem(player+0x174)
    changes = d.mem(0x807FC924)
    base = flag_base()
    addr = base + 0x24D//8
    flag_before = d.mem(addr,'u8')
    d.check('fairy not already captured', not flag_before & (1 << (0x24D & 7)), flag_before)
    # Position the live fairy in the lens. The game still performs its own
    # targeting and photo action; neither its targeting byte nor flags are set.
    targeted = False
    d.cmd(tap='p',wait=.02)
    for attempt in range(5):
        eye = [d.mem(changes+0x210+i*4,'f32') for i in range(3)]
        at = [d.mem(changes+0x228+i*4,'f32') for i in range(3)]
        vector = [at[i]-eye[i] for i in range(3)]
        length = math.sqrt(sum(v*v for v in vector))
        # Stay in front of the camera's native depth/occlusion limit.
        target = [eye[i]+vector[i]/length*40 for i in range(3)]
        target[1] -= 10
        writes = []
        for start in (0x7C,0x88):
            writes += [{'address':fairy+start+i*4,'type':'f32','value':target[i]} for i in range(3)]
        writes.append({'address':fairy+0xB8,'type':'f32','value':0})
        d.cmd(write=writes,wait=.05)
        d.cmd(tap='p',wait=0)
        d.cmd(tap='p',wait=0)
        if d.mem(paad+0x1EC,'u8')==1:
            targeted=True;break
    d.check('native camera targets fairy', targeted, {'result':d.mem(paad+0x1EC,'u8')})
    d.cmd(shot='final-fairy-in-frame')
    film = d.status()['inventory'][4]
    # Native shutter takes several frames before freezing the target result.
    # Keep this position fixture in the lens over that interval; a single
    # teleport can drift out again before the shutter and only tests a miss.
    d.cmd(down=['Control_L'],wait=0)
    for shutter_frame in range(48):
        d.cmd(write=writes,wait=0)
        d.cmd(tap='slash',wait=.03)
        if d.mem(addr,'u8') & (1 << (0x24D & 7)): break
    d.cmd(up=['Control_L'],tap='p',wait=1,shot='final-fairy-captured')
    after = d.mem(addr,'u8')
    state = d.mem(fairy+0x154,'u8')
    d.check('fairy photo earns native shared capture flag', bool(after & (1 << (0x24D & 7))) and state==0x40,
            {'before':flag_before,'after':after,'fairy_state':state,'status':d.status()})
    # A successful first photo starts the native refill/tutorial sequence;
    # it may need ordinary A input before returning control.
    for attempt in range(30):
        if d.status()['player']['state'] in (12,13,0x4E,0x4F): break
        d.cmd(wait=.5)
        if d.status()['player']['state'] in (4,5): d.press('i',wait=.5)
        else: d.press('Shift_L',.15,.5)
    d.check('camera returns safely after fairy photo', d.status()['player']['state'] in (12,13,0x4E,0x4F),d.status())
    d.checkpoint(7,'krusha-build-fairy-photo')

def locked_kongs():
    d.place([910,280,800], wait=2)
    base = flag_base()
    original = {}
    writes = []
    for flag in (6,70,66,117):
        address = base + flag//8
        if address not in original: original[address]=d.mem(address,'u8')
    modified=original.copy()
    for flag in (6,70,66,117):
        address=base+flag//8
        modified[address] &= ~(1 << (flag & 7))
    story = d.mem(0x8074452C,'u8')
    d.cmd(tap='p',wait=.05)
    for address,value in modified.items():
        writes.append({'address':address,'type':'u8','value':value})
    writes.append({'address':0x8074452C,'type':'u8','value':0})
    d.cmd(write=writes)
    d.cmd(tap='p',wait=.2)
    try:
        # Start as Krusha: forward goes DK; forward/backward then skip four
        # genuinely locked native unlock flags and still reach Krusha.
        seen=[]
        for key in ('d','d','a','a'):
            d.press(key,wait=.8)
            seen.append(d.status()['character'])
        d.check('Krusha always available with other Kongs locked and speed mode off', seen==[0,5,0,5],seen)
    finally:
        d.cmd(tap='p',wait=.05)
        writes=[{'address':a,'type':'u8','value':v} for a,v in original.items()]
        writes.append({'address':0x8074452C,'type':'u8','value':story})
        d.cmd(write=writes)
        d.cmd(tap='p',wait=.2)

if __name__ == '__main__':
    try:
        d.start()
        d.press('3',.1,.1)
        d.press('F7',.1,2)
        s=d.status()
        d.check('native checkpoint reloads after emulator restart',s['map']==7 and s['character']==5 and s['player']['actor']==7,s)
        d.place([1145,288,1940],wait=2)
        d.cmd(record='krusha-gameplay-demo')
        oranges=d.status()['inventory'][2]
        d.combo('l',wait=1,shot='final-orange-throw')
        d.check('Krusha throws orange',d.status()['inventory'][2]==oranges-1,d.status())
        d.press('Up',.5,.1)
        d.cmd(keys=['Up','Shift_L'],seconds=.3,wait=.4,shot='final-extra-jump')
        d.cmd(stop_record=True)
        d.cmd(wait=1)
        fairy_photo()
        locked_kongs()
        d.go(34)
        d.place([2780,500,2260],wait=2)
        d.checkpoint(5,'krusha-build-ready-to-play')
        d.results['complete']=True
        (d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
        print('EXTRA_CHECKS_COMPLETE; interactive controller ready',flush=True)
    except Exception as exc:
        d.results['error']=str(exc)
        (d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
        print(json.dumps({'test_error':str(exc)}),flush=True)
        try:d.cmd(shot='extra-test-failure')
        except Exception:pass
        print('INTERACTIVE_CONTROLLER_READY',flush=True)
    d.interactive()
