#!/usr/bin/python3
"""Native options UI, EEPROM persistence, five/six-character controller tests."""
import importlib.util
import json
import struct
import os
from pathlib import Path

spec=importlib.util.spec_from_file_location('driver',Path(__file__).with_name('krusha-test.py'))
d=importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
d.REPORT_NAME='krusha-options-tests.json'
d.results={'rom_sha256':d.DIGEST,'fixtures':'No state loads or option writes; cold boots and controller input. Position fixture only for final ready checkpoint.','checks':[]}

# Resolve the read-only diagnostic variable from GCC's three-instruction getter.
symbols={row[1]:int(row[0],16) for row in (line.split() for line in d.ROM.with_suffix('.sym').read_text().splitlines()) if len(row)>=2}
offset=0x1FED020+symbols['krushaenabled']-0x805DAE00
lui,jr,lw=struct.unpack_from('>III',d.ROM.read_bytes(),offset)
assert lui>>16==0x3C02 and jr==0x03E00008 and lw>>16==0x8C42
ENABLED=((lui&0xFFFF)<<16)+struct.unpack('>h',struct.pack('>H',lw&0xFFFF))[0]

def main_menu():
    # Ordinary speed keeps Start edges out of accelerated demo transitions.
    for i in range(120):
        if d.status()['map']==80: break
        d.press('Return',.3,.8)
    d.check('cold boot main menu',d.status()['map']==80,d.status())
    d.cmd(wait=8)

def options():
    # From default Adventure, one left reaches the Other Options barrel.
    menu=next(a for a in d.scene('v2-options-controller')['actors'] if a['type']==326)
    data=d.mem(int(menu['pointer'],16)+0x174)
    # A boot Start press can carry into Adventure/file selection. Use native
    # B to return to root page 1, then select Other Options (root item 4).
    for _ in range(8):
        if d.mem(data+0x12,'u8')==1:break
        d.press('Shift_L' if d.mem(data+0x12,'u8')==0 else 'Control_L',.4,2)
    for _ in range(12):
        if d.mem(data+0x17,'u8')==4 and d.mem(data,'f32')==0 and d.mem(data+4,'f32')==0:break
        d.press('Left',.35,1.5)
    for i in range(6):
        d.press('Shift_L',.5,2)
        if d.mem(data+0x12,'u8')==9:break
    d.cmd(wait=1)
    if os.environ.get('DK64_OPTIONS_WIDE')=='1' and not d.mem(0x807444C0,'u8'):
        d.press('Up',.2,1)
    for i in range(4): d.press('Right',.2,1)
    page=d.mem(data+0x12,'u8'); selected=d.mem(data+0x17,'u8')
    d.check('native options menu contains selectable fifth Krusha item',page==9 and selected==4 and d.mem(0x800338FC,'u8')==5,{'page':page,'selected':selected})

def unchanged_settings():
    return [d.mem(a,'u8') for a in (0x807444C0,0x8074452C,0x80744530)]

def toggle(expected,key='Up',hold=.2):
    before=unchanged_settings()
    d.press(key,hold,1,shot='v2-option-'+('on' if expected else 'off'))
    actual=d.mem(ENABLED)
    d.check('UI toggles Krusha '+('on' if expected else 'off'),actual==expected,actual)
    d.check('Krusha toggle preserves screen size, Speed Mode and camera setting',unchanged_settings()==before,before)

def adventure():
    d.press('Control_L',.2,2)
    d.press('Right',.2,1) # Other Options -> Adventure
    for i in range(10):
        d.press('Shift_L',.3,1.5)
        if d.status()['map']==34: break
    d.cmd(wait=3)
    for _ in range(120):
        s=d.status()
        if s['map']==34 and s['frame']>180 and s['player']['state']==12 and not d.mem(0x807463B8,'u8') and not d.mem(0x807444EC,'u8'):break
        d.cmd(wait=.25)
    d.check('enter adventure through native menu',d.status()['map']==34 and d.status()['character']==0,d.status())

def rotation(enabled):
    for key,expected in [('d',list(range(1,6 if enabled else 5))+[0]),
                         ('a',list(range(5 if enabled else 4,-1,-1)))]:
        seen=[]
        for kong in expected:
            d.press(key,.2,.7); seen.append(d.status()['character'])
        d.check(('six' if enabled else 'five')+' character rotation with option '+('on' if enabled else 'off')+' '+key,seen==expected,seen)

def restart():
    d.proc.stdin.write('{"quit":true}\n'); d.proc.stdin.flush()
    d.proc.wait(timeout=15)
    d.start(); main_menu()

def barrel(enabled):
    if os.environ.get('DK64_BARREL_PORTRAIT_REVIEW') == '1':
        # The exterior model/face assets live in table 27 only with Krusha ON.
        # This is a read-only check of native loading, not a model/option write.
        loaded = d.mem(0x807F9528 + 27*4)
        d.check('exterior asset table loaded only with Krusha ON '+str(enabled),
                bool(loaded) == bool(enabled), hex(loaded))
        d.place([2773,500,2260],0,wait=1)
        d.press('c',.7,.2,shot='portrait-option-'+('on' if enabled else 'off')+'-outside')
        if enabled:
            d.checkpoint(0,'six-face-approved-rom-dk-isles')
    d.place([2773,500,2320],0,wait=1)
    d.press('c',.7,.2)
    d.cmd(keys=['Up','Shift_L'],seconds=.4,wait=1.5)
    s=d.scene('option-'+('on' if enabled else 'off')+'-barrel')
    models=[a for a in s['actors'] if a['type'] in (316,317)]
    identities=[d.mem(d.mem(int(a['pointer'],16)+0x174),'u16') for a in models if a['type']==316]
    expected=list(range(2,8 if enabled else 7))
    d.check('barrel shows '+str(len(expected))+' characters with option '+str(enabled),len(models)==len(expected) and sorted(identities)==expected,identities)
    b=next(a for a in s['actors'] if a['type'] in (98,136,137) and a['state']==1)
    data=d.mem(int(b['pointer'],16)+0x174)
    seen=[]
    for i in range(len(expected)):
        d.press('Right',.2,1.1);seen.append(d.mem(data+6,'u8'))
    d.check('barrel cursor wraps with option '+str(enabled),seen==list(range(1,len(expected)))+[0],seen)
    d.press('Left',.2,1.3,shot='barrel-option-'+('on-six-characters' if enabled else 'off-five-characters'))
    d.press('Shift_L',.2,3)
    d.check('barrel last slot selects '+('Krusha' if enabled else 'Chunky'),d.status()['character']==(5 if enabled else 4),d.status())
    d.place([2780,500,2260],2048,wait=1)
    remaining=[a for a in d.scene('barrel-option-cleanup')['actors'] if a['type'] in (316,317)]
    d.check('barrel cleanup with option '+str(enabled),not remaining,remaining)
    d.press('d',wait=1)

try:
    d.start()
    if os.environ.get('DK64_BARREL_PORTRAIT_REVIEW') == '1':
        d.cmd(shot='portrait-startup')
    main_menu(); options()
    if not d.mem(ENABLED): toggle(1)
    toggle(0,hold=1.2) # Held stick changes setting once, not once each frame.
    restart(); options()
    d.check('OFF survives full emulator restart and native EEPROM reload',d.mem(ENABLED)==0,d.mem(ENABLED))
    d.cmd(shot='v2-option-off-after-restart')
    adventure(); rotation(False); barrel(False)
    restart(); options(); toggle(1,key='Down')
    adventure(); rotation(True); barrel(True)
    d.place([2780,500,2260],2048,wait=1)
    d.press('a',wait=1)
    p=int(d.status()['player_pointer'],16)
    d.check('ready checkpoint has unarmed Krusha in adventure',d.status()['character']==5 and d.status()['player']['state']==12 and d.mem(p+0x20C,'u8')==0 and d.mem(p+0x146,'u16')&3==2,d.status())
    d.checkpoint(5,'krusha-v2-ready-to-play')
    restart(); options()
    d.check('ON survives full emulator restart and native EEPROM reload',d.mem(ENABLED)==1,d.mem(ENABLED))
    d.cmd(shot='v2-option-on-after-restart')
    d.results['complete']=True
    (d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
    print('OPTIONS_CHECKS_COMPLETE; interactive controller ready',flush=True)
except Exception as exc:
    d.results['error']=str(exc)
    (d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
    print(json.dumps({'test_error':str(exc)}),flush=True)
    try:d.cmd(shot='options-test-failure')
    except Exception:pass
    print('INTERACTIVE_CONTROLLER_READY',flush=True)
d.interactive()
