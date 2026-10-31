#!/usr/bin/python3
from pathlib import Path
import importlib.util,json,os
ROOT=Path(__file__).resolve().parent.parent;s=importlib.util.spec_from_file_location('d',ROOT/'tools/krusha-test.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
OUT=Path(os.environ['DK64_TREE_OUT']);OUT.mkdir(parents=True,exist_ok=True);rows=[]
def snap():
 s=d.status();p=int(s['player_pointer'],16);data=d.mem(p+0x174);swap=d.mem(0x807FC924)
 fields=[(swap+0x29c,'u16'),(p+0x36f,'u8'),(p+0x6a,'u16')]+[(data+i,'u32') for i in range(0x130,0x160,4)]
 s['contact']=d.cmd(read=[{'address':a,'type':t} for a,t in fields],wait=0)[0]['memory'];return s
def step(n=1):
 for _ in range(n):d.press('slash',.025,.025)
try:
 d.start()
 if os.environ.get('DK64_TREE_BOOT')=='1':
  d.cmd(down=['f'])
  for _ in range(60):
   if d.status()['map']==80:break
   d.press('Return',.2,.6)
  d.cmd(up=['f'],wait=7)
  for _ in range(12):
   d.press('Shift_L',.3,1.5)
   if d.status()['map']==34:break
  d.cmd(wait=3);d.place([2940,500,2220],0,wait=.5);d.checkpoint(8,'tree-fix-native-dk-standard')
 for count in range(9):
  d.press('8',.1,.1);d.press('F7',.1,1);d.press('a',.15,.6);d.place([2940,500,2220],0,wait=.5);d.go(7);d.place([910,280,835],0,wait=.5);d.press('c',.4,.1);d.cmd(tap='p',wait=0)
  row={'delay_frames':count,'samples':[]};d.cmd(down=['Up','Shift_L'],wait=0)
  for i in range(count):step();row['samples'].append(snap())
  row['before_tag']=snap();d.cmd(down=['d'],wait=0);step();d.cmd(up=['d'],wait=0);row['samples'].append(snap());step(3);d.cmd(up=['Up','Shift_L'],wait=0);step(4);row['after']=snap();rows.append(row);print(json.dumps({'delay':count,'before':row['before_tag'],'after':row['after']}),flush=True);d.cmd(tap='p',wait=.1)
except Exception as e:print('TRACE_ERROR',repr(e),flush=True)
finally:
 (OUT/'trace.json').write_text(json.dumps({'rom_sha256':d.DIGEST,'rows':rows},indent=2)+'\n')
 if d.proc and d.proc.poll() is None:d.proc.stdin.write('{"quit":true}\n');d.proc.stdin.flush();d.proc.wait(timeout=20)
