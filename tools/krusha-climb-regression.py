#!/usr/bin/python3
"""Frame-step native vine grabs around a tag, then swing and jump off.
Requires same-ROM slot 8; position/loading fixtures only. No action/ID writes.
"""
from pathlib import Path
import importlib.util,json,os
ROOT=Path(__file__).resolve().parent.parent;s=importlib.util.spec_from_file_location('d',ROOT/'tools/krusha-test.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
d.REPORT_NAME='climb-regression.json';d.results={'rom_sha256':d.DIGEST,'fixtures':__doc__,'checks':[],'cases':[]}
def step(n=1):
 for _ in range(n):d.press('slash',.025,.025)
def load(n):d.press(str(n),.07,.05);d.press('F7',.07,.7)
def select(k):
 for _ in range(6):
  if d.status()['character']==k:return
  d.press('d',.07,.35)
 raise AssertionError('source selection failed')
try:
 d.start();load(8);d.place([2940,500,2220],0,wait=.3);d.go(7);d.cmd(wait=4);d.place([1000,280,750],0,wait=.5);d.checkpoint(9,'climb-japes-baseline')
 for source in [0,5]:
  for key in ['a','d']:
   for delay in [0,2]:
    label=str((source,key,delay));load(9);select(source);d.cmd(tap='p',wait=0);d.cmd(position=[929,510,780],facing=0,wait=0);step(delay)
    before=d.status();d.cmd(down=[key],wait=0);step();d.cmd(up=[key],wait=0);step(8);after=d.status();d.results['cases'].append({'source':source,'key':key,'delay':delay,'before':before,'after':after})
    p=after['player'];d.check('valid native vine attachment '+label,after['map']==7 and p['state']==0x57 and abs(p['x']-929)<150 and abs(p['z']-795)<150 and p['actor']==after['character']+2,after)
    if source==5 and key=='d' and delay==0:d.cmd(shot='vine-fixed',scene='vine-fixed')
    selected=after['character'];d.cmd(down=['d'],wait=0);step(2);d.cmd(up=['d'],wait=0);d.check('tag remains denied while on vine '+label,d.status()['character']==selected)
    d.cmd(down=['Up'],wait=0);step(6);d.cmd(up=['Up'],wait=0);d.check('vine remains stable during swing input '+label,d.status()['player']['state']==0x57,d.status())
    d.cmd(down=['Shift_L'],wait=0);step(2);d.cmd(up=['Shift_L'],wait=0);step(6);d.check('jump off vine works '+label,d.status()['player']['state']!=0x57,d.status());d.cmd(tap='p',wait=.1)
 d.results['complete']=True
except Exception as e:d.results['error']=repr(e);print('CLIMB_ERROR',repr(e),flush=True)
finally:
 (d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
 if d.proc and d.proc.poll() is None:d.proc.stdin.write('{"quit":true}\n');d.proc.stdin.flush();d.proc.wait(timeout=20)
 print('CLIMB_COMPLETE',d.results.get('complete'),flush=True)
