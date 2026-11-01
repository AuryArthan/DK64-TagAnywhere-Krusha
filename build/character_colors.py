"""Krusha identity effects derived from the approved startup silhouette."""
from collections import Counter
from pathlib import Path
import struct
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SHOCKWAVE_TEXTURE_IDS = tuple(range(7003, 7009))


def identity_color():
    with Image.open(ROOT / 'bin/Nintendo_Krusha.png') as image:
        image = image.convert('RGB')
        # The rightmost head is Krusha. Ignore black/antialiased background.
        grays = Counter(p for p in image.crop((image.width-38, 0, image.width, image.height)).getdata()
                        if p[0] == p[1] == p[2] and p[0] >= 100)
    return grays.most_common(1)[0][0]


def shockwave_payloads(rom, read_file):
    # spawnActor uses one-based model numbers: model 0xAD is file 0xAC.
    assert struct.unpack_from('>I', rom, 0x101C50 + (32+5)*4)[0] == 0xEC
    model = bytearray(read_file(rom, 5, 0xAC))
    assert len(model) == 0x308
    native_ids = struct.unpack_from('>6H', model, 0x2FC)
    assert native_ids == tuple(range(0x1321, 0x1327))
    struct.pack_into('>6H', model, 0x2FC, *SHOCKWAVE_TEXTURE_IDS)
    color = bytes(identity_color())
    textures = []
    for index in native_ids:
        assert read_file(rom, 25, SHOCKWAVE_TEXTURE_IDS[index-native_ids[0]]) == b''
        texture = bytearray(read_file(rom, 25, index))
        assert len(texture) == 32*32*4  # Native RGBA32; retain every alpha byte.
        for offset in range(0, len(texture), 4):
            texture[offset:offset+3] = color
        textures.append(bytes(texture))
    return [bytes(model)] + textures
