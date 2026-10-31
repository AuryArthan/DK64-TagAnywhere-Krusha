#!/usr/bin/python3
"""Private X display plus a line-oriented controller. Commands are JSON objects.

{"keys":["Up","Shift_L"],"seconds":0.5,"shot":"jump"}
{"tap":"Return","wait":2,"shot":"menu"}
{"shot":"current"} / {"wait":10} / {"quit":true}
"""
import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import time
import socket
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
TOOL_ROOT = Path(os.environ.get("DK64_TOOL_ROOT", ROOT / "tools"))
ROM = Path(os.environ.get("DK64_ROM", ROOT / "rom/dk64-krusha-dev.z64"))
ROM_HASH = hashlib.sha256(ROM.read_bytes()).hexdigest()
RUN = ROOT / "runtime/libretro"
if ROM_HASH != "b6347d9f1f75d38a88d829b4f80b1acf0d93344170a5fbe9546c484dae416ce3":
    RUN = RUN / "roms" / ROM_HASH
RUN = Path(os.environ.get("DK64_RUNTIME", RUN)).resolve()
ENV = os.environ.copy()
ENV.update(DISPLAY=ENV.get("DK64_DISPLAY", ":99"), SDL_AUDIODRIVER="dummy",
           LIBGL_ALWAYS_SOFTWARE="1", DK64_AUDIO="dummy")
ENV["LD_LIBRARY_PATH"] = str(TOOL_ROOT / "emulator/usr/lib/x86_64-linux-gnu")
LIBRETRO_ROOT = Path(os.environ.get("DK64_LIBRETRO_ROOT", ROOT/"runtime/libretro-tools")).resolve()
CORE = LIBRETRO_ROOT/'core/mupen64plus_next_libretro.so'
if hashlib.sha256(CORE.read_bytes()).hexdigest() != "26f2b4ec722558d77bc9e1582e62ab80c84190bb20dfadc48a148e6210c8775e":
    raise SystemExit('This test controller requires the pinned core; revalidate RDRAM lookup before updating it.')
ENV.update(XDG_CONFIG_HOME=str(RUN/"xdg-config"), XDG_DATA_HOME=str(RUN/"xdg-data"), XDG_CACHE_HOME=str(RUN/"xdg-cache"))
CAPTURE_AUDIO = os.environ.get('DK64_CAPTURE_AUDIO') == '1'
RESOLUTION = os.environ.get('DK64_RESOLUTION', '640x480')
WIDTH, HEIGHT = (int(v) for v in RESOLUTION.split('x'))
AUDIO_RAW = RUN / 'audio/game-audio.raw'
if CAPTURE_AUDIO:
    ENV.update(SDL_AUDIODRIVER='disk', SDL_DISKAUDIOFILE=str(AUDIO_RAW),
               SDL_DISKAUDIODELAY='46', DK64_AUDIO='mupen64plus-audio-sdl.so')
XDOTOOL = str(TOOL_ROOT / "emulator/usr/bin/xdotool")

held = set()
PADFILE = RUN / 'gamepad.bin'
def pad_update():
    import struct
    bits={'Shift_L':0,'Control_L':1,'Return':3,'w':4,'s':5,'a':6,'d':7,'x':10,'c':11,'z':12}
    mask=sum(1<<n for k,n in bits.items() if k in held)
    value=lambda minus,plus:32767*((plus in held)-(minus in held))
    data=struct.pack('<5i',mask,value('Left','Right'),value('Up','Down'),value('j','l'),value('i','k'))
    with PADFILE.open('r+b' if PADFILE.exists() else 'wb') as stream: stream.write(data)
def network(command):
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        sock.sendto((command+'\n').encode(),('127.0.0.1',55357))

def xdo(*args):
    hotkeys={'p':'PAUSE_TOGGLE','slash':'FRAMEADVANCE','F5':'SAVE_STATE','F7':'LOAD_STATE',
             'F9':'STATE_SLOT_PLUS','F8':'STATE_SLOT_MINUS','Escape':'QUIT'}
    if args and args[0] in ('keydown','keyup','key'):
        for key in args[1:]:
            if key=='f':network('FAST_FORWARD')
            elif key in hotkeys:
                if args[0]!='keyup':network(hotkeys[key])
            elif args[0]=='keydown':held.add(key)
            elif args[0]=='keyup':held.discard(key)
        pad_update()
        return ''
    return subprocess.check_output([XDOTOOL, *args], env=ENV, text=True, timeout=5).strip()

def main():
    for folder in ("logs", "screenshots", "videos", "states", "saves", "system"):
        (RUN / folder).mkdir(parents=True, exist_ok=True)
    if CAPTURE_AUDIO:
        AUDIO_RAW.parent.mkdir(exist_ok=True)
    with (RUN / "logs/xvfb.log").open("w") as xlog, (RUN / "logs/emulator.log").open("w") as elog, (RUN / "logs/actions.jsonl").open("a") as actions:
        display = subprocess.Popen([str(TOOL_ROOT / "emulator/usr/bin/Xvfb"), ENV["DISPLAY"],
                                    "-screen", "0", RESOLUTION + "x24", "-nolisten", "tcp", "-noreset", "-ac"],
                                   env=ENV, stdout=xlog, stderr=subprocess.STDOUT)
        game = None
        recording = None
        try:
            time.sleep(1)
            if display.poll() is not None:
                raise RuntimeError("Xvfb failed; see runtime/logs/xvfb.log")
            pad_update()
            ENV['DK64_PADFILE']=str(PADFILE)
            options = RUN / 'core-options.cfg'
            if not options.exists(): options.write_text('mupen64plus-aspect = "4:3"\nmupen64plus-43screensize = "320x240"\nmupen64plus-rdp-plugin = "gliden64"\nmupen64plus-CountPerOp = "1"\nmupen64plus-ThreadedRenderer = "False"\n')
            config = RUN / 'retroarch.cfg'
            entries = {
                'video_driver':'glcore', 'audio_driver':'sdl2', 'video_fullscreen':'true','video_fullscreen_x':str(WIDTH),'video_fullscreen_y':str(HEIGHT),'video_windowed_fullscreen':'false',
                'video_window_custom_size_enable':'true','video_window_width':str(WIDTH), 'video_window_height':str(HEIGHT),
                'video_scale_integer':'false', 'video_force_aspect':'false', 'video_vsync':'true',
                'pause_nonactive':'false', 'config_save_on_exit':'false', 'input_driver':'sdl2','video_context_driver':'sdl',
                'input_joypad_driver':'null', 'input_autodetect_enable':'false',
                'menu_driver':'rgui', 'menu_enable_widgets':'false', 'video_font_enable':'false',
                'libretro_info_path':str(LIBRETRO_ROOT/'info'), 'libretro_directory':str(LIBRETRO_ROOT/'core'), 'sort_savefiles_enable':'false','sort_savestates_enable':'false','system_directory':str(RUN/'system'),'core_options_path':str(options),'savefile_directory':str(RUN/'saves'),
                'savestate_directory':str(RUN/'states'), 'screenshot_directory':str(RUN/'screenshots'),
                'input_player1_b':'lshift','input_player1_y':'lctrl','input_player1_l2':'z',
                'input_player1_r':'c','input_player1_l':'x','input_player1_start':'enter',
                'input_player1_left':'a','input_player1_right':'d','input_player1_up':'w','input_player1_down':'s',
                'input_player1_l_x_minus':'left','input_player1_l_x_plus':'right',
                'input_player1_l_y_minus':'up','input_player1_l_y_plus':'down',
                'input_player1_r_x_minus':'j','input_player1_r_x_plus':'l',
                'input_player1_r_y_minus':'i','input_player1_r_y_plus':'k',
                'input_pause_toggle':'p','input_frame_advance':'slash','input_hold_fast_forward':'f',
                'input_save_state':'f5','input_load_state':'f7',
                'input_state_slot_increase':'f9','input_state_slot_decrease':'f8',
                'input_exit_emulator':'escape','savestate_auto_save':'false',
                'savestate_auto_load':'false','input_enable_hotkey':'nul', 'core_info_savestate_bypass':'true', 'network_cmd_enable':'true','network_cmd_port':'55357',
            }
            config.write_text(''.join(k+' = "'+v+'"\n' for k,v in entries.items()))
            slot = 0
            game = subprocess.Popen([str(LIBRETRO_ROOT/'retroarch/usr/bin/retroarch'),
                '-v','-c',str(config),'-L',str(LIBRETRO_ROOT/'core/mupen64plus_next_test_libretro.so'),
                str(ROM)],env=ENV,stdout=elog,stderr=subprocess.STDOUT)
            time.sleep(float(os.environ.get('DK64_BOOT_WAIT', '4'))) # Optional early splash capture; diagnostics wait for RDRAM themselves.
            deadline = time.monotonic() + 20
            windows = []
            while not windows and time.monotonic() < deadline:
                if game.poll() is not None:
                    raise RuntimeError("Emulator exited before opening a window; see logs/emulator.log")
                try:
                    windows = xdo("search", "--onlyvisible", "--class", ".").splitlines()
                except subprocess.CalledProcessError:
                    time.sleep(.25)
            if not windows:
                raise RuntimeError("Emulator did not open a window; see logs/emulator.log")
            details=[(w,xdo('getwindowname',w)) for w in windows]
            (RUN/'logs/windows.json').write_text(json.dumps(details))
            window = next((w for w,title in details if 'RetroArch' in title),windows[0])
            xdo("windowsize", "--sync", window, str(WIDTH), str(HEIGHT))
            xdo("windowfocus", "--sync", window)
            print(json.dumps({"ready": True, "window": window}), flush=True)
            memory = None
            for line in sys.stdin:
                try:
                    cmd = json.loads(line)
                    actions.write(json.dumps({"time": time.time(), "rom_sha256": ROM_HASH, **cmd}) + "\n")
                    actions.flush()
                    if cmd.get("quit"):
                        break
                    if game.poll() is not None:
                        raise RuntimeError(f"Emulator exited with code {game.returncode}; see logs/emulator.log")
                    if any(k in cmd for k in ('status', 'read', 'write', 'position', 'scene', 'fixture_map')):
                        if memory is None:
                            spec = importlib.util.spec_from_file_location('emulator_memory', ROOT / 'tools/emulator-memory.py')
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            def libretro_init(self, pid):
                                import struct
                                self.fd = os.open(f'/proc/{pid}/mem', os.O_RDWR)
                                rows=Path(f'/proc/{pid}/maps').read_text().splitlines()
                                core=next(int(line.split('-')[0],16) for line in rows if 'mupen64plus_next_libretro.so' in line and line.split()[2]=='00000000')
                                # Pinned official core SHA256 26f2b4ec...c8775e.
                                self.base=struct.unpack('<Q',os.pread(self.fd,8,core+0xa25ed48))[0]
                                if not self.base: raise RuntimeError('Libretro RDRAM not ready')
                                if self.u32(0x80000318) not in [0x400000,0x800000]: raise RuntimeError('Unexpected core memory layout')
                            module.Memory.__init__=libretro_init
                            memory = module.Memory(game.pid)
                        for item in cmd.get('write', []):
                            memory.write(item['address'], item['value'], item.get('type', 'u32'))
                        if 'position' in cmd:
                            memory.position(cmd['position'], cmd.get('facing'))
                        if 'fixture_map' in cmd:
                            memory.transition_fixture(cmd['fixture_map'], cmd.get('fixture_exit', 0))
                        if cmd.get('scene'):
                            scene = memory.scene()
                            (RUN / 'logs' / (Path(str(cmd['scene'])).name + '.json')).write_text(json.dumps(scene, indent=2))
                            print(json.dumps(scene), flush=True)
                        if cmd.get('status'):
                            (RUN/'logs/last-status.json').write_text(json.dumps(memory.status()))
                            print(json.dumps(memory.status()), flush=True)
                        if cmd.get('read'):
                            print(json.dumps({'memory': [memory.read(item['address'], item.get('type', 'u32'))
                                                       for item in cmd['read']]}), flush=True)
                    if cmd.get("down"):
                        xdo("keydown", *cmd["down"])
                    if cmd.get("up"):
                        xdo("keyup", *cmd["up"])
                    if cmd.get("record"):
                        if recording is not None:
                            raise ValueError("A recording is already running")
                        path = RUN / "videos" / (Path(cmd["record"]).name + ".mp4")
                        recording = subprocess.Popen(["ffmpeg", "-nostats", "-y", "-f", "x11grab", "-video_size", RESOLUTION,
                            "-framerate", "30", "-i", ENV["DISPLAY"], "-an", "-c:v", "libx264", "-preset", "ultrafast",
                            "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+frag_keyframe+empty_moov", str(path)], env=ENV,
                            stdin=subprocess.PIPE, stdout=elog, stderr=subprocess.STDOUT)
                    if cmd.get("stop_record") and recording is not None:
                        recording.communicate(b"q", timeout=10)
                        recording = None
                    keys = cmd.get("keys", [])
                    if len(keys)==1 and keys[0].isdigit():
                        target=int(keys[0])
                        while slot!=target:
                            key='F9' if target>slot else 'F8'
                            xdo('key',key);time.sleep(.25);slot+=1 if target>slot else -1
                        keys=[]
                    if keys:
                        xdo("keydown", *keys)
                        try:
                            time.sleep(min(float(cmd.get("seconds", 0.1)), 55))
                        finally:
                            xdo("keyup", *keys)
                    if cmd.get("tap"):
                        xdo("keydown", cmd["tap"])
                        time.sleep(0.1)
                        xdo("keyup", cmd["tap"])
                    time.sleep(min(float(cmd.get("wait", 0.1)), 55))
                    result = {"ok": True, "running": game.poll() is None}
                    if cmd.get('audio_offset'):
                        result['audio_bytes'] = AUDIO_RAW.stat().st_size if AUDIO_RAW.exists() else 0
                    if cmd.get("shot"):
                        name = Path(cmd["shot"]).name
                        path = RUN / "screenshots" / (name + ".png")
                        subprocess.run(["import", "-window", window, str(path)], env=ENV, check=True, timeout=10)
                        result["screenshot"] = str(path)
                    print(json.dumps(result), flush=True)
                except Exception as exc:
                    print(json.dumps({"error": str(exc)}), flush=True)
        finally:
            if recording is not None:
                recording.communicate(b"q", timeout=10)
            if game is not None and game.poll() is None:
                try:
                    xdo("key", "Escape")
                    game.wait(timeout=10)
                except Exception:
                    game.terminate()
                    game.wait(timeout=5)
            display.terminate()
            display.wait(timeout=5)

if __name__ == "__main__":
    main()
