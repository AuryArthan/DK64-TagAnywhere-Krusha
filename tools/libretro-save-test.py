#!/usr/bin/python3
"""Cold-boot native EEPROM persistence test; no savestates or option RAM writes."""
from pathlib import Path
import hashlib, importlib.util, json, os, struct, subprocess, sys
ROOT = Path(__file__).resolve().parent.parent
RUN = Path(os.environ['DK64_RUNTIME']).resolve()
SEED = Path(os.environ['DK64_TEST_SAVE'])
seed = SEED.read_bytes()
assert len(seed) == 2048
seed_hash = hashlib.sha256(seed).hexdigest()
ROM = Path(os.environ.get('DK64_TEST_ROM', ROOT/'rom/dk64-krusha-dev.z64'))
srm = RUN/'saves'/(ROM.stem+'.srm')
if srm.exists(): raise SystemExit('Use a new profile; this test creates its own native save.')
srm.parent.mkdir(parents=True, exist_ok=True)
srm.write_bytes(seed + b'\xff'*(0x48800-len(seed)))
spec = importlib.util.spec_from_file_location('driver', ROOT/'tools/krusha-test.py')
d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
d.REPORT_NAME = 'libretro-save-tests.json'
d.results.update(checks=[], fixtures='Explicit private native EEPROM copied; native menu inputs only; no savestates')
symbols = {row[1]:int(row[0],16) for row in (line.split() for line in ROM.with_suffix('.sym').read_text().splitlines()) if len(row)>=2}
off = 0x1fed020 + symbols['krushaenabled'] - 0x805dae00
lui,jr,lw = struct.unpack_from('>III', ROM.read_bytes(), off)
assert lui>>16==0x3c02 and jr==0x03e00008 and lw>>16==0x8c42
ENABLED = ((lui & 0xffff)<<16) + struct.unpack('>h',struct.pack('>H',lw & 0xffff))[0]
def start():
 d.proc = subprocess.Popen(['/usr/bin/python3',str(ROOT/'tools/control-libretro.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,env={**os.environ,'DK64_ROM':str(ROM)})
 print(d.proc.stdout.readline().strip(),flush=True)
 for _ in range(90):
  if d.status()['map']==80:break
  d.press('Return',1,1)
 d.check('native main menu reached',d.status()['map']==80,d.status());d.cmd(wait=8)
 d.check('core automatically selects EEPROM 16K','Save type: 1' in (RUN/'logs/emulator.log').read_text())
def stop():
 if d.proc and d.proc.poll() is None:
  d.proc.stdin.write('{"quit":true}\n');d.proc.stdin.flush();d.proc.wait(timeout=20)
def options():
 a=next(a for a in d.scene('save-menu')['actors'] if a['type']==326);data=d.mem(int(a['pointer'],16)+0x174)
 d.press('Left',.2,3)
 for _ in range(6):
  d.press('Shift_L',.3,2)
  if d.mem(data+0x12,'u8')==9:break
 for _ in range(6):
  if d.mem(data+0x17,'u8')==4:break
  d.press('Right',.2,1)
 d.check('native Krusha option selected',d.mem(data+0x12,'u8')==9 and d.mem(data+0x17,'u8')==4)
try:
 start();d.check('native seed loads Speed Mode',d.mem(0x8074452c,'u8')==1)
 d.check('Krusha initially enabled',d.mem(ENABLED)==1)
 options();d.press('Up',.2,1,shot='save-krusha-off');d.check('native option turns Krusha off',d.mem(ENABLED)==0)
 d.press('Control_L',.3,1);stop()
 saved=srm.read_bytes()[:2048]
 d.check('native EEPROM file written',saved!=seed,hashlib.sha256(saved).hexdigest())
 start();d.check('Krusha OFF survives complete frontend restart',d.mem(ENABLED)==0)
 d.check('Speed Mode preserved',d.mem(0x8074452c,'u8')==1)
 options();d.cmd(shot='save-off-after-restart');d.press('Down',.2,1);d.check('restore Krusha ON through UI',d.mem(ENABLED)==1)
 d.press('Control_L',.3,1);stop()
 d.check('source EEPROM fixture unchanged',hashlib.sha256(SEED.read_bytes()).hexdigest()==seed_hash)
 d.results['complete']=True
except Exception as exc:
 d.results['error']=str(exc);print('SAVE_TEST_ERROR',exc,flush=True)
finally:
 stop();(RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
sys.exit(0 if d.results.get('complete') else 1)
