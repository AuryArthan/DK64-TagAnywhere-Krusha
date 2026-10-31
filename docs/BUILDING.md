# Building the Krusha ROM

Run commands from the repository root. The source targets the original USA
big-endian ROM only. Place it at `rom/dk64.z64`; the builder checks its SHA-1:
`CF806FF2603640A748FCA5026DED28802F1F4A50`.

## Tested tool versions

- Python 3 with Pillow (`python3 -m pip install Pillow` in your Python environment).
- n64chain GCC 9.1.0, providing `mips64-elf-gcc` and its toolchain libraries.
- armips 0.11.0.
- gzip 1.2.4 for the compressed overlays. Compression size matters: a different
  gzip may exceed a fixed overlay slot. The builder rejects such an overflow.

The source includes the approved portrait/startup PNGs and encoded scream assets.
The original supplied recording is not needed for a normal build; regenerating
sound assets is a separate workflow described in the audio development notes.

## Linux

Make the compiler, armips and gzip available, then run:

```sh
python3 build/build.py
```

The compiler defaults to `mips64-elf-gcc`. You can override the tool locations:

```sh
export N64_GCC=/path/to/n64chain/tools/bin/mips64-elf-gcc
export ARMIPS=/path/to/armips
export N64_GZIP=/path/to/gzip-1.2.4
python3 build/build.py
```

Set your toolchain's library search path if its host executables require it.
Output is `rom/dk64-krusha-dev.z64`, with symbols alongside it. The build converts
textures, patches overlays, embeds the approved audio and barrel assets, pads
the final ROM to a 16 KiB boundary, and fixes its N64 header checksums. The output
path can be changed with `DK64_BUILD_ROM` (use a `.z64` filename).

The accepted v0.4.2 ROM SHA-256 is:

```text
dee2bbfcd04ba4ad1c0671e3f1ddd6d212ed1c94af0476caf12d9e862144d29d
```

## Windows

The inherited `build.bat` invokes the Python builder. Put n64chain on PATH;
Windows defaults use `build/armips.exe`, `build/gzip.exe` and `build/n64tex.exe`.
The Krusha development and regression runs used Linux; the Windows path has
not been revalidated for this version.

## Repository workflow tools

The maintained [tools workflow](../tools/README.md) now lives inside this repo.
Use `./tools/setup-build-tools.sh` and `./tools/build-krusha.sh` for the pinned
build plus manifest/BPS generation. Emulator setup, launchers and isolated
regression helpers are included as source scripts. Downloads and runtime output
are ignored. The direct builder above remains usable on its own.

Legacy parent-workspace helpers are retained as historical/local conveniences;
a standalone clone uses this repository's tools and does not need that workspace.
