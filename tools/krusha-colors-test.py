#!/usr/bin/python3
"""Native charged-B attacks, model-cache isolation, and both aspect modes.

Use a new DK64_RUNTIME and an explicit DK64_TEST_SAVE. Optional
DK64_COLORS_SEED_PROFILE reuses slot 1 from a passing exact-ROM core suite.
DK64_COLORS_BACKEND=libretro selects the pinned Mupen64Plus-Next controller.
DK64_COLORS_FOCUSED=1 checks Krusha/DK/Krusha only (both aspect modes).
"""
from pathlib import Path
import importlib.util
import json
import os
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('driver', ROOT/'tools/krusha-test.py')
d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
d.REPORT_NAME = 'character-colors-tests.json'
if (d.RUN/'logs'/d.REPORT_NAME).exists():
    raise SystemExit('Preserve previous evidence; choose a fresh DK64_RUNTIME')
backend = os.environ.get('DK64_COLORS_BACKEND', 'standalone')
d.results.update(backend=backend, fixtures='Native EEPROM; position and aspect-option fixtures only. Real charged B input, no actor/animation/code writes.')
if backend == 'libretro':
    srm = d.RUN/'saves'/(d.ROM.stem+'.srm')
    if not srm.exists():
        eep = Path(os.environ['DK64_TEST_SAVE']).read_bytes()
        assert len(eep) == 2048
        srm.write_bytes(eep + b'\xff'*(0x48800-len(eep)))
    def start():
        d.proc = subprocess.Popen(['/usr/bin/python3', str(ROOT/'tools/control-libretro.py')],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
            env={**os.environ, 'DK64_ROM':str(d.ROM)})
        print(d.proc.stdout.readline(), flush=True)
    d.start = start

def ready():
    seed = os.environ.get('DK64_COLORS_SEED_PROFILE')
    if seed:
        assert backend == 'standalone'
        seed = Path(seed).resolve()
        assert seed != d.RUN
        report = json.loads((seed/'logs/krusha-tests.json').read_text())
        assert report['rom_sha256'] == d.DIGEST and report.get('complete') and all(c['passed'] for c in report['checks'])
        (d.RUN/'states').mkdir(exist_ok=True)
        assert not any((d.RUN/'states').iterdir()), 'Preserve old states; use a fresh profile'
        source = next((seed/'states').glob('Donkey*.st1'))
        shutil.copy2(source, d.RUN/'states'/source.name)
        d.cmd(wait=8); d.press('1', .1, .1); d.press('F7', .1, 12)
        first = d.status()['frame']; d.cmd(wait=.7)
        if d.status()['frame'] == first: d.cmd(tap='p', wait=.7)
        d.results.update(cold_boot=False, exact_rom_state=True)
    else:
        for _ in range(120):
            if d.status()['map'] == 80: break
            d.press('Return', .4, .7)
        d.check('native main menu', d.status()['map'] == 80)
        d.cmd(wait=8)
        for _ in range(15):
            if d.status()['map'] == 34: break
            d.press('Shift_L', .4, 1.5)
    for _ in range(120):
        st = d.status()
        if st['map'] == 34 and st['frame'] > 180 and st['player']['state'] == 12 and not d.mem(0x807463B8,'u8') and not d.mem(0x807444EC,'u8'): break
        d.cmd(wait=.25)
    d.check('adventure ready', d.status()['map'] == 34 and d.status()['player']['state'] == 12, d.status())
    d.place([2940,500,2220], 2048, wait=2); d.press('c', .4, .8)

def select(char):
    for _ in range(6):
        if d.status()['character'] == char: break
        d.press('d', .25, .7)
    d.check('select character '+str(char), d.status()['character'] == char, d.status())

def charged_ring(char, wide, run):
    select(char)
    d.cmd(write=[{'address':0x807444C0, 'type':'u8', 'value':wide}], wait=.3)
    stock = d.status()['inventory'][3]
    d.cmd(down=['Control_L']); d.wait_frames(100,60)
    d.cmd(up=['Control_L'], tap='p', wait=.05)
    captured = False
    initialized = False
    ring = None
    details = None
    # Next advances one VI per frontend step: two steps per DK64 update.
    # Allow the native charge-release clip plus the complete ring lifetime.
    for frame in range(240):
        rings = [a for a in d.scene(f'ring-{run}-{frame}')['loaded_actors'] if a['type'] == 255]
        if rings:
            ring = int(rings[0]['pointer'],16)
            parent = d.mem(ring+0x11C)
            if parent:
                initialized = True
                if not captured and rings[0]['state'] >= 12:
                    model = d.mem(ring)
                    count = d.mem(0x807FBB30,'u16')
                    fields = d.cmd(read=[{'address':0x807FB630+i*12+off,'type':kind}
                        for i in range(count) for off,kind in ((0,'u16'),(4,'u32'))])[0]['memory']
                    keys = [fields[i] for i in range(0,len(fields),2) if fields[i+1] == model]
                    anim = d.mem(ring+4)
                    scale = d.cmd(read=[{'address':anim+i,'type':'f32'} for i in (0x34,0x38,0x3C)])[0]['memory']
                    rate = d.cmd(read=[{'address':ring+i,'type':'u32'} for i in (0x160,0x164)])[0]['memory']
                    rate = struct.unpack('>d',struct.pack('>II',*rate))[0]
                    details = {'parent':hex(parent),'cache_model_ids':keys,'scale':scale,'rate':rate,'lifetime':d.mem(ring+0x168,'u16')}
                    d.cmd(shot=f'ring-character-{char}-wide-{wide}-run-{run}')
                    expected = [0xAD,0xAE,0xD0,0xD1,0xCF,0xED][char]
                    d.check(f'native ring uses distinct correct model {char}/{wide}/{run}', keys == [expected] and parent == int(d.status()['player_pointer'],16), details)
                    d.check(f'native expansion and lifetime {char}/{wide}/{run}', abs(rate-1.09)<.00001 and details['lifetime']==25 and abs(scale[0]-scale[2])<.00001, details)
                    captured = True
        elif initialized:
            break
        d.cmd(tap='slash', wait=.03)
    d.check(f'ring rendered and cleaned up {char}/{wide}/{run}', captured and not rings, details)
    d.cmd(tap='p', wait=2); d.wait_player_ready(60)
    d.check(f'native cost and control restored {char}/{wide}/{run}', d.status()['inventory'][3] == stock-150 and d.status()['character'] == char, d.status())

try:
    d.start(); ready()
    cases = [(5,0),(0,0),(5,1)]
    if os.environ.get('DK64_COLORS_FOCUSED') != '1':
        cases += [(1,0),(2,0),(3,0),(4,0),(5,0)]
    d.results['cases'] = cases
    for run, (char,wide) in enumerate(cases):
        charged_ring(char,wide,run)
    d.results['complete'] = True
except Exception as exc:
    d.results['error'] = repr(exc)
    print('COLOR_TEST_ERROR',repr(exc),flush=True)
    try: d.cmd(up=['Control_L'],shot='color-test-failure')
    except Exception: pass
finally:
    (d.RUN/'logs'/d.REPORT_NAME).write_text(json.dumps(d.results,indent=2)+'\n')
    if d.proc and d.proc.poll() is None:
        d.proc.stdin.write('{"quit":true}\n'); d.proc.stdin.flush(); d.proc.wait(timeout=20)
