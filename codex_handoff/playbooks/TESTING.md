# Playbook: control the game and verify a change

**Workflow migration, 2026-10-31:** maintained scripts now live inside the repo.
Start with [tools/README.md](../../tools/README.md) for current runnable commands
and required fixtures/output variables. Parent-workspace commands and hardcoded
historical-runner cautions below describe the legacy setup.

Commands here run from the **full workspace root**, not inside the source repo.
First read the actual target script: old suites can contain fixed output paths,
state dependencies, temporary progress fixtures and interactive loops.

## Ordinary play / setup

```sh
./tools/play-krusha.sh
# For a 16:9 window/display:
./tools/play-krusha-wide.sh
```

These launch the built ROM; they do not build it. Required memory is 8 MB and
save type EEPROM 16K. The launcher configures these, `CountPerOp=1`, and `--noosd`.
The default desktop audio is enabled; automated runs normally mute it.

Keyboard: arrows = stick, Left Shift = A, Left Ctrl = B, Z = Z, C = R,
X = L, I/J/K/L = C-Up/Left/Down/Right, Enter = Start. In the Krusha config,
A/D also provide backward/forward D-pad tagging (confirm the live INI if changed).
F5/F7 save/load the numbered slot; 0–9 select it; P pauses; slash advances one
frame while paused; F fast-forwards while held; F12 captures a PNG; Escape exits.

Use the current ROM's fresh slot 5 for manual play only when its hash matches
the accepted snapshot. A long intro can be native/unskippable. Fast-forward is
an emulator aid, not a ROM proof of a skipped scene.

## Isolate every development test

Pick a **new** scratch directory and use it throughout a run. Never mutate the
normal `runtime/krusha/current` profile with adversarial/unlock/resource fixtures.
Never run two emulators against one profile. Do not run independent controllers
on the same X display.

```sh
mkdir -p runtime/krusha/scratch-example
DK64_ROM="$PWD/dk64-tag-anywhere/rom/dk64-krusha-dev.z64" \
DK64_RUNTIME="$PWD/runtime/krusha/scratch-example/profile" \
./tools/control.py
```

`control.py` uses a private Xvfb display, default `:99`; `DK64_DISPLAY=:100`
selects another. Local X sockets and reading the emulator child's `/proc` memory
may require an execution-permission escalation in a managed environment. Use
`/usr/bin/python3` for helpers needing Pillow; another `python3` on this machine
has lacked it. Memory diagnostics depend on this bundled amd64 Mupen64Plus build;
revalidate the RDRAM lookup if replacing the emulator/core.

Send one JSON line, wait for its `ok`, then send the next. Some replies precede
`ok` with `status`, `memory` or scene data. Never write status/debug logs into the
JSON stdin stream. Examples:

```json
{"status":true}
{"keys":["Up","Shift_L"],"seconds":0.2,"wait":0.2,"shot":"jump"}
{"down":["z"],"wait":0.1}
{"keys":["j"],"seconds":0.15,"wait":0.8}
{"up":["z"],"wait":0.1}
{"scene":"inspect-player"}
{"read":[{"address":"0x807444C0","type":"u8"}]}
{"tap":"p","wait":0}
{"keys":["slash"],"seconds":0.025,"wait":0.025}
{"tap":"p","wait":0.1}
{"quit":true}
```

The Z+J example equips/holsters the gun. Other combos are Z+K camera, Z+I shout,
Z+L orange. Keep keydowns/keyup balanced; an A held across a vine grab can cause
an immediate leap. Quit through the JSON command so saves flush and the emulator,
recording and X server exit cleanly. Do not kill unrelated desktop processes.

## Fixtures versus real gameplay

The controller supports `position` (XYZ), `facing`, `fixture_map`, resource/flag
`write`, recording and screenshots. `position` resets previous collision and
attachment fields; it is not a simple cosmetic teleport. `fixture_map` redirects
an actual live loading zone so the native engine loads the requested map. Inspect
`tools/emulator-memory.py` rather than guessing these side effects.

Do not write identity, action, animation or code to claim a mechanic works.
Position/resource/temporary unlock fixtures are useful when logged and described.
Restore temporary flags and keep that EEPROM isolated. Use native menu inputs for
options; the current matrix's menu-ready polling is a good example.

RAM read kinds are u8, u16, u32, f32. Mupen's RDRAM byte/halfword layout needs XOR
3/2, already handled by Memory. Do not use raw host byte offsets without it.

## Existing regression helpers and dependencies

`tools/krusha-test.py` is the importable driver and core cold-boot suite. It uses
`DK64_TEST_ROM` to choose its ROM, then passes `DK64_ROM` to control.py itself.
`DK64_RUNTIME` selects a profile. Importing it can seed a missing native EEPROM
from the baseline Speed Mode save; that is **not** a fresh casual file.
The initial cold boot creates same-ROM native checkpoints for downstream tests.

```sh
DK64_RUNTIME="$PWD/runtime/krusha/scratch-example/profile" \
/usr/bin/python3 -u tools/krusha-test.py </dev/null
```

Then read that profile's `logs/krusha-tests.json`: require matching ROM SHA-256,
`complete: true`, all checks passed, and no error. Zero shell exit status alone
is not sufficient. Most helpers finish in an interactive stdin loop; EOF or
`{"quit":true}` closes it. Do not leave it waiting unattended.

| Helper | Prerequisite / purpose |
| --- | --- |
| `krusha-test.py` | Cold boot, core gameplay, saves slots 0–4 including Krusha Isles slot 1 and Japes slot 3 |
| `krusha-extra-test.py` | Core slot 3; oranges, fairy camera, locked-Kong tagging |
| `krusha-barrel-test.py` | Cold boot; creates barrel slot 6 and an Isles slot 0 |
| `krusha-v2-test.py` | Core slot 1 and barrel slot 6; gun/model and armed barrel regressions |
| `krusha-barrel-extra-test.py` | Barrel slot 0; all selections, animation, locked Kongs, second map |
| `krusha-options-test.py` | Native UI, no state loads; repeated cold boots/persistence and ON/OFF barrels |
| `krusha-tree-fix-matrix.py` | Cold boots; same-ROM slots 8/9; tree and ordinary-airborne timing |
| `krusha-climb-regression.py` | Same-ROM, Krusha-ON slot 8; vine grabs/tag restrictions/swing/leap |
| `trace-tree-tag.py` | Matching slot 8, or DK64_TREE_BOOT=1; original nine-frame comparison |
| `krusha-release-newgame-test.py` | Erased EEPROM; long story, no unlock/move assumptions |

Historical orchestration `krusha-tree-fix-regressions.py` overrides its own output
AND profile paths under the frozen tree review. Do not blindly reuse it with an
outer DK64_RUNTIME and assume isolation. Copy/adapt its stage list/output handling
or invoke the individual helpers against a new profile. Other release/widescreen
packagers also need path review. Some scripts hardcode the development ROM even
when another helper honors DK64_TEST_ROM. Verify this before an A/B comparison.

The matrix has explicit safe output overrides:

```sh
DK64_RUNTIME="$PWD/runtime/krusha/scratch-example/matrix-profile" \
DK64_MATRIX_OUT="$PWD/runtime/krusha/scratch-example/matrix" \
/usr/bin/python3 -u tools/krusha-tree-fix-matrix.py
```

Its default phases are ON Standard, ON Widescreen, OFF Standard. To cover OFF
Standard and OFF Widescreen separately, use `DK64_MATRIX_OFF_ONLY=1` with new
profile/output directories. The accepted 723-count report consolidated two ON
phases and two OFF phases, requiring all 112 case identities. Do not reuse its
packager on new evidence without adjusting its hardcoded directories/schema.

## Reading results and reporting honestly

Frame-step race conditions; wall-time input is approximate, especially under
software-renderer load. Prefer one emulator at a time and native ready flags.
Record finite XYZ, map, player actor matching character+2, control states,
resource deltas, actual projectile/enemy states and cleanup where relevant.
Test the changed behavior plus its boundaries; do not repeatedly rerun unrelated
large suites after a documentation-only edit.

A fresh ROM must cold-boot, not restore old RAM/code. Only copy exact-same-ROM
states between isolated profiles; regenerate them after a binary change.
Native EEPROM filenames use the local-build title plus the first eight uppercase
MD5 digits. Preserve the source save and copy into the destination filename.

Audio: DK64_CAPTURE_AUDIO=1 uses the SDL disk mixer to capture native S16LE stereo
at the bundled setup's 22050 Hz, in profile `audio/game-audio.raw`. Check the live
helper before interpreting timestamps. DK64_RESOLUTION and DK64_STRETCH control
capture geometry. See audio/centering tools for measured comparisons rather than
approving a synthetic preview as in-game output.

Separate ROM bugs, test fixture errors, and emulator/host failures. Reports must
state ROM hash, fixtures, actual successes, failures, and limits. No physical
console was available; no emulator run changes that fact.
