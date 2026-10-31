import os
#!/usr/bin/python3
"""Create an isolated Mupen game database entry for a modified DK64 USA ROM."""
import hashlib
from pathlib import Path
import shutil
import sys

rom, destination = map(Path, sys.argv[1:])
data = rom.read_bytes()
if data[:4] != bytes.fromhex("80371240") or data[0x3E] != 0x45 or data[0x20:0x34].rstrip(b" \0") != b"DONKEY KONG 64":
    raise SystemExit("Expected a big-endian DK64 USA ROM")
source = Path(os.environ.get("DK64_TOOL_ROOT", Path(__file__).resolve().parent)) / "emulator/usr/share/games/mupen64plus"
destination.mkdir(parents=True, exist_ok=True)
shutil.copytree(source, destination, dirs_exist_ok=True)
md5 = hashlib.md5(data).hexdigest().upper()
with (destination / "mupen64plus.ini").open("a") as output:
    output.write(f"\n[{md5}]\nGoodName=Donkey Kong 64 (local build)\n"
        f"CRC={data[0x10:0x14].hex().upper()} {data[0x14:0x18].hex().upper()}\n"
        "RefMD5=9EC41ABF2519FC386CADD0731F6E868C\n"
        "SaveType=Eeprom 16KB\nCountPerOp=1\nPlayers=4\nRumble=Yes\n")
