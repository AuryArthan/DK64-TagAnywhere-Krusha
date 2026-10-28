"""Embed the committed VADPCM recording, leaving the game's original banks intact."""
from pathlib import Path
import hashlib,json
ROM_ADDRESS=0x02100000

def appendScream(rom):
    root=Path(__file__).resolve().parent.parent
    assets=root/'assets/krusha';meta=json.loads((assets/'scream.json').read_text())
    data=(assets/'TheScream.adpcm').read_bytes()
    for name,key in [('TheScream.adpcm','adpcm_sha256'),('scream.h','header_sha256'),('TheScream.wav','source_sha256')]:
        if hashlib.sha256((assets/name).read_bytes()).hexdigest()!=meta[key]:
            raise RuntimeError('Scream asset mismatch: '+name+'; regenerate using build/prepare_scream.py')
    assert len(data)==meta['adpcm_bytes'] and len(data)%9==0
    with open(rom,'r+b') as stream:
        stream.seek(0,2);end=stream.tell()
        if end>ROM_ADDRESS:raise RuntimeError('Appended game data overlaps the custom scream ROM region')
        stream.write(bytes(ROM_ADDRESS-end));stream.write(data)
        # Native DMA requests complete 0x800-byte cache blocks, including the tail.
        stream.write(bytes(0x800));stream.write(bytes((-stream.tell())&15))
    print('Embedded supplied scream at ROM '+hex(ROM_ADDRESS)+' ('+str(len(data))+' VADPCM bytes)')
