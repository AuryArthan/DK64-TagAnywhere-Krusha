#!/usr/bin/python3
"""Check built identity-effect assets without launching an emulator."""
from pathlib import Path
import hashlib
import json
import struct
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'build'))
from barrel_assets import read_file, make_model, encode_face
from character_colors import identity_color, SHOCKWAVE_TEXTURE_IDS
from PIL import Image

source = (ROOT / 'rom/dk64.z64').read_bytes()
target = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'rom/dk64-krusha-dev.z64').read_bytes()
assert hashlib.sha1(source).hexdigest() == 'cf806ff2603640a748fca5026ded28802f1f4a50'
checks = []
def check(name, passed):
    checks.append({'name': name, 'passed': bool(passed)})
    assert passed, name

check('approved silhouette gray', identity_color() == (173, 173, 173))
original = read_file(source, 5, 0xAC)
model = read_file(target, 27, 3)
check('native ring geometry/materials unchanged', model[:0x2FC] == original[:0x2FC])
check('six separate texture references', struct.unpack_from('>6H', model, 0x2FC) == SHOCKWAVE_TEXTURE_IDS)
for frame in range(6):
    old = read_file(source, 25, 0x1321 + frame)
    new = read_file(target, 27, 4 + frame)
    check(f'frame {frame}: native alpha/fade unchanged', len(new) == 4096 and new[3::4] == old[3::4])
    check(f'frame {frame}: exact neutral RGB', all(new[i:i+3] == b'\xad\xad\xad' for i in range(0, len(new), 4)))
for index in (0xAC, 0xAD, 0xCE, 0xCF, 0xD0):
    check(f'original model {index:x} untouched', read_file(source, 5, index) == read_file(target, 5, index))
    native = read_file(source, 5, index)
    # Native models store their texture count at 0x20 and references at EOF.
    count = native[0x20]
    ids = struct.unpack_from('>%dH' % count, native, len(native) - count * 2)
    check(f'original model {index:x} textures untouched', all(read_file(source, 25, i) == read_file(target, 25, i) for i in ids))
barrel, _ = make_model(read_file(source, 5, 0xC0))
check('six-face barrel payload unchanged', read_file(target, 27, 0) == barrel)
halves = encode_face(Image.open(ROOT / 'assets/krusha/barrel/krusha-face-64.png'))
check('approved barrel portrait payloads unchanged', all(read_file(target, 27, i+1) == half for i, half in enumerate(halves)))
check('custom asset table has ten files', struct.unpack_from('>I', target, 0x101C50 + (32+27)*4)[0] == 10)
print(json.dumps({'rom_sha256': hashlib.sha256(target).hexdigest(), 'complete': True, 'checks': checks}, indent=2))
