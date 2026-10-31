#!/usr/bin/python3
"""Check cooldown reset across a real map load and create the fresh enemy fixture."""
import importlib.util,json
from pathlib import Path
s=importlib.util.spec_from_file_location('driver',Path(__file__).with_name('krusha-test.py'));d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
d.REPORT_NAME='krusha-roar-transition-tests.json';d.results={'rom_sha256':d.DIGEST,'fixtures':'Exact-build slot 1; position and native loading-zone redirect; no identity/state/animation/code writes','checks':[]}
def roar():
 d.cmd(down=['z'],wait=.15);d.press('i',.08,.6);d.cmd(up=['z'],wait=.15)
try:
 d.start();d.press('1',.1,.1);d.press('F7',.1,2)
 d.place([2780,500,2260],2048,wait=1);roar();d.cmd(wait=6)
 previous=d.status()['frame'];d.go(7);d.place([1072,281,540],0,wait=1)
 d.check('map frame counter resets below previous roar completion',d.status()['frame']<previous,[previous,d.status()['frame']])
 d.checkpoint(7,'roar-japes-before-attack')
 e=next(int(a['pointer'],16) for a in d.scene('roar-transition-enemy')['actors'] if a['type']==178)
 before=d.status()['inventory'][3];roar()
 d.check('roar immediately available after map change',d.status()['player']['state']==103,d.status())
 d.check('new-map enemy receives native instrument death',d.mem(e+0x154,'u8')==22,d.mem(e+0x154,'u8'))
 d.check('new-map roar spends exactly once',d.status()['inventory'][3]==before-150,d.status())
 d.cmd(wait=6);d.check('new-map roar recovers safely',d.status()['player']['state']==12,d.status())
 d.press('5',.1,.1);d.press('F7',.1,2)
 d.results['complete']=True
 (d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
except Exception as e:
 d.results['error']=str(e);(d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n');print('TRANSITION_ERROR',str(e),flush=True)
print('TRANSITION_COMPLETE',flush=True)
if d.proc and d.proc.poll() is None:
 d.proc.stdin.write('{"quit":true}\n');d.proc.stdin.flush();d.proc.wait(timeout=15)
