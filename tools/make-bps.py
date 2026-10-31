#!/usr/bin/python3
"""Make and verify a BPS patch using SourceRead and TargetRead instructions."""
import argparse
from pathlib import Path
import struct
import zlib

def number(value):
    out = bytearray()
    while True:
        byte = value & 127
        value >>= 7
        if value == 0:
            out.append(byte | 128)
            return out
        out.append(byte)
        value -= 1

def create(source, target):
    patch = bytearray(b'BPS1')
    patch += number(len(source)) + number(len(target)) + number(0)
    pos = 0
    while pos < len(target):
        same = pos < len(source) and source[pos] == target[pos]
        end = pos + 1
        if same:
            while end < min(len(source), len(target)) and source[end] == target[end]:
                end += 1
        else:
            # Include short unchanged runs in a literal to avoid tiny operations.
            while end < len(target):
                if end + 8 <= len(source) and target[end:end+8] == source[end:end+8]:
                    break
                end += 1
        patch += number(((end-pos-1) << 2) | (0 if same else 1))
        if not same:
            patch += target[pos:end]
        pos = end
    patch += struct.pack('<II', zlib.crc32(source), zlib.crc32(target))
    patch += struct.pack('<I', zlib.crc32(patch))
    return patch

def apply(source, patch):
    assert patch[:4] == b'BPS1'
    assert zlib.crc32(patch[:-4]) == struct.unpack_from('<I', patch, len(patch)-4)[0]
    pos = 4
    def read_number():
        nonlocal pos
        value, shift = 0, 1
        while True:
            byte = patch[pos]; pos += 1
            value += (byte & 127) * shift
            if byte & 128: return value
            shift <<= 7
            value += shift
    assert read_number() == len(source)
    size = read_number(); metadata = read_number(); pos += metadata
    result = bytearray()
    while len(result) < size:
        action = read_number(); count = (action >> 2) + 1
        if action & 3 == 0:
            result += source[len(result):len(result)+count]
        elif action & 3 == 1:
            result += patch[pos:pos+count]; pos += count
        else:
            raise ValueError('This verifier expects SourceRead / TargetRead only')
    assert pos == len(patch)-12
    source_crc, target_crc = struct.unpack_from('<II', patch, pos)
    assert source_crc == zlib.crc32(source) and target_crc == zlib.crc32(result)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path); parser.add_argument('target', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    source, target = args.source.read_bytes(), args.target.read_bytes()
    patch = create(source, target)
    assert apply(source, patch) == target, 'Patch round-trip failed'
    args.output.write_bytes(patch)
    print(f'Wrote {args.output} ({len(patch)} bytes); CRCs and exact round-trip verified')
