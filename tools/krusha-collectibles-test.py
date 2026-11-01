#!/usr/bin/python3
"""Exact-ROM pickup/quest checks using native collection and logged fixtures.

DK64_COLLECTIBLE_SEED_PROFILE must contain a completed core regression on the
same ROM. The destination DK64_RUNTIME must be a separate test profile. Select
DK64_COLLECTIBLE_PHASE=supplies,quests,keys,fairies,coins,balloons,locks,bean (default: all).
"""
from pathlib import Path
import importlib.util,json,os,struct,zlib,shutil,subprocess
ROOT=Path(__file__).resolve().parent.parent
seed=Path(os.environ['DK64_COLLECTIBLE_SEED_PROFILE']).resolve()
run=Path(os.environ['DK64_RUNTIME']).resolve()
if seed==run:raise SystemExit('Use a separate destination profile')
spec=importlib.util.spec_from_file_location('driver',ROOT/'tools/krusha-test.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
backend=os.environ.get('DK64_COLLECTIBLE_BACKEND','standalone')
seed_report=seed/'logs'/('libretro-compat-tests.json' if backend=='libretro' else 'krusha-tests.json')
if backend=='libretro' and (seed/'logs/libretro-boot-tests.json').exists():seed_report=seed/'logs/libretro-boot-tests.json'
report=json.loads(seed_report.read_text())
assert report['rom_sha256']==d.DIGEST and report.get('complete') and all(c['passed'] for c in report['checks']), 'Need completed passing exact-ROM seed checks'
if (run/'states').exists() and any((run/'states').iterdir()):raise SystemExit('Choose a new test profile; preserve existing states')
(run/'states').mkdir(exist_ok=True)
source=(seed/'states'/(d.ROM.stem+'.state')) if backend=='libretro' else next((seed/'states').glob('Donkey*.st1'))
shutil.copy2(source,run/'states'/source.name)
if backend=='libretro':
 shutil.copy2(seed/'saves'/(d.ROM.stem+'.srm'),run/'saves'/(d.ROM.stem+'.srm'))
 def start():
  d.proc=subprocess.Popen(['/usr/bin/python3',str(ROOT/'tools/control-libretro.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1,env={**os.environ,'DK64_ROM':str(d.ROM)})
  print(d.proc.stdout.readline(),flush=True)
 d.start=start
phase=os.environ.get('DK64_COLLECTIBLE_PHASE','all')
d.REPORT_NAME='collectibles-'+phase+'.json'
d.results.update(backend=backend,cold_boot=False,exact_rom_state=True,fixtures='Exact-ROM state from completed core; logged position, resource and temporary unlock fixtures. No identity/action/code/collection-result writes.',phase=phase)
raw=(ROOT/'rom/dk64.z64').read_bytes();base=0x101c50
assert d.hashlib.sha1(raw).hexdigest()=='cf806ff2603640a748fca5026ded28802f1f4a50'

# Teleports are fixtures; ordinary play moves the camera/chunk loader along
# with the player. Explicitly recenter it before testing distant actors/items.
_original_place=d.place
def place_ready(xyz,facing=0,wait=1.5):
 _original_place(xyz,facing,wait)
 d.press('c',.3,.7)
d.place=place_ready
def go_ready(mid):
 d.cmd(tap='p',wait=.05)
 d.cmd(fixture_map=mid,wait=.05)
 d.cmd(tap='p',wait=2)
 for _ in range(120):
  st=d.status()
  if st['map']==mid and st['frame']>180 and not d.mem(0x807444ec,'u8') and not d.mem(0x807463b8,'u8'):break
  d.cmd(wait=.25)
 d.check('fixture loaded map '+str(mid),d.status()['map']==mid,d.status())
d.go=go_ready

def objects(mid,typ):
 t=base+struct.unpack_from('>I',raw,base+9*4)[0];a,b=struct.unpack_from('>II',raw,t+mid*4)
 data=raw[base+(a&0x7fffffff):base+(b&0x7fffffff)]
 if data[:2]==b'\x1f\x8b':data=zlib.decompress(data,15+32)
 return [list(struct.unpack_from('>fff',data,4+i*0x30)) for i in range(struct.unpack_from('>I',data)[0]) if struct.unpack_from('>H',data,4+i*0x30+0x28)[0]==typ]

def actor_positions(mid,types):
 t=base+struct.unpack_from('>I',raw,base+9*4)[0];a,b=struct.unpack_from('>II',raw,t+mid*4)
 data=raw[base+(a&0x7fffffff):base+(b&0x7fffffff)]
 if data[:2]==b'\x1f\x8b':data=zlib.decompress(data,15+32)
 p=4+struct.unpack_from('>I',data)[0]*0x30
 p+=4+struct.unpack_from('>I',data,p)[0]*0x24
 n=struct.unpack_from('>I',data,p)[0];p+=4
 return [(struct.unpack_from('>H',data,p+i*0x38+0x32)[0]+16,list(struct.unpack_from('>fff',data,p+i*0x38))) for i in range(n) if struct.unpack_from('>H',data,p+i*0x38+0x32)[0]+16 in types]

def restore():
 d.press('0' if backend=='libretro' else '1',.1,.1);d.press('F7',.1,12)
 # Loading a native state can finish paused. Establish a running emulator
 # before helpers start their paired pause/position/resume input sequence.
 before=d.status()['frame'];d.cmd(wait=.7)
 if d.status()['frame']==before:d.cmd(tap='p',wait=.7)
 if backend=='libretro':d.press('a',.25,1)
 d.check('exact-ROM Krusha checkpoint',d.status()['character']==5 and d.status()['map']==34,d.status())

def write(address,value,kind='u16'):
 d.cmd(write=[{'address':address,'type':kind,'value':value}])

def flag_addr(flag):
 f=d.mem(0x807467c8,'u8');slots=[d.mem(0x807edea8+i,'u8') for i in range(4)]
 size=((((d.mem(0x807ecea0,'u16')+0x6b7)&~63)+0x27)&~7)//8
 return 0x807ecea8+slots.index(f)*size+flag//8

def flag(flag):return bool(d.mem(flag_addr(flag),'u8')&(1<<(flag&7)))
def flag_fixture(f,on):
 a=flag_addr(f);v=d.mem(a,'u8');write(a,(v|(1<<(f&7))) if on else (v&~(1<<(f&7))),'u8')

def supplies():
 for wide in [0,1]:
  restore();write(0x807444c0,wide,'u8');d.go(7)
  write(0x807fcc46,1500);d.place(objects(7,0x8e)[0],wait=2)
  d.check('crystal collected wide '+str(wide),1500 < d.status()['inventory'][3] <= 3000 and (d.status()['inventory'][3]-1500)%150==0,d.status())
  before=d.status()['inventory'][3];d.combo('i',wait=.2)
  d.check('collected crystals fund shout wide '+str(wide),d.status()['player']['state']==0x67 and d.status()['inventory'][3]==before-150,d.status());d.wait_player_ready()
  write(0x807fcc48,3);d.place(objects(7,0x98)[0],wait=2)
  d.check('film collected wide '+str(wide),3 < d.status()['inventory'][4] <= 10,d.status());d.cmd(shot='film-crystals-wide-'+str(wide))
  write(0x807fcc46,3000);d.place(objects(7,0x8e)[1],wait=2)
  d.check('crystals respect native capacity',d.status()['inventory'][3]==3000,d.status())
  d.go(48);write(0x807fcc40,100);write(0x807fcc42,7)
  d.place(objects(48,0x11)[0],wait=3)
  for _ in range(30):
   if d.status()['inventory'][:2]==[105,7]:break
   d.cmd(wait=.25)
  d.check('homing crate supplies five REGULAR bazooka rounds wide '+str(wide),d.status()['inventory'][:2]==[105,7],d.status())
  d.check('bazooka remains non-homing',d.mem(0x807fc950+5*0x5e+2,'u8')&3==1)
  d.place([1181,1250,1360],wait=1);d.combo('j',wait=.5)
  d.wait_frames(30)
  before=d.status()['inventory'][:2];d.press('Control_L',.2,.4)
  d.check('bazooka still fires regular ammo only',d.status()['inventory'][0]<before[0] and d.status()['inventory'][1]==before[1],d.status());d.combo('j',wait=.5)
  restore();d.press('d',.25,1);d.check('original DK selected for comparison',d.status()['character']==0,d.status());d.go(48)
  write(0x807fcc40,100);write(0x807fcc42,7);d.place(objects(48,0x11)[1],wait=3)
  for _ in range(30):
   if d.status()['inventory'][:2]==[100,12]:break
   d.cmd(wait=.25)
  d.check('DK keeps native homing-ammo crate behavior',d.status()['inventory'][:2]==[100,12],d.status())

def quests():
 def gb_counts():
  return d.cmd(read=[{'address':0x807fc950+k*0x5e+0x42+i*2,'type':'u16'} for k in range(6) for i in range(14)])[0]['memory']
 restore();d.go(44);gold=gb_counts()
 # Hold a close position through the real clam cycle. Closed-shell contact
 # must not award a pearl; the native open phase must still be respected.
 pos=objects(44,0x1b4)[0]
 clams=[a for a in d.scene('clam-timing')['loaded_actors'] if a['type']==286]
 clam=min(clams,key=lambda a:sum((a['xyz'][i]-pos[i])**2 for i in range(3)))
 for _ in range(120):
  if d.mem(int(clam['pointer'],16)+0x154,'u8')==0:break
  d.cmd(wait=.1)
 d.cmd(tap='p',wait=.05);d.cmd(position=pos,wait=0);d.cmd(tap='slash',wait=.03)
 d.check('closed clam does not award its pearl',not flag(0xba))
 d.cmd(position=[pos[0],pos[1],pos[2]-120],wait=0);d.cmd(tap='p',wait=.1)
 for f,pos in zip(range(0xba,0xbf),objects(44,0x1b4)):
  d.check('pearl initially uncollected '+hex(f),not flag(f))
  d.place([pos[0],pos[1],pos[2]-120],wait=1);write(0x807fcc4b,12,'u8')
  clam=min(clams,key=lambda a:sum((a['xyz'][i]-pos[i])**2 for i in range(3)))
  for _ in range(120):
   if d.mem(int(clam['pointer'],16)+0x154,'u8')==2:break
   d.cmd(wait=.1)
  d.place(pos,wait=.3)
  for _ in range(10):
   if flag(f):break
   d.cmd(wait=.2)
  d.cmd(scene='pearl-contact-'+hex(f))
  d.check('Krusha collects pearl '+hex(f),flag(f),d.status())
 d.check('pearls award no Kong Golden Bananas',gb_counts()==gold)
 before=[flag(f) for f in range(0xba,0xbf)];d.place(objects(44,0x1b4)[0],wait=3)
 d.check('collected pearls remain collected without duplicate flags',before==[flag(f) for f in range(0xba,0xbf)])
 d.cmd(shot='pearls-collected')
 bean()

def bean():
 def gb_counts():
  return d.cmd(read=[{'address':0x807fc950+k*0x5e+0x42+i*2,'type':'u16'} for k in range(6) for i in range(14)])[0]['memory']
 restore();d.go(52);gold=gb_counts();pos=objects(52,0x198)[0]
 d.place(pos,wait=2)
 d.check('bean cannot be taken before its enemy-clear gate',not d.mem(0x807fdd90+34//8,'u8')&(1<<(34&7)))
 d.place([759,205.33,764],wait=1)
 for _ in range(4):
  before=d.status()['inventory'][3];d.combo('i',wait=.3)
  if d.status()['inventory'][3]<before:break
  d.cmd(wait=1)
 scene=d.scene('bean-after-fight');obj=next(o for o in scene['objects'] if o['type']==0x198);b=d.mem(int(obj['pointer'],16)+0x7c)
 # Enemy deaths and the reveal animation use native frames, not wall seconds.
 for _ in range(100):
  if d.mem(b+0x60,'u8')==0 and d.mem(b+0x70,'u8'):break
  d.cmd(wait=.25)
 d.check('bean becomes collectible only after native enemy clear',d.mem(b+0x60,'u8')==0 and bool(d.mem(b+0x70,'u8')))
 d.place(pos,wait=3)
 for _ in range(40):
  if d.mem(0x807fdd90+34//8,'u8')&(1<<(34&7)):break
  d.cmd(wait=.25)
 d.check('bean native script records collection',bool(d.mem(0x807fdd90+34//8,'u8')&(1<<(34&7))),{'script':hex(b),'state':d.mem(b+0x48,'u8'),'status':d.status()})
 d.check('bean does not grant its delivery Golden Banana',gb_counts()==gold and not flag(0xfb))
 d.cmd(shot='bean-collected')

def keys():
 restore();write(0x8074452c,0,'u8')
 # The coin door's native script owns the Helm key flag. Teleporting behind
 # a still-locked door skips that monitor; supply the ordinary access flags.
 flag_fixture(0x84,True);flag_fixture(0x17b,True);flag_fixture(0x303,True);d.go(17)
 d.check('Helm key initially uncollected',not flag(0x17c))
 d.place([279.52,64,5230.49],wait=5)
 d.place(objects(17,0x13c)[0],wait=5)
 d.cmd(scene='key-after-contact')
 d.check('Krusha collects shared Helm boss key',flag(0x17c),d.status());d.cmd(wait=5,shot='boss-key-collected')
 d.check('key celebration finishes safely with Speed Mode OFF',d.status()['character']==5 and d.status()['player']['actor']==7 and d.status()['player']['state'] in (12,13,0x4e,0x4f),d.status())
 restore();d.go(17);d.place(objects(17,0x90)[0],wait=2)
 d.check('physical Helm medal does not award a sixth-character medal',not any(flag(f) for f in range(0x248,0x24d)),d.status())

def fairies():
 spec=importlib.util.spec_from_file_location('extra',ROOT/'tools/krusha-extra-test.py')
 extra=importlib.util.module_from_spec(spec);spec.loader.exec_module(extra);extra.d=d
 for wide in [0,1]:
  restore();write(0x807444c0,wide,'u8');d.go(7)
  extra.fairy_photo()
  d.cmd(shot='fairy-capture-complete-wide-'+str(wide))

def coins():
 for mid,temp,permanent,name in [(26,17,0x84,'Nintendo'),(5,98,0x17b,'Rareware')]:
  restore();d.check(name+' coin initially uncollected',not flag(permanent));d.go(26)
  if name=='Nintendo':d.go(29)
  # Native arcade/Jetpac win-return flag as an explicit prerequisite fixture.
  # We test the real reward script/cutscene, not a minigame completion claim.
  address=0x807fdd90+temp//8;write(address,d.mem(address,'u8')|(1<<(temp&7)),'u8')
  # Both small rooms have real exits, but neither uses the generic 9/16
  # loading-zone kinds accepted by the redirect fixture. Leave natively.
  if name=='Nintendo':d.place([120,0,11],wait=6)
  else:d.go(5)
  d.check('native reward return map '+name,d.status()['map']==mid,d.status())
  if name=='Nintendo':d.place(objects(26,0x48)[0],wait=3)
  d.cmd(scene=name.lower()+'-reward-script')
  for attempt in range(40):
   if flag(permanent):break
   d.press('Shift_L',.15,.5)
  d.check('native '+name+' reward script awards shared coin to Krusha',flag(permanent),d.status())
  d.cmd(wait=3,shot=name.lower()+'-coin-earned')
  d.check(name+' celebration keeps Krusha actor valid',d.status()['character']==5 and d.status()['player']['actor']==7,d.status())

def balloons():
 restore();d.go(7)
 positions=actor_positions(7,[91,111,112,113,114])
 d.check('balloon setup locations found',bool(positions),positions)
 def shot_into_balloon(a,projectile_type):
  d.press('Control_L',.1,0);d.cmd(tap='p',wait=0)
  projectiles=[x for x in d.scene('balloon-live-shot')['loaded_actors'] if x['type']==projectile_type]
  d.check('native gun projectile exists',bool(projectiles),projectiles)
  ptr=int(projectiles[-1]['pointer'],16)
  for frame in range(5):
   scene=d.scene('balloon-collision-frame')['loaded_actors']
   target=next((x for x in scene if x['pointer']==a['pointer']),None)
   if target is None or not any(int(x['pointer'],16)==ptr and x['type']==projectile_type for x in scene):break
   d.cmd(write=[{'address':ptr+off+i*4,'type':'f32','value':target['xyz'][i]} for off in (0x7c,0x88) for i in range(3)])
   d.cmd(tap='slash',wait=.03)
  d.cmd(tap='p',wait=.5)
  return d.scene('balloon-after-shot')['loaded_actors']
 tested=set()
 for typ,pos in positions:
  if typ in tested:continue
  d.place(pos,0,wait=2)
  a=next((a for a in d.scene('balloon-touch-'+str(typ))['loaded_actors'] if a['type']==typ),None)
  d.check('native colored balloon remains after Krusha contact '+str(typ),a is not None)
  tested.add(typ)
 d.check('all five balloon colors exercised by contact',tested=={91,111,112,113,114},sorted(tested))
 d.check('balloon contact awards no bananas',all(d.mem(0x807fc950+5*0x5e+0xa+i*2,'u16')==0 for i in range(14)))
 # Exercise real gun collisions on the yellow balloon over stable ground.
 # The five native collision lists separately exclude projectile 171; their
 # shared handler also rejects a late original-Kong hit while Krusha is active.
 typ,pos=next((t,p) for t,p in positions if t==114)
 restore();d.go(7);d.place([pos[0],pos[1]-25,pos[2]+200],0,wait=2)
 write(0x807fcc4b,12,'u8');d.combo('i',wait=5);d.combo('j',wait=.8)
 a=next(x for x in d.scene('balloon-bazooka-control')['loaded_actors'] if x['type']==114)
 live=shot_into_balloon(a,171)
 d.check('Krusha bazooka cannot pop colored balloon',any(x['pointer']==a['pointer'] and x['type']==114 for x in live),d.status())
 restore();d.press('d',.25,1);d.check('original DK selected for balloon control',d.status()['character']==0,d.status())
 d.go(7);d.place([pos[0],pos[1]-25,pos[2]+200],0,wait=2)
 d.combo('i',wait=15);d.combo('j',wait=.8)
 a=next(x for x in d.scene('balloon-positive-control')['loaded_actors'] if x['type']==114)
 before=d.mem(0x807fc950+0xa,'u16');shot_into_balloon(a,48)
 d.check('original Kong still pops own balloon and receives ten bananas',d.mem(0x807fc950+0xa,'u16')==before+10,d.status())
 # A genuine coconut left in flight must not credit a sixth banana counter
 # after a native D-pad tag. Hold only its position while stepping the tag.
 restore();d.press('d',.25,1);d.go(7)
 typ,pos=next((t,p) for t,p in positions if t==114)
 d.place([pos[0],pos[1]-25,pos[2]+200],0,wait=2)
 d.combo('i',wait=15);d.combo('j',wait=.8)
 a=next(x for x in d.scene('late-shot-balloon')['loaded_actors'] if x['type']==typ)
 d.press('Control_L',.1,0);d.cmd(tap='p',wait=0)
 shot=next(x for x in d.scene('late-shot-projectile')['loaded_actors'] if x['type']==48);ptr=int(shot['pointer'],16)
 d.cmd(down=['a'],wait=0)
 for _ in range(15):
  # Keep the live projectile away from collisions until the tag is complete.
  d.cmd(write=[{'address':ptr+off+i*4,'type':'f32','value':pos[i]+(400 if i==0 else 0)} for off in (0x7c,0x88) for i in range(3)])
  d.cmd(tap='slash',wait=.03)
  if d.status()['character']==5:break
 d.cmd(up=['a'],wait=0);d.check('native tag completes with original projectile in flight',d.status()['character']==5,d.status())
 for _ in range(5):
  scene=d.scene('late-shot-collision')['loaded_actors'];target=next(x for x in scene if x['pointer']==a['pointer'])
  if not any(x['pointer']==shot['pointer'] and x['type']==48 for x in scene):break
  d.cmd(write=[{'address':ptr+off+i*4,'type':'f32','value':target['xyz'][i]} for off in (0x7c,0x88) for i in range(3)])
  d.cmd(tap='slash',wait=.03)
 d.cmd(tap='p',wait=.5)
 d.check('late original projectile cannot pop a balloon for Krusha',any(x['pointer']==a['pointer'] and x['type']==114 for x in d.scene('late-shot-result')['loaded_actors']) and all(d.mem(0x807fc950+5*0x5e+0xa+i*2,'u16')==0 for i in range(14)),d.status())

def locks():
 restore();write(0x8074452c,0,'u8');flag_fixture(377,False)
 for i in range(5):write(0x807fc950+i*0x5e,0,'u8')
 write(0x807fcc46,0);d.place([2940,500,2220],2048,wait=1)
 d.combo('i',wait=.4);d.check('no shout before native crystal unlock',d.status()['player']['state']!=0x67 and d.status()['inventory'][3]==0,d.status())
 write(0x807fcc46,1500);d.combo('i',wait=.4)
 d.check('locked shout rejects even pre-existing crystal stock',d.status()['player']['state']!=0x67 and d.status()['inventory'][3]==1500,d.status());write(0x807fcc46,0)
 d.go(7);pos=objects(7,0x8e)[0];d.place(pos,wait=2)
 d.check('locked crystal cannot be collected',d.status()['inventory'][3]==0,d.status())
 # An original Kong's first crystal move unlocks the shared crystal capacity;
 # camera remains locked, exercising the distinction from camera/shockwave.
 write(0x807fc950+4*0x5e,1,'u8');d.place(pos,wait=2)
 d.check('original crystal move unlocks pickup for Krusha',d.status()['inventory'][3]>=150,d.status())
 d.place([910,280,800],wait=1);before=d.status()['inventory'][3];d.combo('i',wait=.2)
 d.check('unlock enables shout, consuming one crystal',d.status()['player']['state']==0x67 and d.status()['inventory'][3]==before-150,d.status());d.cmd(wait=5)
 film=d.status()['inventory'][4];d.place(objects(7,0x98)[0],wait=2)
 d.check('film remains unavailable before camera unlock',d.status()['inventory'][4]==film,d.status())
 restore();d.go(48)
 # Headphones are actors, not collected model2 props. Inspect native behavior
 # rather than adding them to the model2 whitelist.
 phone_positions=actor_positions(48,[128]);d.place(phone_positions[0][1],wait=2)
 phones=[a for a in d.scene('headphones')['loaded_actors'] if a['type']==128]
 d.check('native headphones present',bool(phones),phones)
 if phones:
  write(0x807fcc46,1500);d.place(phones[0]['xyz'],wait=2)
  d.check('headphones do not replenish shout crystals',d.status()['inventory'][3]==1500,d.status())
  d.check('headphones do not create sixth instrument energy',d.mem(0x807fc950+5*0x5e+8,'u16')==0)
  d.press('d',.25,1);write(0x807fc950+8,0);d.place(phones[0]['xyz'],wait=2)
  d.check('headphones still refill original DK instrument energy',d.status()['character']==0 and d.mem(0x807fc950+8,'u16')>0,d.status())

try:
 d.start()
 # Load states after native boot has initialized its code/EEPROM threads.
 # Early restores in this harness sometimes froze at the first restored
 # frame. Let native boot and renderer initialization settle before F7.
 for _ in range(80):
  if d.status()['map']==80:break
  d.press('Return',.3,.6)
 d.cmd(wait=12)
 for name,fn in [('supplies',supplies),('quests',quests),('keys',keys),('fairies',fairies),('coins',coins),('balloons',balloons),('locks',locks),('bean',bean)]:
  if phase==name or (phase=='all' and name!='bean'):fn()
 d.results['complete']=True
except Exception as e:
 d.results['error']=repr(e);print('COLLECTIBLE_TEST_ERROR',repr(e),flush=True)
 try:d.cmd(shot='collectible-failure')
 except Exception:pass
finally:
 (run/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
 if d.proc and d.proc.poll()is None:d.proc.stdin.write('{"quit":true}\n');d.proc.stdin.flush();d.proc.wait(timeout=15)
 print('COLLECTIBLE_TEST_COMPLETE',d.results.get('complete'),flush=True)
