# Native widescreen UI correction

The approved 10% larger Krusha build is preserved as annotated tag `v0.2.1`
(commit `f75d590a451221dae5029999f7bf2a74d5c1f517`) and as a complete offline
checkpoint in `runtime/checkpoints/v0.2.1/`. This development change follows it.

Choose **Screen Size → Widescreen** in the existing Other Options menu, then
use a display stretched to 16:9. `tools/play-krusha-wide.sh` configures that
stretch; it does not alter the game's world projection. Native Screen Size is
session-only and resets to Standard on cold boot, as in the approved baseline.
With Standard selected, the new rendering wrappers call their native routines
without modifying their output. Krusha's separate ON/OFF setting still persists.

## Rendering

DK64 draws the world with the native widescreen perspective, but normally draws
screen graphics for 4:3. A 4:3 framebuffer displayed at 16:9 needs screen graphics
compressed to 75% of their former horizontal width. `src/widescreen.c` gates
that correction exclusively on native flag `807444C0`.

* The shared `guOrtho` wrapper expands the horizontal projection range equally
  on both sides. Text, portraits, icons and their positions remain together in
  a centered safe area. Vertical size and depth remain native. It does not
  modify perspective-projected world sprites, character models or geometry.
* Captured framebuffer projections and the separate sky/background projection
  retain full width. This keeps the pause backdrop and background coverage.
* The native uSprite texture-rectangle renderer bypasses projection matrices.
  Its wrapper transforms the emitted RDP rectangle endpoints and inverse U
  texture step together, including mirrored sprites. The startup Rare logo's
  separate rectangle path is corrected once, without double-scaling nested calls.
* Animated number counters have explicit RDP scissor windows. Their wrapper
  corrects those windows with the digits, preserving the final viewport restore.
* The simple bitmap-text renderer emits its own texture rectangles. Its wrapper
  corrects those too, including Arcade and Jetpac score text. A 4:3 reference
  capture exposed this separate path after scenery sprites were already fixed.
* Fairy-camera, photo-shutter and sniper masks receive black side coverage so
  narrowing the mask artwork cannot expose the world outside the lens.
* The Factory/Castle car race's minimap frame uses raw RDP fills. Its queued
  renderer corrects those fills along with the projected map and markers.
* Searchlight Seek's aiming arrows are attached to a projected world location.
  Its queued renderer preserves that location while correcting the artwork's
  aspect. This is limited to the four Searchlight maps; other world-to-screen
  projections are not changed. The two matrix commands match the native DK64
  words explicitly: this repository’s SDK macro mixes older matrix flags with
  F3DEX2 opcodes and otherwise corrupts that callback’s drawing state.

Resident hooks preserve the original displaced instructions and return to the
native functions. Overlay callback replacements check both map and callback
address because several overlays occupy the same RAM address. The menu overlay
patch checks the original prologue. Its unused, already-replaced Options renderer
body is zeroed to retain compressed overlay capacity without moving RAM offsets.
The build now rejects any compressed overlay that would overrun its ROM slot.

## Verification

The scripts `tools/widescreen-test.py`, `tools/widescreen-extra-test.py`,
`tools/krusha-options-test.py` and `tools/krusha-roar-centering-test.py` exercise
the actual ROM. Native option changes and gameplay use controller inputs.
Position and loading-zone fixtures shorten travel; no option, character or
rendering-code writes are used for final integration checks. Reports identify
an exact ROM hash. New builds cold boot and use portable EEPROM; emulator
states are loaded only into the ROM that created them.

The review gallery and current validation totals are in
`runtime/krusha/widescreen-review/` and `runtime/krusha/validation-summary.json`.
OFF-mode projection matrices are compared byte for byte with v0.2.1. Native
ON/OFF/ON toggles test all three UI projections and the full-width framebuffer
projection. Captures use the emulator's actual output resolution, including
854×480 with display stretching enabled.

The final pass exercises gunfire/ammunition, oranges, pause/resume, fairy-camera
entry/photo/shutter/exit, the Krusha shout, six-slot barrel selection, pickup HUD,
and all three shop visits/exits. Extended captures cover Arcade, Jetpac, Kremling
Kosh, active Searchlight Seek and the Factory car-race minimap. The native Krusha
option suite covers persistence across cold boots and five/six-slot selection
with Widescreen enabled. The camera pass measures the actual enlarged animated
mesh on every shout frame in three setups. Rendered title-pixel bounds provide
a separate visual check of Standard parity and the horizontal correction. The
classic-game pass compares actual bitmap-glyph dimensions and placement with
the approved ROM at 4:3; this caught and verifies the separate score-text path.

This is focused integration coverage, not a full campaign or every multiplayer
layout. Rare bespoke renderers may need individual follow-up adjustments.

## Instrument scenes and HUD edge placement

Instrument action 103 now receives the complete 4/3 perspective-aspect multiplier
when native Widescreen is enabled in single-player adventure. The original camera
code uses only 1.2 during ordinary gameplay and drops to 1.0 for the five native
instrument cutscenes. Live before-change measurements confirmed those values for
all five Kongs; Krusha's custom performance retained 1.2. The `guPerspective`
wrapper divides out that native multiplier and applies 4/3 for the performance.
It preserves the native camera's animated aspect, vertical FOV, eye/aim, near/far
planes and perspective normalization. Other actions, cutscenes and Standard mode
keep their existing perspective inputs.

The normal adventure HUD moves outward by 16 native horizontal units, with
upper/lower items moving 4 units toward the corresponding vertical edge. At an
854×480 stretched display this is approximately 32 horizontal and 8 vertical
pixels. Icon and number origins shift together. The five-Kong golden-banana
counter is treated as one group, including its separately generated icons.
Native counter/sprite positions are restored immediately after their rendering
matrices are built, so there is no drift or saved-layout mutation. Health melons
use a separate double-buffered projection shifted four pixels upward, followed
by an explicit restoration of the ordinary projection. Menu, pause inventory,
barrel, camera masks, aiming reticles and bonus-game layouts retain their
existing positions.

`tools/widescreen-layout-test.py` cold-boots each screen mode, operates the
native option, checks all six instrument performances and camera recovery, and
captures HUD origins and actual sprite matrices. A copy of the previous ROM is
used for the independent Standard-mode HUD comparison; states stay with their
own ROM. Inspection captures and focused reports are in
`runtime/krusha/layout-review/`.
