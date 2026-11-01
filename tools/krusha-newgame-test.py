#!/usr/bin/python3
"""Cold-boot blank EEPROM and try Krusha before native Kong/move unlocks."""
from pathlib import Path
import os,hashlib,importlib.util,json,time,struct
ROOT=Path(__file__).resolve().parent.parent;ROM=ROOT/'rom/dk64-krusha-dev.z64';RUN=Path(os.environ['DK64_NEWGAME_PROFILE']).resolve();os.environ['DK64_RUNTIME']=str(RUN)
os.environ.setdefault('DK64_RESOLUTION','320x240')
(RUN/'saves').mkdir(parents=True,exist_ok=True);save=RUN/'saves'/('Donkey Kong 64 (local build)-'+hashlib.md5(ROM.read_bytes()).hexdigest()[:8].upper()+'.eep')
# An erased EEPROM is 0xff. Native checksum validation initializes all files.
if save.exists():raise SystemExit('Choose a fresh new-game profile; preserve existing saves')
save.write_bytes(b'\xff'*2048)
s=importlib.util.spec_from_file_location('d',ROOT/'tools/krusha-test.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d);d.REPORT_NAME='collectibles-newgame-tests.json';d.results={'rom_sha256':d.DIGEST,'fixtures':__doc__,'checks':[],'observations':[]}
try:
 d.start();d.cmd(down=['f'])
 for _ in range(70):
  if d.status()['map']==80:break
  d.press('Return',.2,.6)
 d.cmd(up=['f'],wait=7);d.check('erased EEPROM initializes main menu',d.status()['map']==80)
 d.check('fresh game Speed Mode is off',d.mem(0x8074452C,'u8')==0)
 # Explicitly select the feature being tested through the native options UI.
 # No option RAM writes: KRUSHA OFF must remain a valid player preference.
 symbols={row[1]:int(row[0],16) for row in (line.split() for line in ROM.with_suffix('.sym').read_text().splitlines()) if len(row)>=2}
 offset=0x1fed020+symbols['krushaenabled']-0x805dae00
 lui,jr,lw=struct.unpack_from('>III',ROM.read_bytes(),offset)
 enabled=((lui&0xffff)<<16)+struct.unpack('>h',struct.pack('>H',lw&0xffff))[0]
 d.results['initial_krusha_enabled']=d.mem(enabled)
 if not d.mem(enabled):
  menu=next(a for a in d.scene('fresh-options')['actors'] if a['type']==326);data=d.mem(int(menu['pointer'],16)+0x174)
  d.press('Left',.2,3)
  for _ in range(6):
   d.press('Shift_L',.3,2)
   if d.mem(data+0x12,'u8')==9:break
  while d.mem(data+0x17,'u8')!=4:d.press('Right',.2,1)
  d.press('Up',.2,1);d.press('Control_L',.2,2);d.press('Right',.2,2)
 d.check('fresh test uses KRUSHA ON and Speed Mode OFF',d.mem(enabled)==1 and d.mem(0x8074452c,'u8')==0)

 for _ in range(12):
  d.press('Shift_L',.3,1)
  if d.status()['map']!=80:break
 d.cmd(down=['f'])
 for _ in range(600):
  s=d.status()
  if s['map'] in (171,176) and s.get('player',{}).get('state')==12 and d.mem(0x807444EC,'u8')==0:break
  if _%10==0:print('INTRO_PROGRESS',_,s,flush=True)
  d.press('Return',.15,.4)
 d.cmd(up=['f'],wait=1)
 if d.mem(0x807FBB63,'u8')&2:d.press('Return',.1,1)
 if d.status()['map']==171:
  d.check('opening story returns control in Treehouse',d.mem(0x807444EC,'u8')==0,d.status())
  # Position fixture reaches the ordinary door. Native collision performs the
  # transition; no destination, action, character or progress flag is changed.
  d.place(d.zone_position(171,176),0,wait=4)
 d.cmd(wait=2);d.check('new game reaches Training Grounds',d.status()['map']==176,d.status());d.cmd(shot='newgame-training')
 # Intro text and fairy cutscenes may still hold the player; ordinary A input.
 for _ in range(90):
  s=d.status()
  if s['frame']>180 and s['player']['state']==12 and not d.mem(0x807444ec,'u8') and not d.mem(0x807463b8,'u8') and not d.mem(0x807fbb63,'u8')&2:break
  d.press('Shift_L',.15,.5)
 # Keep the native starting position: a second teleport near Cranky's
 # entrance can retrigger the introductory auto-walk/camera sequence.
 d.cmd(wait=2)
 hud=d.mem(0x80754280)
 d.results['tag_gates']={'enabled':d.mem(enabled),'cutscene':d.mem(0x807444ec,'u8'),'autowalk':d.mem(0x807463b8,'u8'),'pause':d.mem(0x807fbb63,'u8'),'fade':d.mem(0x807fd888,'f32'),'HUD':[d.mem(hud+i*0x30+0x20)for i in (0,1,5,8,10,12,13,14)] if hud else []}
 d.check('intro returns player control',d.status()['player']['state']==12,d.status())
 seen=[]
 for _ in range(4):d.press('a',.15,.8);seen.append(d.status()['character'])
 d.check('new file cycles only DK and always-unlocked Krusha',seen==[5,0,5,0],seen)
 d.press('a',.15,.8);d.check('fresh Krusha actor valid',d.status()['character']==5 and d.status()['player']['actor']==7)
 before=d.status()['frame'];d.cmd(keys=['Up','Shift_L'],seconds=.4,wait=.4);d.check('fresh Krusha moves and jumps',d.status()['frame']>before)
 d.cmd(wait=2)
 d.check('fresh Speed-OFF file has no crystals',d.status()['inventory'][3]==0,d.status())
 d.combo('i',wait=.3)
 d.check('fresh Krusha cannot shout before crystals unlock',d.status()['player']['state']!=0x67 and d.status()['inventory'][3]==0,d.status())
 for button in ['j','k','l']:d.combo(button,wait=1);d.results['observations'].append({'button':button,'status':d.status()})
 d.cmd(wait=6);d.check('fresh move inputs leave gameplay advancing',d.status()['frame']>before and d.status()['player']['actor']==7,d.status());d.cmd(shot='newgame-krusha')
 d.press('d',.15,1);d.check('fresh file returns to DK',d.status()['character']==0)
 d.press('Return',.15,1);d.press('Return',.15,1)
 d.results['complete']=True
except Exception as e:
 d.results['error']=repr(e);print('NEWGAME_ERROR',repr(e),flush=True)
 try:d.cmd(shot='release-newgame-failure',scene='release-newgame-failure')
 except Exception:pass
finally:
 (RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
 if d.proc and d.proc.poll() is None:d.proc.stdin.write('{"quit":true}\n');d.proc.stdin.flush();d.proc.wait(timeout=20)
 print('NEWGAME_COMPLETE',d.results.get('complete'),flush=True)
