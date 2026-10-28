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
