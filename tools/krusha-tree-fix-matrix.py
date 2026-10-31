#!/usr/bin/python3
"""Frame-stepped tree-tag matrix and normal airborne-tag controls.
Cold boots create exact-ROM states. Native options select widescreen/ON/OFF.
Fixtures change positions only, never identity, action, animation, or code.
"""
from pathlib import Path
import os,json,importlib.util,math,struct
ROOT=Path(__file__).resolve().parent.parent
s=importlib.util.spec_from_file_location('d',ROOT/'tools/krusha-test.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
# Read the exact build's getter, so repeated cold boots preserve the requested
# native ON/OFF state instead of blindly toggling an EEPROM-persisted setting.
symbols={row[1]:int(row[0],16) for row in (line.split() for line in d.ROM.with_suffix('.sym').read_text().splitlines()) if len(row)>=2}
lui,jr,lw=struct.unpack_from('>III',d.ROM.read_bytes(),0x1FED020+symbols['krushaenabled']-0x805DAE00)
assert lui>>16==0x3C02 and jr==0x03E00008 and lw>>16==0x8C42
ENABLED=((lui&0xFFFF)<<16)+struct.unpack('>h',struct.pack('>H',lw&0xFFFF))[0]
OUT=Path(os.environ['DK64_MATRIX_OUT']);OUT.mkdir(parents=True,exist_ok=True);d.REPORT_NAME='tree-fix-matrix.json';d.results={'rom_sha256':d.DIGEST,'fixtures':__doc__,'checks':[],'cases':[]}
def step(n=1):
 for _ in range(n):d.press('slash',.025,.025)
def select(target):
 for _ in range(12):
  if d.status()['character']==target:return
  d.press('d',.07,.35)
 raise AssertionError('cannot select source '+str(target))
def read(a,t='u32'):return d.mem(a,t)
def boot(mode,off=False):
 d.start();d.cmd(down=['f'])
 for _ in range(60):
  if d.status()['map']==80:break
  d.press('Return',.2,.6)
 d.cmd(up=['f'],wait=1)
 a=next(a for a in d.scene('tree-options')['actors'] if a['type']==326);data=read(int(a['pointer'],16)+0x174)
 # Map 80 exists before the native Start screen has opened the carousel.
 # Wait for actual menu readiness; a wall-clock delay can miss that input.
 for _ in range(80):
  page=read(data+0x12,'u8')
  if page==1 and read(0x800337F0,'u8')==1:break
  if page==0:d.press('Return',.12,.3)
  else:d.cmd(wait=.3)
 d.check('native menu carousel ready',read(data+0x12,'u8')==1 and read(0x800337F0,'u8')==1)
 if mode or off:
  for _ in range(30):
   selected=read(data+0x17,'u8');ready=read(0x800337F0,'u8')==1
   if selected==4 and ready:break
   if selected!=4 and ready:d.press('Left',.15,.5)
   else:d.cmd(wait=.3)
  d.check('native Other Options carousel selected',read(data+0x17,'u8')==4)

  for _ in range(6):
   d.press('Shift_L',.3,2)
   if read(data+0x12,'u8')==9:break
  d.check('native options reached',read(data+0x12,'u8')==9)
  if read(0x807444C0,'u8')!=mode:d.press('Up',.2,1)
  if off:
   for _ in range(4):d.press('Right',.2,.5)
   if read(ENABLED):d.press('Up',.2,1)
  d.press('Control_L',.2,2);d.press('Right',.2,1)
 for _ in range(12):
  d.press('Shift_L',.3,1.5)
  if d.status()['map']==34:break
 d.cmd(wait=3);d.check('cold-boot mode '+str((mode,off)),d.status()['map']==34 and read(0x807444C0,'u8')==mode)
 d.check('native Krusha option '+str((mode,off)),read(ENABLED)==int(not off))
 d.place([2940,500,2220],0,wait=1);d.checkpoint(8,'matrix-isles-'+str((mode,off)))
 d.go(7);d.place([1000,280,750],0,wait=1);d.cmd(wait=4);d.checkpoint(9,'matrix-tree-'+str((mode,off)))
def load(slot):d.press(str(slot),.07,.05);d.press('F7',.07,.7)
def grab_case(mode,source,key,n,off):
 load(9);select(source);d.place([910,280,835],0,wait=.4);d.press('c',.35,.1);d.cmd(tap='p',wait=0);d.cmd(down=['Up','Shift_L'],wait=0);step(n)
 before=d.status();d.cmd(down=[key],wait=0);step();d.cmd(up=[key],wait=0);step(3);d.cmd(up=['Up','Shift_L'],wait=0);step(6);after=d.status()
 ok=after['map']==7 and abs(after['player']['x']-910)<150 and abs(after['player']['z']-835)<150 and after['player']['actor']==after['character']+2
 if source==5 and key=='d' and n==5:d.cmd(shot='tree-fixed-mode-'+str(mode),scene='tree-fixed-mode-'+str(mode))
 row={'mode':mode,'off':off,'source':source,'key':key,'delay_frames':n,'before':before,'after':after};d.results['cases'].append(row);d.check('tree retains valid attachment '+str((mode,off,source,key,n)),ok,after)
 # Existing policy blocks tags once actually climbing. Climbing itself must
 # continue and jumping off must restore ordinary controls.
 if after['player']['state']==89:
  char=after['character'];d.cmd(down=['d'],wait=0);step(2);d.cmd(up=['d'],wait=0);d.check('tag denied while climbing '+str((mode,off,source,key,n)),d.status()['character']==char)
  d.cmd(down=['Up'],wait=0);y=d.status()['player']['y'];step(6);d.cmd(up=['Up'],wait=0)
  d.check('climbing still moves '+str((mode,off,source,key,n)),d.status()['player']['y']!=y)
  d.cmd(down=['Shift_L'],wait=0);step(2);d.cmd(up=['Shift_L'],wait=0);step(10);d.check('jump off still works '+str((mode,off,source,key,n)),d.status()['player']['state']!=89)
 d.cmd(tap='p',wait=.1)
def airborne(mode,source,key,count):
 load(8);select(source);d.place([2940,500,2220],0,wait=.4);d.cmd(tap='p',wait=0);d.cmd(down=['Shift_L'],wait=0);step(4);d.cmd(up=['Shift_L'],wait=0);d.cmd(down=[key],wait=0);step();d.cmd(up=[key],wait=0);step(2)
 s=d.status();paad=read(int(s['player_pointer'],16)+0x174)
 d.check('regrab cooldown expires after tag '+str((mode,count,source,key)),read(paad+0x100)==0)
 expected=(source+(1 if key=='d' else -1))%count
 d.check('normal airborne tag remains available '+str((mode,count,source,key)),s['character']==expected and s['player']['actor']==expected+2,s);d.cmd(tap='p',wait=.1)
def stop():
 if d.proc and d.proc.poll() is None:d.proc.stdin.write('{"quit":true}\n');d.proc.stdin.flush();d.proc.wait(timeout=20)
try:
 for mode,off in ([(0,True),(1,True)] if os.environ.get('DK64_MATRIX_OFF_ONLY')=='1' else [(0,False),(1,False),(0,True)]):
  boot(mode,off);count=5 if off else 6
  for source in range(count):
   for key in ['a','d']:
    airborne(mode,source,key,count)
    for n in ([3,5] if off else [3,5,7]):grab_case(mode,source,key,n,off)
  stop()
 d.results['complete']=True
except Exception as e:
 d.results['error']=repr(e);print('TREE_MATRIX_ERROR',repr(e),flush=True)
 try:d.cmd(shot='tree-matrix-failure',scene='tree-matrix-failure')
 except Exception:pass
finally:
 stop();(OUT/'checks.json').write_text(json.dumps(d.results,indent=2)+'\n');print('TREE_MATRIX_COMPLETE',d.results.get('complete'),flush=True)
