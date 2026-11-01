# Playbook: control the game and verify a change

**Workflow migration, 2026-10-31:** maintained scripts now live inside the repo.
Start with [tools/README.md](../../tools/README.md) for current runnable commands
and required fixtures/output variables. Parent-workspace commands and hardcoded
historical-runner cautions below describe the legacy setup.

Run current commands from the **source repository root**. Maintained helpers
are tracked in `tools/`; defaults write ignored output inside this repository.
The parent workspace's original tools and reports are historical backups.
Consult [tools/README.md](../../tools/README.md) for installation and runnable examples.

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
DK64_ROM="$PWD/rom/dk64-krusha-dev.z64" \
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

`tools/krusha-test.py` is the importable driver and core suite. It accepts
DK64_TEST_ROM and passes that target as DK64_ROM to the child controller.
DK64_RUNTIME selects the profile. If no save exists, DK64_TEST_SAVE must name
an explicit private fixture. Read the fixture requirements in tools/README.md.

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

The maintained sequence is `tools/run-regressions.py`, with a new DK64_QA_OUT
and an explicit DK64_TEST_SAVE. It creates its own isolated profile beneath the
chosen output. Read tools/README.md before invoking individual dependent stages.
The old parent `krusha-tree-fix-regressions.py` and packaging suites can overwrite
historical reports; they were deliberately not imported as active orchestration.

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

## Collectible fixtures: lessons from 2026-11-01

Use the new collectible/new-game helpers described in tools/README.md. The
collectible seed must have a completed **same-ROM** core report; libretro uses
its same-ROM graphics report/slot0 instead. All destination profiles are new.

The render actor list omits headphones and offscreen live objects; use scene
`loaded_actors` for these. After a distant teleport, recenter with native R and
wait for map entry autowalking/cutscenes to finish. Player idle alone can appear
before autowalking ends. Do not diagnose inactivity from an unloaded chunk.
A collected key disappearing from the model2 list is expected, not a failure.

A real fairy's targeting result is read several shutter frames after B. The
photo fixture holds the live fairy's position in the lens over that interval;
it never writes targeting, action, animation or capture flags. Success can run
a long first-photo refill/tutorial; use bounded native A/C-Up input and wait for
control. Check active flag-bank relocation after autosaves. Crystal/film groups
can contain multiple overlapping props; verify increments/caps, not just +1.

Native menu navigation must establish the correct page before using the stick:
menu actor326's additional data +0x12 is page0 (opening),1 (root carousel),
2/3 (Adventure file pages),9 (Other Options). A opens page0; B backs out of file
pages. At root, +0x17 item4 is Other Options. Wait for the native transition
floats +0/+4 to reach zero, then A. Assuming the root after an arbitrary boot
Start press caused false menu failures in both emulators. The maintained options
and libretro graphics helpers now use this native page/selection polling.

Early native-state restores sometimes froze at the first restored frame in
this harness. Let boot/renderer initialization finish before F7, and give the
state load time to settle before paired P pause/resume fixture commands. This
was a harness timing issue; no game timing patch was justified by that evidence.
Set a distinct REPORT_NAME when importing the driver for probes: its `check()`
writes the report, so the default name would overwrite the seed core report.
