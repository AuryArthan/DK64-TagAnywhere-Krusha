# Krusha vocal instrument research

The checkpoint before this work is `v0.1`, commit
75f92e37440b19806e9dc5c20b704ee1d5c1f198. Its offline bundle, ROM,
BPS, native saves, exact-build states and matching tools are in
`runtime/checkpoints/v0.1/`.

## Native assets and crash

The local decompilation provides the primary references:

- `code_EFDC0.c`, 806F03C4: the native instrument initializer chooses an
  instrument cutscene for the original five actors. Actor 7 has no initialized
  choice. Entering this path as Krusha can play an invalid cutscene.
- `code_F56F0.c`, 806F10E8: instrument prop/model handling covers the five
  Kongs, with no Krusha prop. The model-name bank likewise has no Krusha
  instrument model. These checks found no dedicated Krusha instrument asset;
  they do not prove every unidentified ROM asset has been identified.
- Generic instrument animation 5A resolves to script 1BC for both Chunky and
  Krusha. Its raw table also supplies a shared fallback, not a unique Krusha
  performance. Nearby instrument actions 63..65 likewise have shared entries.
- Krusha's held-B release uses raw skeletal clip 2AA, 110 frames long, shared
  with Chunky. It is usable on Krusha's skeleton. Its normal gameplay script C4
  also spends crystals and creates a shockwave: running that script for the
  roar would apply unwanted extra gameplay effects.
- Native Krusha voice cues 274..278 occur in his multiplayer scripts. The
  provisional roar uses cue 276 at pitch 0.48. This is an existing voice with
  runtime pitch processing, not a newly recorded or wholly unused sound asset.
  The sound ID, pitch and cost are isolated at the start of `src/krusha_roar.c`
  for later tuning/sample replacement.

## Implementation

The input hook at 806E52D0 delegates to the displaced native routine for the
original five Kongs. Krusha uses filtered Z + newly pressed C-Up, retaining the
native platform, input and cutscene gates. Scripted action 53 is routed to the
same guarded initializer instead of the undefined sixth instrument cutscene.

The roar stops animation scripts, holsters the visible gun and plays raw 2AA.
It enters actual native control state 67. A wrapper in dispatch entry 80750E88
uses the common instrument control/rendering routine, keeping progress zero to
avoid the five-Kong song branch. At 110 game frames it returns through the
native ground/water recovery routine 806CFF9C. It has a 15-frame cooldown,
reset on map changes. Repeated inputs cannot reenter an active roar.

Enemy spawner update 80727958 already checks for player state 67 and sends
active vulnerable enemies to native instrument death state 16 (hex). This
preserves spawner activation and immunity bit 40, instead of deleting arbitrary
actors or inventing a map-wide damage loop. No character-ID spoof is involved.

The first implementation costs 150 shared crystal units (one displayed crystal),
matching the existing charged attack's cost. Krusha still cannot collect pickups;
other Kongs refill the shared supply. Native instrument energy and prop bits for
slot six remain zero. No five-Kong energy record is borrowed. Instrument-pad
puzzle flags/songs are not added by this change.

## Validation

See exact-ROM `krusha-roar-tests.json` and `krusha-roar-extra-tests.json` under
`runtime/krusha/current/logs/`. Input traces distinguish controller actions from
position, loading-zone, inventory and temporary spawner-immunity fixtures.
The audio preview is captured through the emulator's real SDL mixer at 22050 Hz,
stereo S16LE; it contains game background audio as well as the processed vocal.

## Second revision: trimmed performance and layered shout

The user-verified first roar is commit `385afd9`. Its ROM, patch, source bundle,
workspace tools, report summary and preview are preserved in
`runtime/krusha/roar-first-version/`; the v0.1 checkpoint remains untouched.

The roar now seeks directly to skeletal frame **55** of clip 2AA and restricts
its lower playback bound to 55. It uses native channel-speed setter **80614D48**
at **0.8**, rather than modifying the shared asset or confusing the raw animation
API's fourth argument (blend duration) with playback speed. The normal charged-B
attack's clip and script are unchanged.

Completion follows the actual channel's final skeletal frame (109), with a
150-game-tick failsafe. Frame-advance measurement shows the inherited crouch
animation time scale is 0.5: the channel advances **0.4 skeletal frames per game
tick**, versus the previous 0.5. In that normal input context, the second half
finishes after approximately **135 ticks / 4.5 seconds**. Using the previous
fixed 110-tick lifetime would cut off the slower animation.

The original voice was already requested at the signed per-voice mixer maximum,
32767. The new dry fundamental uses two coherent copies at 32767 and 22937,
for **1.7x nominal amplitude gain** (about +4.6 dB) without overflowing either
voice. Pitch randomization is disabled so the two copies stay in tune. Two
quieter copies add an octave (pitch 0.96, gain 22%) and third harmonic (pitch
1.44, gain 10%) above the 0.48 fundamental. Pitch-shifted full voice recordings
are layered harmonies, rather than synthesized pure sine-wave partials.

Three decreasing echoes replay the fundamental at 7, 14 and 23 game ticks
(approximately 233, 467 and 767 ms), with gains 75%, 45% and 25% relative to
the old single voice and stereo pan positions 40, 88 and 58. Overtones have
native reverb mix 64; echoes use 40. The dry fundamentals retain the old room
mix minimum: sending them heavily into reverb would reduce the direct gain.
The complete effect requests seven one-shot voices. All layers use the native
sound bank and N64 mixer; the video preview has no added offline audio effects.

A louder prototype used 38%/16% overtones and 90%/55%/30% echoes. Its capture
showed occasional mixer-ceiling samples (roughly 0.05% of the recording), so
these secondary layers were reduced while retaining the requested dry boost.
New exact-build audio measurements and controller checks are recorded in the
current runtime profile. Nominal gain is not a guarantee of 1.7x perceived
loudness, which depends on pitch, reverberation, other game sounds and settings.

The balanced Japes capture contains 67 samples near the plugin output ceiling
out of 299008 (about 0.022%), versus 154/303104 in the louder prototype.
This is occasional peak limiting, not a guarantee of zero clipping in all game
mixes. The final preview retains real native mixer behavior and has no offline
gain, compression or echo added.

## Third revision: supplied recording, last two-thirds at 90%

The user-verified second revision is commit `9582a39`. Its ROM, patch, source
bundle, tools, reports and preview are in `runtime/krusha/roar-second-version/`.

The input is `input_files/TheScream.wav` (the message said `.waw`), SHA-256
`b266fb6775583953c4f82daa7e0a1fcba3d918197ec2f9949d7c4f3bf8815103`.
It is a 3.148125-second, 48 kHz stereo recording. The original is copied unchanged
into `assets/krusha/`. The converter produces 22050 Hz mono at the original
pitch/duration, removes DC at 20 Hz, adds 3 ms / 15 ms click-prevention fades,
and encodes native VADPCM using the pinned open-source encoder documented in
`assets/krusha/README.md`. Reported encoding SNR is about 46 dB.

The user requested amplitude weights of **65% supplied scream / 35% preceding
roar effect**. The supplied sample plays at native voice volume 21299/32767.
Every earlier fundamental, overtone and echo volume is multiplied by 0.35,
with integer rounding; its pitch, stereo placement and reverb are retained.
No per-source loudness normalization is applied, so these weights preserve the
relative levels in the recordings rather than promising a perceived-loudness
ratio. The recording has no extra octave/pitch change or additional echoes.

`src/krusha_scream.c` defines an independent one-sound ALBank/ALInstrument,
ALSound, envelope, key map and VADPCM wavetable/book in the reserved resident
region. Its non-looping sample streams through the game's normal audio DMA
from ROM `0x02100000`, with a zero-padded DMA tail. The native allocator at
80737638 creates the voice; the persistent handle is cleared by native cleanup.
Thread-priority protection matches playSound. Original sound-bank descriptors,
voice samples and music are not replaced. SFX master volume still applies
through the native group-0 mixer. A persistent handle requires explicit zero
initialization: an uninitialized GCC COMMON global caused armips to emit an
incorrect relocation in the first prototype; the final .bss relocation was
checked in the built machine code.

The converted assets and checksums are committed. Normal ROM builds neither
need the source file in `input_files` nor an installed encoder. The build
validates source, encoded data and header hashes and refuses to overlap the
sample region. Optional regeneration is `build/prepare_scream.py`.

The animation now begins at **110/3 = 36.6667** and uses channel speed **0.9**.
Frame-advance checks observe **0.45 skeletal frames per game tick** with the
native crouch time scale 0.5. It reaches frame 109 after **161 ticks / 5.37 s**.
Recovery follows the actual last frame, with a 240-tick safety timeout.
The normal charged attack's shared animation asset remains untouched.

The native sound-state records verified 65% gain, pitch/base pitch 1.0, the
correct custom ROM sample address/size, all earlier 35% layers and echoes,
and release of the custom voice. A captured gameplay mix correlates with the
decoded user recording at 0.816, confirming it survives the real codec, ROM
DMA and mixer path. That scene's peak is 23584 with no plugin-ceiling samples.
These are scene-specific measurements, not a guarantee for every game mix.
The captured preview has no sound effects added offline.

## Fourth revision: last three-quarters at normal speed

The user requested a slightly earlier start with no added slowdown. The roar
now starts at **110/4 = 27.5** of clip 2AA and sets its native channel speed to
**1.0**. Recovery still follows the actual final skeletal frame. The 65% supplied
recording / 35% preceding effect mix and encoded sound asset are unchanged.
The preceding accepted build (`1774b68`, 52 checks) is preserved in
`runtime/krusha/roar-third-version/`. This revision is checked by cold boot,
native frame advance and actual enemy/cost/recovery interactions, with a new
real-time audio/video capture and matching native checkpoints.

## Fifth revision: last four-fifths, 20% faster

The roar now starts at **110/5 = 22** of clip 2AA and plays at native channel
speed **1.2**. Recovery follows the actual final skeletal frame as before.
The preceding accepted three-quarter build (`bc1238c`) and its 18-check evidence
are preserved in `runtime/krusha/roar-fourth-version/`. The sound remains the
65% supplied recording / 35% earlier vocal effect. The revised frame-advance
checks verify the earlier start, 120% channel speed, the observed skeletal
progress against native actor time scale, final-frame recovery and native
sound-state/voice cleanup. A fresh real-time capture demonstrates the result.

## Sixth revision: native instrument backdrop

The custom roar entered native instrument state 67 but bypassed its animation
script. That script also controls presentation: command **80618E4C** clears
scene mask **0x10030** and enables performer object flag **0x40000000**.
Renderer **8062CA70** uses bit 0x10 for scenery; **80630B70** uses bit 0x20 for
non-actor props and 0x10000 for normal actors, with a performer-flag exception.
The omitted masking exposed enemy death movement normally hidden by instruments.

A controller-driven comparison using DK in Japes captured the native black
backdrop and spotlight, with scene flags changing from 0x31030 to 0x20000.
Krusha now uses the same presentation mask and performer exception for his
existing roar. It does not enter the five-character instrument cutscene table.
The scene bits and original performer bit are saved before masking and restored
at normal completion or a same-map interruption. Cleanup updates only the owned
bits. After a map change, it discards the old visual state instead of restoring
old flags over a newly initialized scene or dereferencing a freed actor.

The previous accepted build (`bcfff58`) is preserved in
`runtime/krusha/roar-fifth-version/`. The four-fifths/120% animation, 65/35 sound
blend, crystal cost and native enemy death behavior are retained.

Native checkpoints and image checks show a black fraction of 0.971 during the
Japes scream (Krusha and HUD visible), returning to 0.026 afterward. The focused
performance checks also verify exact scene/performer-bit restoration. Separate
controller checks cover pause/resume, ordinary movement, bazooka, camera,
insufficient crystals, a loading-zone transition during the move, a new-map
scream, and the original DK instrument backdrop and restoration. These tests
write player position, inventory and loading-zone fixtures only, not character,
action, animation, damage or executable state. The earliest cold-boot run exposed
a missing optional image-analysis module in the test harness; image analysis now
uses the already-installed FFmpeg decoder, and the complete checks passed using
that ROM's own cold-boot checkpoint.
