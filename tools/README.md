# Repository-local development workflow

Run these commands from the repository root. No parent workspace directory is
required. ROMs, tool downloads, saves and test output are local ignored inputs.
The supported automated environment is Linux x86-64, developed on Ubuntu/Mint.

## Build and dependencies

Place your original USA big-endian ROM at `rom/dk64.z64`. Its SHA-1 must be
`cf806ff2603640a748fca5026ded28802f1f4a50`. Install Python 3 with Pillow in the
interpreter used by the scripts (`/usr/bin/python3` here). Setup also needs curl,
APT/dpkg, tar, make, and host C/C++ compilers. Emulator control needs SDL2/Mesa,
ImageMagick's `import` and FFmpeg on the host.

```sh
./tools/setup-build-tools.sh
./tools/build-krusha.sh
```

Setup downloads n64chain GCC 9.1.0 and armips 0.11.0 with archive SHA-256 checks,
builds armips (including its GCC 13 include fix), and builds gzip 1.2.4 from the
verified GNU source archive. CMake and its libraries are unpacked from APT into
the ignored cache. No sudo or system package installation is performed. APT
packages depend on the host's configured Ubuntu-compatible sources; this is not
a hermetic environment. An existing cache can be reused with
`DK64_TOOL_ROOT=/absolute/path/to/tools`; default is this repo's `tools/`.

Build output is `rom/dk64-krusha-dev.z64`. The wrapper also writes the BPS patch,
manifest and source diff in `runtime/krusha/` and a current-profile symlink.
`ARMIPS` and `N64_GZIP` can override individual executables. The pinned compiler
is found under the tool cache; the Python builder also supports `N64_GCC`.

## Play and control

```sh
./tools/setup-emulator.sh
./tools/play-krusha.sh
./tools/play-krusha-wide.sh
# Headless JSON controller, separate from a desktop play session:
DK64_RUNTIME="$PWD/runtime/scratch/manual" ./tools/control-krusha.sh
```

The emulator setup unpacks packages locally and records their SHA-256 values.
The checked-in configuration template contains only keyboard/controller events,
not anyone's saves, paths or game progress. It is copied only for new profiles.
8 MB memory, EEPROM16K, CountPerOp=1 and `--noosd` are set by the launcher.

Arrows move, Left Shift=A, Left Ctrl=B, Z=Z, C=R, X=L; I/J/K/L are C buttons.
A/D are backward/forward D-pad tags. Enter=Start; F5/F7 save/load; digits select
slots; P pauses; slash frame-advances; F holds fast-forward; F12 takes a PNG.

`control.py` accepts JSON lines and replies with optional diagnostic data followed
by `ok`. For example `{"status":true}`, `{"keys":["Up"],"seconds":0.3}`,
`{"shot":"test"}`, and `{"quit":true}`. Always quit cleanly. The default private
X display is :99; `DK64_DISPLAY` selects another. X sockets and the emulator child's
/proc memory may need execution permission in restricted environments.

`DK64_ROM` chooses a ROM for the controller/launcher. `DK64_RUNTIME` chooses its
profile; otherwise modified ROMs use `runtime/roms/<SHA256>/`. `DK64_RESOLUTION`
and `DK64_STRETCH=1` control display output; `DK64_CAPTURE_AUDIO=1` captures native
SDL audio. Camera memory diagnostics are specific to the bundled amd64 core
layout: replacing the core requires revalidating `emulator-memory.py`.

## Regression tests

No native EEPROM fixtures are shipped. Make a disposable save with Speed Mode
ON using the real menu, or copy your own suitable native EEPROM. Set
`DK64_TEST_SAVE` to that file; tests copy it into an isolated profile only when
that profile has no save. Never point tests at your normal play profile.
The core suite expects all original Kongs/moves unlocked and shared resources.

```sh
DK64_TEST_SAVE=/absolute/path/to/disposable-speed-mode.eep \
DK64_QA_OUT="$PWD/runtime/qa/new-run" \
/usr/bin/python3 -u tools/run-regressions.py
```

The runner requires a new/empty output directory, sets its own profile under
that output, and runs core → extra → barrel → gun → barrel-extra → options.
This creates the exact-ROM checkpoints needed by later stages. Completion
requires valid JSON, matching ROM hash, `complete: true`, all assertions passing,
and a successful process exit. Some individual scripts catch failures and exit
zero; do not infer success from exit status alone. To retry selected stages in
an existing run, use `DK64_REGRESSION_STAGES=barrel-extra,options`.

For individual helpers set `DK64_RUNTIME` and `DK64_TEST_SAVE`. `DK64_TEST_ROM`
selects the target for the importable `krusha-test.py` driver; its child controller
receives that ROM through `DK64_ROM`. The source USA ROM remains `rom/dk64.z64`
for read-only loading-zone fixtures.

Specialized tests have explicit review outputs, avoiding old frozen reports:

```sh
DK64_TEST_SAVE=/absolute/path/to/disposable-speed-mode.eep \
DK64_RUNTIME="$PWD/runtime/qa/tree/profile" \
DK64_MATRIX_OUT="$PWD/runtime/qa/tree/results" \
/usr/bin/python3 -u tools/krusha-tree-fix-matrix.py
```

`DK64_MATRIX_OFF_ONLY=1` tests the two OFF-mode aspect settings. The default
matrix covers ON Standard/ON Wide/OFF Standard. `trace-tree-tag.py` uses
`DK64_TREE_OUT` and a matching slot 8 (or `DK64_TREE_BOOT=1`).
`krusha-climb-regression.py` needs a matching Krusha-ON slot 8.
`krusha-roar-timing-test.py` requires `DK64_REVIEW_OUT` and writes its own states
when testing a new build. `krusha-roar-transition-test.py` expects core slot 1
and ready slot 5; read each script's prerequisites before running it.

Tests perform mechanics through controller inputs. Position/loading-zone/resource
and temporary-unlock fixtures are logged and kept separate from gameplay checks.
Do not import states across different ROM hashes. Run emulators sequentially to
avoid wall-time timing problems. Keep native saves and frozen reports intact.

## Scope of the migration

This folder contains maintained workflows, not all historical one-off probes.
The original parent workspace and its archived support tools remain available;
old scripts can hardcode old review outputs and should not be blindly rerun.
The optional VADPCM setup is pinned to a source revision; normal ROM builds use
committed encoded assets and need no codec rebuild. Large raw QA, downloaded
executables, reference repos, ROMs, saves, videos and shader caches stay outside Git.
