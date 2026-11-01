#!/usr/bin/python3
"""RDRAM diagnostics / fixture setup for the bundled Mupen64Plus 2.5.9.

Loaded by control.py, the emulator's parent process (Linux ptrace policy).
All reads and writes are confined to the child's 8 MiB emulated RDRAM.
Fixture writes are logged separately from normal controller input.
"""
import os
from pathlib import Path
import struct
import math
import time

class Memory:
    def __init__(self, pid):
        self.fd = os.open(f'/proc/{pid}/mem', os.O_RDWR)
        maps = Path(f'/proc/{pid}/maps').read_text().splitlines()
        core = next(int(line.split('-')[0], 16) for line in maps
                    if 'libmupen64plus.so.2.0.0' in line and line.split()[2] == '00000000')
        # DebugMemGetPointer(M64P_DBG_PTR_RDRAM), bundled amd64 build.
        self.base = struct.unpack('<Q', os.pread(self.fd, 8, core + 0x9EE00 + 0x1101EE0))[0]
        if not self.base:
            raise RuntimeError('RDRAM not allocated')
        # The window/core can be ready before DK64's bootstrap writes osMemSize.
        # Larger software-rendered windows make this startup gap noticeable.
        deadline = time.monotonic() + 20
        while self.u32(0x80000318) not in (0x400000, 0x800000):
            if time.monotonic() >= deadline:
                os.close(self.fd)
                raise RuntimeError('Unexpected emulator RAM layout after bootstrap wait')
            time.sleep(.1)

    def offset(self, address, size, xor=0):
        address = int(address, 0) if isinstance(address, str) else address
        if not 0x80000000 <= address <= 0x80800000 - size:
            raise ValueError('Address must be inside DK64 RDRAM')
        return self.base + ((address - 0x80000000) ^ xor)

    def read(self, address, kind='u32'):
        fmt, xor = {'u8': ('B', 3), 'u16': ('H', 2), 'u32': ('I', 0), 'f32': ('f', 0)}[kind]
        size = struct.calcsize(fmt)
        return struct.unpack('<' + fmt, os.pread(self.fd, size, self.offset(address, size, xor)))[0]

    def write(self, address, value, kind='u32'):
        fmt, xor = {'u8': ('B', 3), 'u16': ('H', 2), 'u32': ('I', 0), 'f32': ('f', 0)}[kind]
        data = struct.pack('<' + fmt, value)
        os.pwrite(self.fd, data, self.offset(address, len(data), xor))

    def u32(self, address):
        return self.read(address)

    def status(self):
        p = self.u32(0x807FBB4C)
        result = {'map': self.u32(0x8076A0A8), 'character': self.read(0x8074E77C, 'u8'),
                  'player_pointer': hex(p), 'frame': self.u32(0x8076A064)}
        if 0x80000000 <= p < 0x807FF000:
            result['player'] = {axis: round(self.read(p + off, 'f32'), 2)
                                for axis, off in zip('xyz', (0x7C, 0x80, 0x84))}
            result['player'].update(state=self.read(p + 0x154, 'u8'),
                                    progress=self.read(p + 0x155, 'u8'),
                                    facing=self.read(p + 0xE6, 'u16'),
                                    actor=self.u32(p + 0x58))
        result['inventory'] = [self.read(0x807FCC40 + i, 'u16') for i in (0, 2, 4, 6, 8)]
        return result

    def position(self, xyz, facing=None):
        """Fixture teleport; reset both current and previous collision positions."""
        p = self.u32(0x807FBB4C)
        if self.u32(p + 0x58) not in range(2, 10):
            raise RuntimeError('No active player')
        for base in (0x7C, 0x88):
            for i, value in enumerate(xyz):
                self.write(p + base + i * 4, value, 'f32')
        self.write(p + 0xC0, 0, 'f32')
        # Equivalent attachment reset to native 80672C30: otherwise a platform
        # can move the actor straight back to its previous location next frame.
        self.write(p + 0x110, 0, 'u8')
        ledge = self.u32(p + 0x140)
        if 0x80000000 <= ledge < 0x807FF000:
            self.write(ledge + 0x6C, 0)
            self.write(ledge + 0x24, 0)
        self.write(p + 0x6A, self.read(p + 0x6A, 'u16') & ~0x408, 'u16')
        self.write(p + 0x64, self.u32(p + 0x64) | 0x2000)
        if facing is not None:
            self.write(p + 0xE6, facing, 'u16')
            self.write(p + 0xEE, facing, 'u16')

    def scene(self):
        result = self.status()
        # The render list below can omit offscreen actors and sprite actors
        # such as headphones. Keep the native update list separate so tests
        # do not mistake a rendering omission for a missing game object.
        result['loaded_actors'] = []
        for i in range(min(self.read(0x807FBB34, 'u16'), 64)):
            p = self.u32(0x807FB930 + i * 8)
            if 0x80000000 <= p < 0x807FF000:
                result['loaded_actors'].append({'pointer': hex(p), 'type': self.u32(p + 0x58),
                    'state': self.read(p + 0x154, 'u8'),
                    'xyz': [round(self.read(p + off, 'f32'), 2) for off in (0x7C, 0x80, 0x84)]})
        result['actors'] = []
        for i in range(min(self.read(0x807FC3F0, 'u16'), 256)):
            p = self.u32(0x807FBFF0 + i * 4)
            if 0x80000000 <= p < 0x807FF000:
                result['actors'].append({'pointer': hex(p), 'type': self.u32(p + 0x58),
                    'state': self.read(p + 0x154, 'u8'),
                    'xyz': [round(self.read(p + off, 'f32'), 2) for off in (0x7C, 0x80, 0x84)]})
        result['objects'] = []
        base = self.u32(0x807F6000)
        for i in range(min(self.u32(0x807F6004), 1024)):
            p = base + i * 0x90
            result['objects'].append({'pointer': hex(p), 'type': self.read(p + 0x84, 'u16'),
                'id': self.read(p + 0x8A, 'u16'),
                'xyz': [round(self.read(p + off, 'f32'), 2) for off in (0, 4, 8)]})
        return result

    def transition_fixture(self, map_id, exit_id=0):
        """Redirect one live loading zone; the native engine performs the load.

        Test setup only. Does not change the ROM, character ID, or move code.
        The map's normal loading-zone data is restored on its next load.
        """
        count = self.read(0x807FDCB0, 'u16')
        base = self.u32(0x807FDCB4)
        p = self.u32(0x807FBB4C)
        for i in range(min(count, 256)):
            zone = base + i * 0x3A
            if self.read(zone + 0x10, 'u16') in (9, 16):
                for n, off in enumerate((0x7C, 0x80, 0x84)):
                    coordinate = self.read(p + off, 'f32')
                    value = math.floor(coordinate) - 10 if n == 1 else round(coordinate)
                    self.write(zone + n * 2, value & 0xFFFF, 'u16')
                self.write(zone + 6, 60, 'u16')
                self.write(zone + 8, 100, 'u16')
                self.write(zone + 0xC, 0, 'u8')
                self.write(zone + 0x10, 9, 'u16')
                self.write(zone + 0x12, map_id, 'u16')
                self.write(zone + 0x14, exit_id, 'u16')
                self.write(zone + 0x38, 1, 'u8')
                self.write(zone + 0x39, 1, 'u8')
                return
        raise RuntimeError('No loading zone available for a transition fixture')
