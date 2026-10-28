"""Native equivalent of Isotarge/n64tex's Program.cs conversion rules.

https://github.com/Isotarge/n64tex/blob/master/n64tex/Program.cs
Preserves integer RGB averaging, alpha > 0, and big-endian RGBA5551 output.
"""
import argparse
from pathlib import Path
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("format", choices=("rgba5551", "i4", "i8", "ia4", "ia8"))
parser.add_argument("image", type=Path)
args = parser.parse_args()
with Image.open(args.image) as source:
    pixels = list(source.convert("RGBA").getdata())
output = bytearray()
if args.format == "rgba5551":
    for r, g, b, a in pixels:
        value = ((r // 8) << 11) | ((g // 8) << 6) | ((b // 8) << 1) | (a > 0)
        output.extend(value.to_bytes(2, "big"))
else:
    values = []
    for r, g, b, a in pixels:
        intensity = (r + g + b) // 3
        values.append({"i4": intensity // 16, "i8": intensity,
            "ia4": ((intensity // 32) << 1) | (a > 0),
            "ia8": ((intensity // 16) << 4) | (a // 16)}[args.format])
    if args.format in ("i4", "ia4"):
        if len(values) % 2:
            parser.error("4-bit textures need an even pixel count")
        output.extend((values[i] << 4) | values[i + 1] for i in range(0, len(values), 2))
    else:
        output.extend(values)
args.image.with_suffix("." + args.format).write_bytes(output)
