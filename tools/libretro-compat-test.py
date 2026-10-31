from pathlib import Path
import os,subprocess,importlib.util,json,time,hashlib,sys
repo=Path(__file__).resolve().parent.parent;run=Path(os.environ['DK64_RUNTIME']).resolve()
os.environ.update(DK64_RUNTIME=str(run),DK64_TOOL_ROOT=os.environ.get('DK64_TOOL_ROOT',str(repo/'tools')),DK64_LIBRETRO_ROOT=os.environ.get('DK64_LIBRETRO_ROOT',str(repo/'runtime/libretro-tools')),DK64_DISPLAY=os.environ.get('DK64_DISPLAY',':112'),DK64_TEST_SAVE=os.environ['DK64_TEST_SAVE'])
# libretro's native save-memory block: EEPROM, mempaks, SRAM, FlashRAM.
(run/'saves').mkdir(parents=True,exist_ok=True)
rom=Path(os.environ.get('DK64_TEST_ROM',repo/'rom/dk64-krusha-dev.z64'))
digest=hashlib.sha256(rom.read_bytes()).hexdigest()
for name in ['libretro-compat-tests.json','libretro-interaction-tests.json']:
 previous=run/'logs'/name
 if previous.exists() and json.loads(previous.read_text())['rom_sha256']!=digest:
  raise SystemExit('This profile has evidence/states for another ROM; choose a fresh DK64_RUNTIME')
srm=run/'saves'/(rom.stem+'.srm')
if not srm.exists():
 seed=Path(os.environ['DK64_TEST_SAVE']).read_bytes()
 if len(seed)!=2048:raise SystemExit('Expected a 2048-byte native EEPROM fixture')
 srm.write_bytes(seed+b'\xff'*(0x48800-len(seed)))
spec=importlib.util.spec_from_file_location('d',repo/'tools/krusha-test.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
d.REPORT_NAME='libretro-interaction-tests.json' if os.environ.get('DK64_LIBRETRO_PHASE')=='interactions' else 'libretro-compat-tests.json';d.results.update(core_sha256=hashlib.sha256((Path(os.environ['DK64_LIBRETRO_ROOT'])/'core/mupen64plus_next_libretro.so').read_bytes()).hexdigest(),core='Mupen64Plus-Next / GLideN64',checks=[])
def start():
 d.proc=subprocess.Popen(['/usr/bin/python3',str(repo/'tools/control-libretro.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1,env={**os.environ,'DK64_ROM':str(d.ROM)});print(d.proc.stdout.readline(),flush=True)
d.start=start

def boot():
 for i in range(90):
  if d.status()['map']==80:break
  d.press('Return',1,1)
 d.check('cold boot reaches native main menu',d.status()['map']==80,d.status());d.cmd(wait=8)
 a=next(a for a in d.scene('main-menu')['actors'] if a['type']==326);data=d.mem(int(a['pointer'],16)+0x174)
 d.press('Left',.2,3)
 for i in range(6):
  d.press('Shift_L',.3,2)
  if d.mem(data+0x12,'u8')==9:break
 d.check('native options page reached',d.mem(data+0x12,'u8')==9)
 while d.mem(data+0x17,'u8')!=1:d.press('Right',.2,1)
 if not d.mem(0x8074452c,'u8'):d.press('Up',.2,1)
 d.check('native Speed Mode on',d.mem(0x8074452c,'u8')==1)
 d.press('Left',.2,1)
 if not d.mem(0x807444c0,'u8'):d.press('Up',.2,1)
 d.check('native Widescreen on',d.mem(0x807444c0,'u8')==1)
 d.cmd(shot='options-wide-speed-on');d.press('Control_L',.3,2);d.press('Right',.2,2)
 for i in range(12):
  d.press('Shift_L',.4,2)
  if d.status()['map']==34:break
 d.cmd(wait=8)
 for i in range(60):
  st=d.status()
  if st['map']==34 and st['frame']>150 and st['player']['state']==12:break
  d.cmd(wait=.5)
 d.check('adventure ready',d.status()['map']==34 and d.status()['player']['state']==12,d.status())
 d.checkpoint(0,'compat-ready-dk-isles');d.cmd(wait=1)

def cameras():
 d.place([2940,500,2220],2048,wait=1)
 d.press('a',.3,1);d.check('Krusha tags in',d.status()['character']==5,d.status())
 for wide in [1,0]:
  d.cmd(write=[{'address':0x807444c0,'type':'u8','value':wide}],wait=.2)
  for char in [5,0]:
   if d.status()['character']!=char:d.press('d',.3,1)
   d.combo('k',wait=1,shot=f'camera-{char}-wide-{wide}')
   d.check(f'camera enters character {char} wide {wide}',d.status()['player']['state']==4,d.status())
   film=d.status()['inventory'][4];d.press('Control_L',.25,3,shot=f'photo-{char}-wide-{wide}')
   d.check(f'photo consumes film character {char} wide {wide}',d.status()['inventory'][4]==film-1,d.status())
   for attempt in range(5):
    d.press('i',.4,1)
    if d.status()['player']['state']==12:break
   d.check('camera exits safely after native shutter cooldown',d.status()['player']['state']==12,d.status())
   if char==0:
    d.combo('j',wait=.8);d.press('i',.3,1,shot=f'sniper-wide-{wide}')
    d.check('upgraded scope enters',d.status()['player']['state']==2,d.status())
    ammo=d.status()['inventory'][0];d.press('Control_L',.25,.5)
    d.check('scope fires',d.status()['inventory'][0]<ammo,d.status());d.press('i',.3,1);d.combo('j',wait=.8)
  # DK -> Krusha for next pass.
  if wide==1:d.press('a',.3,1)
 d.cmd(write=[{'address':0x807444c0,'type':'u8','value':1}],wait=.2)
 d.checkpoint(1,'compat-cameras-complete')

def water():
 if d.status()['character']!=5:d.press('a',.3,1)
 d.place([2254,450,2941],wait=2);d.press('z',.4,.5);d.cmd(keys=['Up','Shift_L'],seconds=.5,wait=.5,shot='water-wide')
 d.check('Krusha underwater',d.status()['player']['state']==0x4f,d.status());d.cmd(shot='water-wide-settled')
 d.cmd(write=[{'address':0x807444c0,'type':'u8','value':0}],wait=1,shot='water-standard')
 d.cmd(write=[{'address':0x807444c0,'type':'u8','value':1}],wait=.5)
 d.place([2780,500,2260],wait=2);d.checkpoint(2,'compat-water-complete')

def restore(slot):
 d.press(str(slot),.1,.2);d.press('F7',.1,4)
def flag_address(flag):
 file=d.mem(0x807467c8,'u8');slots=[d.mem(0x807edea8+i,'u8') for i in range(4)]
 size=((((d.mem(0x807ecea0,'u16')+0x6b7)&~63)+0x27)&~7)//8
 return 0x807ecea8+slots.index(file)*size+flag//8

def boulder():
 # Slot 0 is this exact ROM's native ready DK-in-Isles checkpoint.
 restore(0);d.place([2960,1038,1928],wait=2)
 d.press('a',.3,1);d.press('a',.3,1)
 d.check('boulder test starts as Chunky',d.status()['character']==4,d.status())
 d.cmd(write=[{'address':0x807fcc4b,'type':'u8','value':12}]);d.press('Control_L',.3,2)
 p=int(d.status()['player_pointer'],16);held=d.mem(p+0x32c)
 d.check('Chunky lifts boulder',d.status()['player']['state']==0x48 and held!=0,d.status())
 for key in ['d','a','x']:
  d.press(key,.3,.6);d.check('Chunky carry blocks tag '+key,d.status()['character']==4,d.status())
 d.press('z',.3,2);d.check('Chunky drops boulder',d.mem(p+0x32c)==0,d.status())
 d.press('d',.3,1);d.check('tagging resumes after drop',d.status()['character']==5,d.status())
 d.checkpoint(3,'compat-heavy-carry-complete')

def pickups():
 d.place([2780,500,2260],wait=1);d.go(7);d.cmd(wait=3)
 d.check('pickup tests keep Krusha identity',d.status()['character']==5,d.status())
 d.cmd(write=[{'address':0x807fcc40,'type':'u16','value':100},{'address':0x807fcc44,'type':'u16','value':10}])
 d.place([2418.85,280.5,720.65],wait=3);s=d.status();d.cmd(shot='pickup-ammo')
 d.check('ammo crate supplies five bazooka rounds, grenades separate',s['inventory'][0]==105 and s['inventory'][2]==10,s)
 d.place([1145.22,288,1987.38],wait=2);s=d.status();d.cmd(shot='pickup-orange')
 d.check('orange grenade refills separately from bazooka',s['inventory'][2]==11 and s['inventory'][0]==105,s)
 d.place([1000,280,1013],wait=2)
 d.check('Krusha still cannot collect colored coins',d.mem(0x807fc950+5*0x5e+6,'u16')==0 and d.mem(0x807fc950+4*0x5e+6,'u16')==0,d.status())
 d.place([2909,343,2035],wait=2)
 d.check('Krusha still cannot collect colored bananas',all(d.mem(0x807fc950+5*0x5e+0xa+i*2,'u16')==0 for i in range(14)))
 d.checkpoint(4,'compat-pickups-japes')
 # Galleon's 2-door ship has native static melon groups. Use its own map,
 # restore this same-ROM checkpoint afterward; do not invent a loading zone.
 d.go(43);d.cmd(wait=2);d.cmd(write=[{'address':0x807fcc4b,'type':'u8','value':4}]);d.place([1572.89,0,903.61],wait=2)
 hp=d.mem(0x807fcc4b,'u8');d.check('native melons refill Krusha health',hp>4,{'health':hp,'status':d.status()});d.cmd(shot='pickup-health');restore(4)

def dialogue_text():
 actors=d.scene('dialogue')['actors'];lines=[]
 d.cmd(tap='p',wait=.1)
 try:
  for a in actors:
   if a['type']!=299:continue
   owner=d.mem(int(a['pointer'],16)+0x174);line=d.mem(owner+0xc)
   for _ in range(64):
    if not 0x80000000<=line<0x80800000:break
    glyph=d.mem(line+0xc);word=[]
    for j in range(256):
     if not 0x80000000<=glyph<0x80800000:break
     row=d.cmd(read=[{'address':glyph+0x12,'type':'u8'},{'address':glyph+0xa0,'type':'u32'}])[0]['memory'];word.append(chr(row[0]));glyph=row[1]
    lines.append(''.join(word));line=d.mem(line+0x1c)
 finally:d.cmd(tap='p',wait=.1)
 return ' '.join(lines)

def snide():
 for char in [5,0]:
  restore(4)
  if char==0:d.press('d',.3,1)
  d.check('Snide visitor identity',d.status()['character']==char,d.status());d.go(15);d.cmd(wait=2)
  text=''
  for attempt in range(5):
   text=dialogue_text()
   if text:break
   d.cmd(wait=1)
  d.cmd(shot='snide-'+str(char))
  d.check('Snide addresses '+('Krusha as Kremling' if char==5 else 'DK as Kong'),('KREMLING' if char==5 else 'KONG') in text and (char==5 or 'KREMLING' not in text),text)
 restore(4)

def crown():
 addr=flag_address(0x261);before=d.mem(addr,'u8');d.check('Japes crown initially uncollected',not before&(1<<(0x261&7)),hex(before))
 d.place([1989.7,520,2086.71],wait=2)
 for attempt in range(6):
  d.press('z',.3,3)
  if d.status()['map']==53:break
  if d.status()['player']['state'] not in (12,13):d.press('Shift_L',.3,2)
 d.check('Krusha enters native crown battle from pad',d.status()['map']==53 and d.status()['character']==5,d.status())
 d.cmd(wait=3,shot='crown-battle-entered');d.checkpoint(5,'compat-crown-arena')
 deadline=time.monotonic()+210
 while time.monotonic()<deadline:
  s=d.status()
  if s['map']!=53:break
  scene=d.scene('crown-live');c=[o for o in scene['objects'] if o['type']==0x18d]
  if c:
   d.place(c[0]['xyz'],wait=2);break
  # Crown arenas normally restrict instrument inputs; fight with native
  # punches and jumps rather than relying on an instrument shortcut.
  d.press('Control_L',.22,.1);d.press('Shift_L',.22,.1)
  print(json.dumps({'arena_frame':s['frame'],'character':s['character'],'state':s['player']['state']}),flush=True)
 # Reward/exit cutscene and native return to the parent map.
 for attempt in range(20):
  if d.status()['map']==7:break
  d.cmd(wait=1)
 after=d.mem(flag_address(0x261),'u8')
 d.check('Krusha earns battle crown and returns safely',d.status()['map']==7 and d.status()['character']==5 and bool(after&(1<<(0x261&7))),{'flag':hex(after),'status':d.status()})
 d.cmd(wait=5,shot='crown-earned')
 d.check('crown celebration finishes without a crash',d.status()['player']['state']==12 and d.status()['player']['actor']==7,d.status())
 before=d.status()['player']
 d.press('Up',.4,.3)
 after=d.status()['player']
 d.check('movement works after crown reward',sum((after[k]-before[k])**2 for k in ('x','z'))>1,d.status())
 d.checkpoint(6,'compat-crown-earned')

try:
 d.start()
 if os.environ.get('DK64_LIBRETRO_RESUME')=='0':
  previous=json.loads((run/'logs/libretro-compat-tests.json').read_text())
  assert previous['rom_sha256']==d.DIGEST, 'Checkpoint belongs to a different ROM'
  d.results['cold_boot']=False
  d.press('F7',.1,8)
 else:boot()
 if os.environ.get('DK64_LIBRETRO_PHASE')=='interactions':
  boulder();pickups();snide();crown()
 else:cameras();water()
 d.results['core_options_requested']=(run/'core-options.cfg').read_text()
 d.results['complete']=True
except Exception as e:
 d.results['error']=str(e);print('TEST_ERROR',e,flush=True)
 try:d.cmd(shot='compat-test-failure')
 except Exception:pass
finally:
 (run/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2))
 print('INTERACTIVE_READY',flush=True)
 for line in sys.stdin:
  try:print(json.dumps(d.cmd(**json.loads(line))),flush=True)
  except Exception as e:print(str(e),flush=True)
 if d.proc and d.proc.poll()is None:d.proc.stdin.write('{"quit":true}\n');d.proc.stdin.flush();d.proc.wait(timeout=15)
