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

## Seventh revision: spotlight and simple camera zoom

The previous accepted backdrop build (`ba3008e`, 41 focused checks) is preserved
in `runtime/krusha/roar-sixth-version/`.

Native instrument animation command **80618F74** spawns actor **310**, model
**A8**, and places/scales it at the performing Kong. Its controller **806A8070**
marks the spotlight visible through the instrument backdrop and renders the
native cone and floor light. The new `src/krusha_roar_stage.c` uses that same
actor/model and native placement helper **8067B238**. It owns its actor pointer
separately, without using the player's vehicle pointer or the barrel's light.
The live actor registry is checked before following/deleting that pointer;
cleanup uses the native deferred deletion function **806782C0**.

Native instrument command **80619018** temporarily raises the actor's chunk
lighting. The stage similarly saves the current chunk RGB, applies full white
lighting through **80659670**, and restores the saved RGB afterward. If the
performer moves into another chunk, the previous chunk is restored before the
new one is saved and lit.

The camera uses the native player-view field of view at character-change offset
**27C**, which directly feeds `guPerspective`. It smoothly narrows the saved
FOV to 70% over **95 game ticks**, matching the 3.15-second scream. With the
normal 45-degree view, measured values progress 45 → 44.58 → 42.69 → 31.5.
The close view holds briefly, then eases back over the final fourteen skeletal
frames of the recovery. The exact saved FOV is restored on completion. Camera
position/mode remains under the native controller; no five-Kong cutscene is run.

Stage cleanup also runs when the move is interrupted. A different map or a
reset map frame counter discards old pointers and state, leaving the map loader
in charge of the old heap and the new camera/lighting. Failed activation does
not allocate a light or change the camera.

The focused test checks one correctly positioned native spotlight, native full
lighting, the progressive FOV values, exact light/FOV restoration and removal
of the owned actor. The image contains the black backdrop plus visible neutral
spotlight pixels. Cleanup checks additionally cover pause/resume, weapon and
camera use afterward, native tag-barrel spotlight creation/removal, insufficient
energy, map transition during the move, a new-map performance, and the original
DK instrument. The four-fifths/120% animation and 65/35 sound blend remain the
same. All preview sound and visual effects are produced by the game itself.

## Eighth revision: closer zoom, camera orbit and TheScream3

The accepted spotlight build (`c866c83`, 55 checks) is backed up in
`runtime/krusha/roar-seventh-version/`, including its ROM and source bundle.

The supplied recording is now `input_files/TheScream3.wav` (3.560479 seconds),
copied unchanged to the canonical `assets/krusha/TheScream.wav` source path.
Its SHA256 is `cb7c9891b77ec814648983b656143659c97b23448cccd5095620b29a8e32c118`.
It uses the existing native VADPCM conversion and 65/35 mix: 44,163 encoded
bytes at ROM 0x02100000, with original pitch and duration. The old layered roar
and stereo echoes retain their previous weights.

The close-view FOV is now 35% of the saved view, rather than 70%: 45 degrees
narrows to 15.75 degrees. That gives approximately twice the apparent character
size of the preceding close-up. Zoom timing follows the generated sample
length (about 107 game ticks), rather than assuming the old 3.15-second file.
The same eased progress turns the rendered view 45 degrees around the
performer's vertical axis. Both effects ease home over the final fourteen
skeletal recovery frames, with normal animation trim/speed unchanged.

The native camera matrix builder **805FCA94** is wrapped with its displaced
prologue retained. Only during that call, the renderer's eye and aim X/Z
coordinates (character-change offsets **210/218/228/230**) are rotated around
Krusha. All six original eye/aim coordinates are restored immediately afterward.
The camera actor, collision, follow logic and input yaw are never orbited, so
there is no cumulative rotation or drift. The wrapper is inactive outside the
owned Krusha performance and during native cutscenes. Normal stage cleanup
clears the orbit as well as restoring FOV, lighting and spotlight ownership.

Integration checks decode the actual native fixed-point view matrix to measure
the rendered yaw independently of the unchanged camera coordinates. They also
check the progressive zoom, embedded new sample, normal end, pause/resume,
loading-zone transitions, camera/bazooka use afterward and native DK instruments.

## Ninth revision: 150% sound, 110-degree orbit and closer framing

The accepted `9a9f068` build is preserved in
`runtime/krusha/roar-eighth-version/`, with its ROM, patch, source bundle,
validation reports and preview.

The new requested overall gain is **1.5x** for the entire 65/35 scream blend.
The supplied recording's native voice volume rises from 21,299 to 31,949.
All original roar layers and explicit echoes use 35% × 1.5 = 52.5% of their
original volumes. Every voice remains below the native 32,767 volume ceiling;
the original sample, pitch, duration and relative blend remain intact.

The rendered orbit now reaches **110 degrees** over the recording. The
close-view FOV changes from 15.75 to **13.125 degrees** at the normal 45-degree
view, giving approximately another **20%** in apparent size. Zoom and rotation
retain the same smooth progression and eased return during recovery. Spotlight,
animation, enemy-death behavior and move cost remain unchanged.

## Tenth revision: one full turn, wider framing, louder scream and credits

The accepted `2eaeb92` build is preserved in
`runtime/krusha/roar-ninth-version/` with its ROM, patch, source bundle,
validation reports and preview.

The close-up is reduced by 20% in apparent character size: the normal
45-degree view now reaches **16.40625 degrees**, compared with 13.125 before.
The rendered camera completes **one forward 360-degree revolution** over the
supplied recording, then holds the equivalent original angle during recovery.
Zoom still eases out over the last fourteen skeletal frames. Rotation no
longer follows zoom's return curve, avoiding an unintended reverse full turn.
The underlying native camera eye/aim remain unchanged between render calls.

The whole 65/35 audio blend is multiplied by another 1.4, for **2.1x** the
pre-boost mix. The supplied recording needs total voice volume **44,729**, above
a single native voice's 32,767 limit. Two same-bank, same-pitch voices (32,767
and 11,962) start in the same priority-protected allocation block, each with its
own persistent handle. Both are stopped before replay and are cleared by the
native allocator on completion. The previous vocal layers and echoes use
**73.5%** of their original volumes. The source recording, VADPCM payload,
pitch, duration and relative 65/35 blend are unchanged.

The startup credits' third native text box now says
**KRUSHA PATCHED IN BY ARTHAN** (the startup font supports uppercase). It is space-centered within its existing
33-character field. The Isotarge attribution, DK64 Crew line, text offsets,
string lengths and surrounding startup assets remain intact.

## Eleventh revision: lower shout camera

The accepted `c6c6fba` build is preserved in
`runtime/krusha/roar-tenth-version/`, including its ROM, source bundle, reports,
performance preview and startup-credit screenshot.

During the shout, the rendered eye is lowered by **25 world units**, about
half Krusha's normal standing height. This eases in over eight game ticks,
holds throughout the shout and eases out with the existing fourteen-frame
skeletal recovery. The aim point follows down by **12.5 world units**, half the eye displacement,
to retain face/body framing while giving a lower viewing angle.

Only the temporary eye/aim Y values passed to the native camera matrix builder
are changed. The saved native eye and target are restored immediately after that
render call, and the owned offset is cleared when the move ends or the scene
changes. The existing 360-degree orbit, zoom, audio, animation, spotlight and
credits remain unchanged.

The focused camera checks invert the native fixed-point view matrix to measure
the actual rendered eye height, verify the drop and its recovery, and check
normal camera height after completion, pause/resume, map transitions and a
native DK instrument. The capture is produced directly by the emulator.

## Twelfth revision: raised camera and animated-body centering

The accepted `0dca0d2` build is preserved in
`runtime/krusha/roar-eleventh-version/`, with its ROM, source bundle, reports
and lower-camera preview.

The previous eye drop is reduced from 25 to **21 world units**, raising the
view four units (roughly 12% of Krusha's model height). The cause of the drift
was the native camera's forward-looking aim point being orbited around the
player root instead of staying on the visible body.

`src/krusha_roar_framing.c` now follows the animated visible mesh. The committed
`include/krusha_camera_mesh.h` contains **305 unique visible vertices in 22 bone
groups**, extracted from model 0xDB's actual vertex-load/matrix commands. Hidden
bazooka bone 12 is excluded. The native world bone matrices use the same bank
selection as `getBonePosition`. This accounts for scale, facing and the leaning
scream pose. The normal build needs no additional tooling or ROM modifications.
To regenerate after a model change, run
`python3 tools/extract-krusha-camera-mesh.py [ROM]` from the workspace root.
The extraction uses the Python standard library; its geometry hash and source
points are recorded in `research/krusha/roar/krusha-camera-mesh.json`.

The orbit follows the animated body center. Three projection passes center the
visible mesh's screen rectangle, including pose/depth asymmetry. Centering eases
in over eight ticks and remains active through animation recovery. The eye
height still eases back during recovery. The native view is restored when the
move ends or is interrupted; native eye/aim and FOV are restored immediately
after each temporary rendering call, leaving the gameplay camera untouched.

The requested zoom is retained whenever it fits. If the pose would reach the
edge, the rendered FOV opens only enough to retain a small 14% framing margin.
A native camera pressed too close to the body is moved out to a minimum
75-unit horizontal radius during the entry blend. Spotlight, sound, animation,
cost, 360-degree turn and startup credit remain as accepted.

The camera tests read the actual view/projection matrices and independently
extract the visible vertices from the tested ROM. **438 consecutive animation
frames** passed in Isles, Japes, and an Isles view after native camera rotation
and a camera-distance change. The largest centered-phase offset was **0.054**
in normalized screen coordinates, about 16 horizontal pixels at 640x480; every
frame remained inside the viewport. The entry transition is eight ticks.
There are **86 focused checks** in total (40 performance, 15 per-frame framing,
31 cleanup), including pause/resume, map transitions and native DK instruments.
