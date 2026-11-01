#!/usr/bin/python3
"""Controller-driven integration checks for the Krusha development ROM.

Uses logged RAM fixtures only to reach test locations. Game mechanics use normal
controller input. On completion/failure, accepts control.py JSON commands on stdin.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import struct
import zlib

ROOT = Path(__file__).resolve().parent.parent
ROM = Path(os.environ.get('DK64_TEST_ROM', ROOT / 'rom/dk64-krusha-dev.z64'))
DIGEST = hashlib.sha256(ROM.read_bytes()).hexdigest()
RUN = Path(os.environ.get('DK64_RUNTIME', ROOT / 'runtime/roms' / DIGEST)).resolve()
RUN.mkdir(parents=True, exist_ok=True)
(RUN / 'saves').mkdir(exist_ok=True)
# Native EEPROM is portable; emulator savestates are never imported across ROMs.
save = RUN / 'saves' / ('Donkey Kong 64 (local build)-' + hashlib.md5(ROM.read_bytes()).hexdigest()[:8].upper() + '.eep')
if not save.exists():
    seed = os.environ.get('DK64_TEST_SAVE')
    if not seed or not Path(seed).is_file():
        raise SystemExit('Set DK64_TEST_SAVE to a native EEPROM fixture with Speed Mode ON, or prepare this isolated profile in-game. No saves are shipped.')
    save.write_bytes(Path(seed).read_bytes())

results = {'rom_sha256': DIGEST, 'cold_boot': True,
           'fixtures': 'RAM positions / loading-zone redirects only; no character or move-code writes',
           'checks': []}
REPORT_NAME = 'krusha-tests.json'
proc = None

def start():
    global proc
    proc = subprocess.Popen(['/usr/bin/python3', str(ROOT / 'tools/control.py')], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, text=True, bufsize=1,
                            env={**os.environ, 'DK64_ROM': str(ROM)})
    print(proc.stdout.readline().strip(), flush=True)

def cmd(**command):
    proc.stdin.write(json.dumps(command) + '\n'); proc.stdin.flush()
    output = []
    while True:
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError('Controller stopped')
        row = json.loads(line)
        if 'error' in row:
            raise RuntimeError(row['error'])
        output.append(row)
        if 'ok' in row:
            return output

def status():
    return cmd(status=True)[0]

def wait_frames(count, timeout=30):
    """Wait for native game time in a stable map, including slow renderers."""
    first = status()['frame']
    deadline = time.monotonic() + timeout
    while ((status()['frame'] - first) & 0xFFFFFFFF) < count:
        if time.monotonic() >= deadline:
            raise RuntimeError('Native frame wait timed out')
        cmd(wait=.2)

def wait_player_ready(timeout=30):
    deadline = time.monotonic() + timeout
    while status()['player']['state'] not in (12, 13, 0x4E, 0x4F):
        if time.monotonic() >= deadline:
            raise RuntimeError('Player did not return to ordinary movement')
        cmd(wait=.25)

def mem(address, kind='u32'):
    return cmd(read=[{'address': address, 'type': kind}])[0]['memory'][0]

def press(key, seconds=.25, wait=.5, shot=None):
    args = dict(keys=[key], seconds=seconds, wait=wait)
    if shot: args['shot'] = shot
    return cmd(**args)

def combo(key, wait=1, shot=None):
    cmd(down=['z'], wait=.25)
    press(key, .25, wait, shot)
    cmd(up=['z'])

def check(name, condition, detail=None):
    row = {'name': name, 'passed': bool(condition), 'detail': detail}
    results['checks'].append(row)
    (RUN / 'logs' / REPORT_NAME).write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(row), flush=True)
    if not condition:
        raise AssertionError(name)

def checkpoint(slot, name):
    press(str(slot), .1, .1); press('F5', .1, .4)
    files = list((RUN / 'states').glob(f'Donkey*.st{slot}'))
    if files:
        (RUN / 'states' / (name + f'.st{slot}')).write_bytes(files[0].read_bytes())

def place(xyz, facing=0, wait=1.5):
    cmd(tap='p', wait=.05)
    cmd(position=xyz, facing=facing, wait=.05)
    cmd(tap='p', wait=wait)

def scene(name):
    return cmd(scene=name)[0]

def go(map_id):
    cmd(tap='p', wait=.05)
    cmd(fixture_map=map_id, wait=.05)
    cmd(tap='p', wait=5)
    check('fixture loaded map ' + str(map_id), status()['map'] == map_id, status())

def zone_position(map_id, destination=None):
    rom = (ROOT / 'rom/dk64.z64').read_bytes()
    base = 0x101C50
    table = base + struct.unpack_from('>I', rom, base + 18*4)[0]
    start, end = struct.unpack_from('>II', rom, table + map_id*4)
    data = rom[base+(start & 0x7FFFFFFF):base+(end & 0x7FFFFFFF)]
    if data[:2] == b'\x1f\x8b': data = zlib.decompress(data, 15+32)
    for i in range(struct.unpack_from('>H', data)[0]):
        off = 2 + i*0x38
        kind, dest = struct.unpack_from('>HH', data, off+0x10)
        if (destination is None and kind == 17) or (kind in (9,16) and dest == destination):
            return list(struct.unpack_from('>hhh', data, off))
    raise RuntimeError(f'No normal door to {destination} in {map_id}')

def shop(map_id, destination, name):
    place(zone_position(map_id, destination), wait=.1)
    for i in range(30):
        s = status()
        if s['map']==destination and s.get('player',{}).get('actor')==7: break
        cmd(wait=.2)
    check(name + ' entry as Krusha', status()['map']==destination and status()['character']==5, status())
    cmd(shot='final-' + name.lower() + '-inside')
    if name in ('Candy','Funky'):
        # Native first-visit introductions are unskippable by ordinary A input.
        press('f', 10, .1)
    for i in range(16):
        press('Shift_L', .2, .65)
        if status()['map'] != destination: break
    cmd(wait=3)
    if status()['map'] == destination:
        # These shops let the player walk to their normal exit after talking.
        place(zone_position(destination), wait=5)
    check(name + ' dialogue and exit', status()['map']==map_id and status()['character']==5, status())
    cmd(shot='final-' + name.lower() + '-outside')

def run_core():
    try:
        for i in range(50):
            if status()['map'] == 80: break
            press('Return', .3, .8)
        check('main menu reached', status()['map'] == 80)
        cmd(wait=6)
        for i in range(10):
            press('Shift_L', .4, 1.5)
            if status()['map'] in (34, 176): break
        cmd(wait=4)
        s = status(); check('cold boot into adventure', s['map'] == 34 and s['character'] == 0, s)
        place([2780, 500, 2260], 2048)
        checkpoint(0, 'krusha-build-dk-isles')
        press('a', wait=1, shot='final-krusha-entry')
        check('DK backwards to Krusha', status()['character'] == 5, status())
        for key, expected in [('d', [0,1,2,3,4,5]), ('a', [4,3,2,1,0,5])]:
            seen = []
            for kong in expected:
                press(key, wait=.65)
                seen.append(status()['character'])
            check('six character rotation ' + key, seen == expected, seen)
        checkpoint(1, 'krusha-build-krusha-isles')
        # Barrel entry is now enabled for Krusha. Keep this movement/camera
        # fixture on open ground rather than jumping into the nearby barrel.
        place([2940,500,2220], 2048, wait=1)
        before = status()
        press('Down', .6, .1, 'final-running')
        cmd(keys=['Shift_L', 'Down'], seconds=.3, wait=.05, shot='final-jumping')
        s = status(); check('running and jumping advance gameplay', s['frame'] > before['frame'] and s['character'] == 5, s)
        cmd(wait=1)
        combo('i', wait=.2, shot='final-roar')
        check('vocal instrument enters safely', status()['player']['state'] == 0x67 and status()['character'] == 5, status())
        cmd(wait=5)
        check('vocal instrument returns to gameplay', status()['player']['state'] == 12, status())
        combo('k', wait=.8, shot='final-camera')
        check('camera enters fairy view', status()['player']['state'] == 4, status())
        film = status()['inventory'][4]
        press('Control_L', wait=.8, shot='final-photo')
        cmd(wait=3.5)
        check('camera takes photograph', status()['inventory'][4] == film - 1, status())
        press('i', wait=1)
        check('camera exits to gameplay', status()['player']['state'] == 12, status())
        press('Return', wait=1, shot='final-pause-menu')
        press('Return', wait=1)
        check('pause menu returns safely', status()['character'] == 5 and status()['frame'] > s['frame'], status())
        place([2803, 505, 2400], wait=1.5)
        place([3483, 505, 3150], wait=1.5)
        inventory = status()['inventory']
        press('z', .4, 4, 'final-bananaport')
        s = status()
        check('bananaport without identity or inventory change', s['character'] == 5 and abs(s['player']['x']-2803)<50 and abs(s['player']['z']-2400)<50 and s['inventory']==inventory, s)
        place([2960,1038,1928], wait=3)
        # Test setup can cause landing damage; refill health in the isolated test save.
        cmd(write=[{'address':'0x807FCC4B','type':'u8','value':12}])
        press('Control_L', wait=1.5, shot='final-boulder-lift')
        s = status(); p = int(s['player_pointer'], 16)
        held = mem(p+0x32C)
        check('Krusha lifts native boulder', s['player']['state']==0x48 and held != 0 and mem(held+0x58)==61, s)
        press('Left', .3, .2, 'final-boulder-carry')
        press('d', wait=.4)
        check('tagging blocked during heavy carry', status()['character'] == 5)
        press('z', wait=1.5, shot='final-boulder-drop')
        check('Krusha drops boulder', mem(p+0x32C)==0 and status()['player']['state']==12, status())
        nearby = [a for a in scene('after-boulder-drop')['actors'] if a['type']==61]
        print(json.dumps({'boulders_after_drop':nearby}), flush=True)
        checkpoint(2, 'krusha-build-boulders')
        rock = min(nearby, key=lambda a: sum((a['xyz'][i]-status()['player'][axis])**2 for i,axis in enumerate('xyz')))
        place([rock['xyz'][0], rock['xyz'][1], rock['xyz'][2]-28], wait=2)
        press('Control_L', wait=1.5)
        check('boulder can be picked up again', status()['player']['state']==0x48, status())
        press('Control_L', wait=2, shot='final-boulder-throw')
        check('Krusha throws boulder', mem(p+0x32C)==0 and status()['player']['state']==12, status())
        place([2254, 450, 2941], wait=3)
        s = status(); check('Krusha swimming', s['player']['state'] in (0x4E,0x4F), s)
        press('z', .4, .5)
        cmd(keys=['Up','Shift_L'], seconds=.5, wait=.2, shot='final-swimming')
        check('Krusha dives and swims', status()['player']['state']==0x4F and status()['player']['y'] < 440, status())
        # Return to a dry native loading zone before changing test maps.
        place([2780, 500, 2260], wait=2)
        go(7)
        place([1000,280,1013], wait=2)
        krusha_coins = mem(0x807FC950+5*0x5E+6, 'u16')
        chunky_coins = mem(0x807FC950+4*0x5E+6, 'u16')
        cmd(shot='final-krusha-cannot-collect-green-coins')
        check('Krusha collects no coins', krusha_coins==0 and chunky_coins==0, [krusha_coins,chunky_coins])
        press('a', wait=2, shot='final-chunky-collects-preserved-coins')
        check('green coins remain for Chunky', mem(0x807FC950+4*0x5E+6,'u16')>chunky_coins, status())
        press('d', wait=1)
        place([2909,343,2035], wait=2)
        check('Krusha collects no colored bananas', all(mem(0x807FC950+5*0x5E+0xA+i*2,'u16')==0 for i in range(14)))
        # Shared orange supply: use a non-full inventory so a false pickup is visible.
        cmd(write=[{'address':'0x807FCC44','type':'u16','value':10}])
        ammo_before = status()['inventory'][0]
        place([1145,288,1987], wait=2)
        check('Krusha collects shared orange pickup separately from bazooka ammo',
              status()['inventory'][2]>10 and status()['inventory'][0]==ammo_before, status())
        press('a', wait=2)
        oranges_before = status()['inventory'][2]
        place([1109,288,2001], wait=2)
        check('another shared orange remains collectible by Chunky', status()['inventory'][2]>oranges_before, status())
        press('d', wait=1)
        checkpoint(3, 'krusha-build-japes-pickup-tests')
        place([910,280,835], facing=0, wait=2)
        press('c', .7, .3)
        cmd(keys=['Up','Shift_L'], seconds=.3, wait=.05)
        press('Up', .5, .05, 'final-tree-climbing')
        check('Krusha climbs tree', status()['player']['state']==0x59, status())
        press('Shift_L', .3, 1)
        shop(7,5,'Cranky')
        go(30)
        shop(30,25,'Candy')
        shop(30,1,'Funky')
        checkpoint(4, 'krusha-build-after-shops')
        results['complete'] = True
        (RUN / 'logs' / REPORT_NAME).write_text(json.dumps(results, indent=2)+'\n')
        print('ALL_CHECKS_COMPLETE; interactive controller ready', flush=True)
    except Exception as exc:
        results['error'] = str(exc)
        (RUN / 'logs' / REPORT_NAME).write_text(json.dumps(results, indent=2) + '\n')
        print(json.dumps({'test_error': str(exc)}), flush=True)
        try: cmd(shot='test-failure')
        except Exception: pass
        print('INTERACTIVE_CONTROLLER_READY', flush=True)

def interactive():
    try:
        for line in sys.stdin:
            command = json.loads(line)
            if command.get('quit'):
                if proc.poll() is None:
                    proc.stdin.write(json.dumps(command)+'\n'); proc.stdin.flush()
                break
            print(json.dumps(cmd(**command)), flush=True)
    finally:
        if proc.poll() is None:
            proc.stdin.write('{"quit":true}\n'); proc.stdin.flush()
            proc.wait(timeout=15)

if __name__ == '__main__':
    start()
    run_core()
    interactive()
