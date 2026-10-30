"""Six-face tag barrel, using the approved T portrait and native materials.

Keep the original model and texture table untouched. Three uncompressed files in
previously unused pointer table 27 are loaded through a narrow resident hook.
"""
from pathlib import Path
import hashlib
import json
import math
import struct
import zlib
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets/krusha/barrel'
TABLE_BASE = 0x101C50
CUSTOM_ROM = 0x02080000
CUSTOM_TABLE = 27
TEXTURE_IDS = (7001, 7002)
SCALE = 1.15


def prepare_startup_logo():
    """Native asset composition: retain the existing five silhouettes/colours."""
    original = Image.open(ROOT/'bin/Nintendo.png').convert('RGBA')
    assert original.size == (192,48)
    # Preserve all original pixels, including antialiased edges and spacing.
    # Width is a multiple of four for the native unrolled framebuffer copy.
    result = Image.new('RGBA',(236,48),(0,0,0,255))
    result.paste(original,(0,0))
    face = Image.open(ASSETS/'krusha-face-source.png').convert('RGBA')
    mask = face.getchannel('A').point(lambda a:255 if a>=128 else 0)
    mask = mask.crop(mask.getbbox()).resize((37,37),Image.Resampling.LANCZOS)
    gray = Image.new('RGBA',(37,37),(173,173,173,255))
    result.paste(gray,(192,5),mask)
    assert result.crop((0,0,192,48)).tobytes() == original.tobytes()
    result.save(ROOT/'bin/Nintendo_Krusha.png')


def read_file(rom, table, index):
    u = lambda p: struct.unpack_from('>I', rom, p)[0]
    pointer = TABLE_BASE + u(TABLE_BASE + table * 4)
    a, b = (TABLE_BASE + (u(pointer + i * 4) & 0x7FFFFFFF) for i in (index, index + 1))
    data = rom[a:b]
    return zlib.decompress(data, 15 + 32) if data[:2] == b'\x1f\x8b' else data


def encode_face(image):
    """Native portrait storage is upside-down, split into 32x64 halves."""
    assert image.size == (64, 64)
    image = image.convert('RGBA').transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    halves = []
    for start in (0, 32):
        result = bytearray()
        for y in range(64):
            for x in range(start, start + 32):
                r, g, b, a = image.getpixel((x, y))
                value = ((r >> 3) << 11) | ((g >> 3) << 6) | ((b >> 3) << 1) | (a >= 128)
                result.extend(struct.pack('>H', value))
        halves.append(bytes(result))
    return halves


def make_model(native):
    vertices = bytearray()
    commands = []
    def cmd(a, b=0): commands.append((a, b))
    def vertex(x, y, z, u, v):
        vertices.extend(struct.pack('>hhhHhh4B', round(x), round(y), round(z), 0,
                                    round(u), round(v), 254, 254, 254, 255))
    def load(offset, count): cmd(0x01000000 | (count << 12) | (count << 1), 0x03000000 + offset)
    def tri2(a, b, c, d, e, f):
        cmd(0x06000000 | (a*2 << 16) | (b*2 << 8) | c*2, (d*2 << 16) | (e*2 << 8) | f*2)
    def pair_texture(index):
        cmd(0xE7000000); cmd(0xFD100000, index); cmd(0xE6000000)
        cmd(0xF3000000, 0x077FF100); cmd(0xE7000000); cmd(0xE3001001)

    # Retain native bulge, wood and inset end caps. Twelve facets replace ten,
    # giving six equal portrait cells on a barrel enlarged by the allowed 15%.
    radius = [round(90*SCALE), round(120*SCALE), round(120*SCALE), round(90*SCALE)]
    ys = [round(y*SCALE) for y in (6, 58, 110, 162)]
    # Keep the underlying question mark at native physical size too. Enlarging
    # it with the shell would expose its red top/dot beyond unlocked portraits.
    # The outer metal texels extend into the extra height using T clamp.
    vs = [round((y-19)*2048/156) for y in ys]
    shell_offsets = []
    for side in range(12):
        shell_offsets.append(len(vertices))
        # Native first-sector ordering, winding and 16-pixel wood repeats.
        for column, row in [(0,2),(0,3),(1,3),(1,2),(0,1),(1,1),(0,0),(1,0)]:
            theta = math.radians((side + column)*30)
            u = (512 if side % 2 == 0 else 1024) - column*512
            vertex(radius[row]*math.cos(theta),ys[row],radius[row]*math.sin(theta),u,vs[row])
    caps = []
    for bottom in (False, True):
        caps.append(len(vertices))
        for i in range(12):
            theta = math.radians((i if bottom else -i)*30)
            vertex(93*SCALE*math.cos(theta), (18 if bottom else 149)*SCALE,
                   93*SCALE*math.sin(theta),704-704*math.cos(theta),704+704*math.sin(theta))

    # Native bones/masks: Chunky=1, Diddy=2, DK=3, Lanky=4, Tiny=5.
    # Place them in playable-character order. The root-bound sixth portrait is
    # always available; it does not consume a locked-Kong mesh or skeleton bone.
    centres = {'dk':0,'diddy':60,'lanky':120,'tiny':180,'chunky':240,'krusha':300}
    native_groups = [('chunky',0x4A0),('diddy',0x5A0),('dk',0x6A0),('lanky',0x7A0),('tiny',0x8A0)]
    offsets = {}
    # Keep original 156-unit portrait height. Include shell profile breakpoints
    # in the face mesh to avoid sinking a decal into the barrel at its bulge.
    face_y = [19, ys[1], ys[2], 175]
    def radial(y):
        for i in range(3):
            if ys[i] <= y <= ys[i+1]:
                return radius[i] + (radius[i+1]-radius[i])*(y-ys[i])/(ys[i+1]-ys[i])
        raise ValueError(y)
    for name, source_offset in native_groups + [('krusha',0x6A0)]:
        offsets[name] = len(vertices)
        for i in range(16):
            x,y,z,flag,u,v,*colour = struct.unpack_from('>hhhHhh4B',native,40+source_offset+i*16)
            row = (6,58,110,162).index(y)
            y = face_y[row]
            full_u = (i//8)*32 + u/32
            theta = math.radians(centres[name]+30-full_u*60/64)
            r = radial(y)
            vertex(r*math.cos(theta), y, r*math.sin(theta),u,(y-face_y[0])*2048/156)

    # Native material setup for the shell.
    commands.extend(struct.iter_unpack('>II',native[0xA68:0xAF8]))
    commands = [(a, b | 0x00080000 if a == 0xF5101000 else b) for a,b in commands]
    for off in shell_offsets:
        load(off,8)
        tri2(0,1,2,0,2,3); tri2(4,0,3,4,3,5); tri2(6,4,5,6,5,7)
    def cap(off, initial):
        if initial:
            commands.extend(struct.iter_unpack('>II',native[0xBF8:0xC38]))
        else:
            commands.extend(struct.iter_unpack('>II',native[0x1150:0x11E0]))
        load(off,12)
        for i in range(1,11,2): tri2(0,i,i+1,0,i+1,i+2)
    cap(caps[0],True)

    # Krusha uses the root matrix, so the native six-bone hierarchy and its
    # allocation sizes remain unchanged. Native masked faces follow untouched.
    prefix = list(struct.iter_unpack('>II',native[0xD38:0xDC8]))
    for a,b in prefix:
        if a == 0xFD100000: b = TEXTURE_IDS[0]
        if a == 0xDA380003: b = 0x04000000
        cmd(a,b)
    load(offsets['krusha'],16)
    tri2(0,1,2,0,2,3);tri2(4,0,3,4,3,5);tri2(6,4,5,6,5,7)
    pair_texture(TEXTURE_IDS[1])
    tri2(8,9,10,8,10,11);tri2(12,8,11,12,11,13);tri2(14,12,13,14,13,15)
    face_bytes = bytearray(native[0xC60:0x1150])
    old_to_new = {old:offsets[name] for name,old in native_groups}
    for i in range(0,len(face_bytes),8):
        a,b = struct.unpack_from('>II',face_bytes,i)
        if a>>24 == 1:
            assert b&0xFFFFFF in old_to_new
            struct.pack_into('>I',face_bytes,i+4,0x03000000+old_to_new[b&0xFFFFFF])
    commands.extend(struct.iter_unpack('>II',face_bytes))
    cap(caps[1],False)
    cmd(0xDF000000)

    head = struct.unpack_from('>I',native,0)[0]
    header = bytearray(native[:40])
    dl_start = 40+len(vertices)
    dl = b''.join(struct.pack('>II',a,b) for a,b in commands)
    dl_end = dl_start+len(dl)
    trailer = bytearray(native[0x1210:])
    struct.pack_into('>I',trailer,0,head+dl_start-40)
    for off in (4,8,12,16):
        old = struct.unpack_from('>I',native,off)[0]-head+40
        struct.pack_into('>I',header,off,head+dl_end+(old-0x1210)-40)
    result = bytes(header)+vertices+dl+trailer
    assert result[0x20] == 6
    return result, {'scale':SCALE,'facet_count':12,'portrait_height':156,
                    'native_portrait_height':156,'portrait_middle_chord':radius[1],
                    'native_middle_chord':2*120*math.sin(math.radians(36)),
                    'order':['dk','diddy','lanky','tiny','chunky','krusha'],
                    'centres_degrees':centres,'vertices':len(vertices)//16,
                    'display_list_start':dl_start,'display_list_end':dl_end}


def prepareBarrelAssets(rom_path):
    rom = Path(rom_path).read_bytes()
    assert struct.unpack_from('>I',rom,TABLE_BASE+27*4)[0] == 0
    for index in TEXTURE_IDS:
        assert read_file(rom,25,index) == b'', 'Reserved texture ID already in use'
    image = Image.open(ASSETS/'krusha-face-64.png')
    prepare_startup_logo()
    halves = encode_face(image)
    model, layout = make_model(read_file(rom,5,0xC0))
    for name,data in zip(('tag-barrel-six.bin','face-left.rgba5551','face-right.rgba5551'),[model]+halves):
        (ASSETS/name).write_bytes(data)
    layout.update(face_sha256=hashlib.sha256((ASSETS/'krusha-face-64.png').read_bytes()).hexdigest(),
                  model_sha256=hashlib.sha256(model).hexdigest(),custom_table=CUSTOM_TABLE,
                  custom_rom=hex(CUSTOM_ROM),texture_ids=TEXTURE_IDS,
                  alpha_threshold=128, model_bytes=len(model))
    (ASSETS/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')


def appendBarrelAssets(rom_path):
    payloads = [(ASSETS/n).read_bytes() for n in ('tag-barrel-six.bin','face-left.rgba5551','face-right.rgba5551')]
    with open(rom_path,'r+b') as stream:
        stream.seek(0,2)
        end = stream.tell()
        if end > CUSTOM_ROM: raise RuntimeError('Pointer tables overlap custom barrel assets')
        stream.write(bytes(CUSTOM_ROM-end))
        pointer = CUSTOM_ROM+16
        offsets = []
        for data in payloads:
            offsets.append(pointer-TABLE_BASE);pointer += len(data)
        offsets.append(pointer-TABLE_BASE)
        stream.write(struct.pack('>4I',*offsets))
        for data in payloads: stream.write(data)
        stream.seek(TABLE_BASE+CUSTOM_TABLE*4);stream.write(struct.pack('>I',CUSTOM_ROM-TABLE_BASE))
        stream.seek(TABLE_BASE+(32+CUSTOM_TABLE)*4);stream.write(struct.pack('>I',3))
    print('Embedded six-face barrel and approved portrait in custom table 27')
