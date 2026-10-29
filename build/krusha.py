"""Adventure integration patches for the USA 1.0 menu overlay."""
import os
from pathlib import Path

def patchKrushaShop(filename):
    rom = os.environ.get('DK64_BUILD_ROM', './rom/dk64-krusha-dev.z64')
    symbols = dict(line.split()[:2][::-1] for line in
                   Path(rom.replace('.z64', '.sym')).read_text().splitlines()
                   if len(line.split()) >= 2)
    with open(filename, 'r+b') as stream:
        for address, symbol, prologue in [
            (0x80025FB4, 'krushafindpurchase', '27bdffd0afb30020'),
            (0x8002D8AC, 'krushaoptionsinput', '27bdffd0afbf0024'),
            (0x8002DBDC, 'krushaoptionsdraw', '3c0280802442bb60'),
            (0x8003292C, 'widescreenlogo', '27bdff18afb00020'),
        ]:
            target = int(symbols[symbol], 16)
            stream.seek(address - 0x80024000)
            assert stream.read(8) == bytes.fromhex(prologue), f'Unexpected prologue at {address:X}'
            stream.seek(address - 0x80024000)
            stream.write((0x08000000 | ((target & 0x0FFFFFFF) >> 2)).to_bytes(4, 'big'))
            stream.write(bytes(4))
        # The complete options renderer is replaced by resident C code. No
        # trampoline calls its old body. Zero that unreachable body without
        # changing RAM offsets, keeping compressed menu code inside its slot.
        stream.seek(0x8002DBE4 - 0x80024000)
        stream.write(bytes(0x8002DEE8 - 0x8002DBE4))
