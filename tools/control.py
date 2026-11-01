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
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
TOOL_ROOT = Path(os.environ.get("DK64_TOOL_ROOT", ROOT / "tools"))
ROM = Path(os.environ.get("DK64_ROM", ROOT / "rom/dk64-krusha-dev.z64"))
ROM_HASH = hashlib.sha256(ROM.read_bytes()).hexdigest()
RUN = ROOT / "runtime"
if ROM_HASH != "b6347d9f1f75d38a88d829b4f80b1acf0d93344170a5fbe9546c484dae416ce3":
    RUN = RUN / "roms" / ROM_HASH
RUN = Path(os.environ.get("DK64_RUNTIME", RUN)).resolve()
ENV = os.environ.copy()
ENV.update(DISPLAY=ENV.get("DK64_DISPLAY", ":99"), SDL_AUDIODRIVER="dummy",
           LIBGL_ALWAYS_SOFTWARE="1", DK64_AUDIO="dummy")
ENV["LD_LIBRARY_PATH"] = str(TOOL_ROOT / "emulator/usr/lib/x86_64-linux-gnu")
CAPTURE_AUDIO = os.environ.get('DK64_CAPTURE_AUDIO') == '1'
RESOLUTION = os.environ.get('DK64_RESOLUTION', '640x480')
WIDTH, HEIGHT = (int(v) for v in RESOLUTION.split('x'))
AUDIO_RAW = RUN / 'audio/game-audio.raw'
if CAPTURE_AUDIO:
    ENV.update(SDL_AUDIODRIVER='disk', SDL_DISKAUDIOFILE=str(AUDIO_RAW),
               SDL_DISKAUDIODELAY='46', DK64_AUDIO='mupen64plus-audio-sdl.so')
XDOTOOL = str(TOOL_ROOT / "emulator/usr/bin/xdotool")

def xdo(*args):
    return subprocess.check_output([XDOTOOL, *args], env=ENV, text=True, timeout=5).strip()

def main():
    for folder in ("logs", "screenshots", "videos"):
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
            game_args = ['--verbose'] if CAPTURE_AUDIO else []
            game = subprocess.Popen([str(ROOT / "tools/play.sh"), *game_args, *sys.argv[1:]], env=ENV, stdout=elog, stderr=subprocess.STDOUT)
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
            window = windows[-1]
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
                    if any(cmd.get(k) for k in ('keys', 'tap', 'down', 'up')):
                        # Video mode changes can recreate/refocus the SDL
                        # window. Target the current private-display window
                        # before synthetic keyboard input, never the desktop.
                        visible = xdo('search', '--onlyvisible', '--class', '.').splitlines()
                        window = visible[-1]
                        xdo('windowfocus', '--sync', window)
                    if any(k in cmd for k in ('status', 'read', 'write', 'position', 'scene', 'fixture_map')):
                        if memory is None:
                            spec = importlib.util.spec_from_file_location('emulator_memory', ROOT / 'tools/emulator-memory.py')
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
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
