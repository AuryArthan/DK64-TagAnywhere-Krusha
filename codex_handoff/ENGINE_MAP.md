# Implementation map (USA release only)

Read the live code and corresponding `docs/` before changing a hook. Absolute
addresses and structure offsets below are a useful starting point, not a
portable API for other ROM versions. Distinguish UI character index (Krusha 5)
from actor type (Krusha 7). Never globally spoof his identity as Chunky.

## Files to start with

| Source | Responsibility |
| --- | --- |
| `src/main.c`, `asm/main.asm` | Resident update/boot integration and payload |
| `src/taganywhere.c` | Tag input/gates, six-character cycle, native tag wrapper |
| `src/krusha.c`, `asm/krusha.asm` | Hook installation/trampolines, interactions, pickup/shop/camera fixes, 10% bones scaling |
| `src/krusha_options.c` | Native options-menu integration |
| `src/krusha_barrel.c`, `asm/krusha.asm` | Six-slot carousel, previews, animations, OFF behavior |
| `src/krusha_roar.c` | Input/control/lifetime; final trim/speed and actor-rate reset |
| `src/krusha_roar_stage.c` | Scene lighting, spotlight and camera staging/shake |
| `src/krusha_roar_framing.c` | Center animated mesh throughout orbit/zoom |
| `src/krusha_scream.c` | Native stereo VADPCM playback/voice cleanup |
| `src/widescreen.c` | HUD/menu/pause/perspective corrections and restoration |
| `build/build.py` | Compile/patch/repack, overlay capacity, padding/checksum |
| `build/barrel_assets.py`, `assets/krusha/barrel/` | Approved six-face barrel geometry/textures |
| `build/scream_asset.py`, `assets/krusha/` | Committed encoded audio and metadata |
| `build/prepare_scream.py` | Optional audio regeneration, not required to build |
| `bin/Nintendo_Krusha.png` | Exact approved 232×48 six-head startup PNG |

The approved portrait comes from workspace
`research/krusha/barrel-face-study/user_input/krusha-T-user-short-upright_tight.png`
and its `_64.png` version. The approved startup image came from
`extended-six-heads_adjusted.png` in the same user_input directory. Committed
copies are build inputs. Earlier generated candidates and online cutouts were
rejected; do not accidentally replace the approved assets with those.

## Key behavior details

Global flag 0x24 stores the **disabled** state, so old native saves default ON.
The bazooka uses the sixth native slot with shared ammunition. Native instrument
prop/energy bits remain disabled for Krusha; the custom shout supplies the effect.
Pickup rejection occurs before the object is collected/despawned. Bananaport
compatibility is restricted to its script condition, not a shared identity swap.
Boulder support adds its actor collision branch without granting all Chunky skills.

Scaling wraps native bone building, temporarily scaling the root then restoring
it. Permanent root scaling interfered with locomotion/doorway exits. The roar
uses native instrument state/enemy death handling, restores scene ownership and
camera data on cleanup, and resets timing across maps. Do not reintroduce an
inherited crouch animation-rate blend: that caused occasional ~5× screams.
Widescreen hooks restore native data after rendering to prevent layout drift.
Barrel extra resources use the native loader/reference lifecycle (custom table
27), not per-frame private model allocation.

## Tree-tag fix: do not regress

Native tag action 0x3B at 0x806EDFF8 recreates the skeleton before player controls
can perform a tree/vine grab using the new transforms. v0.4.2 changes action-table
slot **0x80752D5C** to `tagFinish`, calls the complete native action, then sets
PaaD **+0x100 (s32)** to 1 only if zero. Native control skips one regrab update,
decrements it, and the ordinary actor update initializes the transforms. Longer
cooldowns remain. It applies to adventure Kongs with Krusha ON or OFF.

Delaying tag dispatch/checking only an already-queued tree action did NOT solve
all timings. Those prototypes were reverted. Avoid whole-airborne tag bans,
position rollback after a warp, or forced extra animation/bone updates.
See [tree-tag-fix.md](../docs/tree-tag-fix.md) and final source.

## Useful RAM diagnostics

| Address / offset | Meaning |
| --- | --- |
| 0x807FBB4C | Player pointer |
| 0x807FBB40 / 0x807FBB48 | Current actor / current player context |
| 0x8074E77C (u8) | Character index |
| 0x8076A0A8 (u32) | Current map |
| 0x8076A064 (u32) | Map frame/object timer; resets across map loads |
| 0x807444C0 (u8) | Widescreen flag |
| 0x807444EC (u8) | Cutscene active |
| 0x807FC924 | Character-change / SwapObject pointer |
| SwapObject +0x29C (s16) | Queued native action |
| Player +0x58 (u32) | Actor type |
| Player +0x7C/80/84 (f32) | World X/Y/Z |
| Player +0x154/155 (u8) | Control state/progress |
| Player +0x174 | Additional actor data (PaaD) pointer |
| Player +0x140 | Ledge/bone collision info pointer |
| Player +0x146 (u16), +0x20C (u8) | Hand/model mask, gun-out state |
| Player +0x36F (u8) | New Kong actor ID for queued tag |
| 0x807FCC40/44/46/48 (u16) | Ammo/oranges/internal crystals/film |

Native states: idle 12 (0x0C), tag barrel 66 (0x42), shout 103 (0x67),
tree 89 (0x59), vine **87 (0x57)**, leaving vine 88 (0x58).
Beware decimal/hex confusion: vine is not decimal 57.
Maps used often: Isles 34, Japes 7, Galleon 30, Cranky 5, Funky 1, Candy 25,
Snide 15, main menu 80, Treehouse 171, Training Grounds 176.

Native climb helpers: 8072F230 finds a grab, 8072FA14 uses player bone 1,
80671C0C gets a bone position, 80614A64 builds actor bones. Skeleton swap is
806C8E58/806C8F8C. Verify signatures/types before calling them from new C/ASM.
Use cache writeback for modified callback data; runtime instruction hooks also
need instruction-cache invalidation. Keep original prologues and ABI correct.
