#!/usr/bin/python3
"""Trace shout timing after native idle/running/crouch input.
Only controller input and player-position fixtures; no animation/speed/code writes.
Reference uses exact-v0.3 states; changed ROMs create their own cold-boot states.
"""
import importlib.util,json,os
from pathlib import Path
s=importlib.util.spec_from_file_location('d',Path(__file__).with_name('krusha-test.py'));d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
runtime=Path(os.environ.get('DK64_RUNTIME',d.RUN));(runtime/'saves').mkdir(parents=True,exist_ok=True)
if not (runtime/'saves'/d.save.name).exists():(runtime/'saves'/d.save.name).write_bytes(d.save.read_bytes())
clean_eeprom=(runtime/'saves'/d.save.name).read_bytes()
REF=os.environ.get('DK64_TIMING_REFERENCE')=='1';OUT=Path(os.environ['DK64_REVIEW_OUT']);OUT.mkdir(exist_ok=True)
report={'rom_sha256':d.DIGEST,'reference':REF,'fixtures':__doc__,'cases':[],'checks':[]}
def read(fields):return d.cmd(read=[{'address':a,'type':t} for a,t in fields],wait=0)[0]['memory']
def snap():
 p,frame=read([(0x807FBB4C,'u32'),(0x8076A064,'u32')]);a=read([(p+4,'u32')])[0];c=read([(a,'u32')])[0]
 v=read([(p+0x154,'u8'),(c+0x10,'u16'),(c+4,'f32'),(c+0x24,'f32')]+[(a+o,'f32') for o in (0x48,0x4C,0x50,0x54,0x58)]+[(0x807FCC46,'u16'),(0x807FBB60,'u32')])
 return dict(zip(('tick','state','clip','pose','channel_speed','actor_speed','blend_from','blend_target','blend_time','blend_duration','crystals','scene_flags'),[frame]+v))
def step(n=1):
 for _ in range(n):d.press('slash',.025,.025)
def check(name,ok,detail=None):
 report['checks'].append({'name':name,'passed':bool(ok),'detail':detail});print(json.dumps(report['checks'][-1]),flush=True)
 if not ok:raise AssertionError(name)
def boot(mode):
 d.start()
 if REF:
  d.press('5',.1,.1);d.press('F7',.1,2);return
 d.cmd(down=['f'])
 for _ in range(70):
  if d.status()['map']==80:break
  d.press('Return',.2,.6)
 d.cmd(up=['f'],wait=7)
 if mode:
  actor=next(a for a in d.scene('timing-menu')['actors'] if a['type']==326);data=read([(int(actor['pointer'],16)+0x174,'u32')])[0];d.press('Left',.2,3)
  for _ in range(6):
   d.press('Shift_L',.3,2)
   if read([(data+0x12,'u8')])[0]==9:break
  check('native screen option reached',read([(data+0x12,'u8')])[0]==9)
  if not read([(0x807444C0,'u8')])[0]:d.press('Up',.2,1)
  d.press('Control_L',.2,2);d.press('Right',.2,1)
 for _ in range(12):
  d.press('Shift_L',.3,1.5)
  if d.status()['map']==34:break
 d.cmd(wait=3);check('cold boot screen mode '+str(mode),d.status()['map']==34 and read([(0x807444C0,'u8')])[0]==mode)
 d.place([2940,500,2220],0,wait=1);d.checkpoint(0 if mode else 8,'timing-dk-'+str(mode));d.press('a',.2,1);check('native tag selects Krusha '+str(mode),d.status()['character']==5);d.checkpoint(5 if mode else 9,'timing-krusha-'+str(mode))
def stop():
 d.proc.stdin.write('{"quit":true}\n');d.proc.stdin.flush();d.proc.wait(timeout=20)
 (runtime/'saves'/d.save.name).write_bytes(clean_eeprom)
def case(mode,name,run,crouch,reset=True,xyz=(2940,500,2220),enemy=None):
 if reset:d.press(str(5 if mode or REF else 9),.1,.1);d.press('F7',.1,2)
 d.place(xyz,0,wait=.5);d.cmd(tap='p',wait=0)
 if not reset:step(20)
 if run:d.cmd(down=['Up'],wait=0);step(run)
 previous=snap()
 if crouch:d.cmd(down=['z'],up=['Up'],wait=0);step(crouch);d.cmd(down=['i'],wait=0)
 else:d.cmd(down=['z','i'],up=['Up'],wait=0)
 samples=[];start=None;enemy_state=None
 for n in range(240):
  step();v=snap()
  if v['state']==103:
   if start is None:start=v['tick'];d.cmd(up=['z','i','Up'],wait=0)
   samples.append(v)
   if enemy and v['tick']-start==10:enemy_state=read([(enemy+0x154,'u8')])[0]
  elif start is not None:break
  if start is None and n>20:break
 row={'wide':mode,'name':name,'previous':previous,'start_tick':start,'duration':v['tick']-start if start is not None else None,'samples':samples,'after':v,'enemy_state':enemy_state};report['cases'].append(row)
 
 if start is None:
  if not REF and crouch:check('expected crouch input starts '+str((mode,name)),False,row)
  check('simultaneous input safely declined '+str((mode,name)),v['crystals']==previous['crystals'],{'before':previous,'after':v});d.cmd(up=['z','i','Up'],wait=0);d.cmd(tap='p',wait=.1);return
 check('controller starts '+str((mode,name)),True,row['previous'])
 print('DURATION',mode,name,row['duration'],'actor rates',sorted(set(round(v['actor_speed'],4) for v in samples)),flush=True)
 if not REF:
  check('stable duration '+str((mode,name)),142<=row['duration']<=150,row['duration'])
  check('fixed effective speed '+str((mode,name)),all(abs(v['actor_speed']-.5)<.00001 and (abs(v['channel_speed']-1.2)<.00001 or (v['pose']>=109 and v['channel_speed']==0)) and v['blend_duration']==0 for v in samples),samples[:2])
  pairs=[(a,b) for a,b in zip(samples,samples[1:]) if b['tick']>a['tick']];rates=[(b['pose']-a['pose'])/(b['tick']-a['tick']) for a,b in pairs if a['pose']<108.5]
  check('continuous skeletal progression '+str((mode,name)),bool(rates) and all(abs(b['pose']-min(109,a['pose']+.6*(b['tick']-a['tick'])))<.002 for a,b in pairs),{'min':min(rates),'max':max(rates)})
  check('cost and recovery '+str((mode,name)),previous['crystals']-v['crystals']==150 and v['state']==12 and (previous['scene_flags']&0x10030)==(v['scene_flags']&0x10030),{'before':previous,'after':v})
 if enemy:check('nearby enemy receives native instrument death',enemy_state==22,enemy_state)
 d.cmd(tap='p',wait=.1)
d.check=check
try:
 for mode in ([1] if REF else [0,1]):
  boot(mode)
  for recipe in [('settled-crouch',0,8),('idle-instant',0,0),('idle-one-crouch-frame',0,1),('running-instant',35,0),('running-one-crouch-frame',35,1),('running-two-crouch-frames',35,2),('running-three-crouch-frames',35,3),('running-settled-crouch',35,8)]:case(mode,*recipe)
  if not REF and mode:
   for i in range(6):case(mode,'repeated-'+str(i+1),35 if i%2 else 0,[1,2,3][i%3],reset=(i==0))
   d.place([2940,500,2220],0,wait=.5);before=d.status();d.press('Down',.4,.1);after=d.status()
   check('running recovers after repeated screams',sum((after['player'][axis]-before['player'][axis])**2 for axis in ('x','z'))>25)
   d.press('Shift_L',.15,.1);check('jumping recovers after repeated screams',d.status()['player']['state']!=12);d.cmd(wait=2)
   d.combo('j',wait=.7);ammo=d.status()['inventory'][0];d.press('Control_L',.15,.3);check('bazooka fires after repeated screams',d.status()['inventory'][0]==ammo-1);d.cmd(wait=.5);d.combo('j',wait=.7)
   d.combo('k',wait=.7);check('camera opens after repeated screams',d.status()['player']['state']==4);d.press('i',.1,1);check('camera closes after repeated screams',d.status()['player']['state']==12)
   d.press('d',.2,1);check('tagging away after screams',d.status()['character']==0);d.combo('i',wait=.8);check('DK retains native instrument',d.status()['player']['state']==103);d.press('f',5,1);check('DK native instrument recovery',d.status()['player']['state']==12);d.press('a',.2,1)
   d.press('5',.1,.1);d.press('F7',.1,2);d.checkpoint(1,'timing-krusha-isles')
   d.go(7);d.place([1072,281,540],0,wait=1);d.checkpoint(7,'timing-japes-before-attack')
   enemy=next(int(a['pointer'],16) for a in d.scene('timing-enemy')['actors'] if a['type']==178)
   case(mode,'Japes quick scream',0,1,reset=False,xyz=(1072,281,540),enemy=enemy)
   d.press('5',.1,.1);d.press('F7',.1,2)
  stop()
 report['complete']=True
except Exception as e:
 report['error']=repr(e);print('TIMING_ERROR',repr(e),flush=True)
 if d.proc and d.proc.poll() is None:stop()
finally:
 (OUT/('reference.json' if REF else 'corrected.json')).write_text(json.dumps(report,indent=2)+'\n')
 print('TIMING_TESTS_COMPLETE' if report.get('complete') else 'TIMING_TESTS_FAILED',flush=True)
