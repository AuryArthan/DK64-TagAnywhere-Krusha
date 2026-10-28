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
