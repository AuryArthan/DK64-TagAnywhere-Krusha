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

## Post-v0.4.2 compatibility additions

- `src/widescreen.c`: `widescreenWater` hooks80701CA0, retaining the native tint
  renderer and replacing only its02000080 projection reference. `maskSides`
  emits F3DEX2 OtherMode wordsE3000A01/E200001C explicitly; SDK2 versus2x macro
  guards otherwise encode wrong bitfields. This caused the GLideN64 camera/
  scope obstruction. Do not change the whole SDK as a workaround.
- `src/krusha.c`: shared pickup whitelist56/57/8F/91/15D..160/18D. Crate8F
  spills five separate ammo props; native actor7 uses15F. All stock updates are
  native. Crown model2 pad1C6's condition12/actor6 branch is extended with a copied
  actor7 instruction. Bananaport condition38 handling remains targeted.
- `krushaDialogueLine` hooks8070DED4, the synchronous glyph formatter, on map15
  and character5 only. Its bounded local line replaces literal whole-word KONG
  with KREMLING; native glyph allocation/wrapping still owns the result.
- `build/build.py`: writes ED atROM3C..3D and high version nibble2 at3F before
  normal CIC checksumming, declaring EEPROM16K for supporting emulators/loaders.
  Region45 and all code/asset offsets remain unchanged by that metadata.

See docs/emulator-compatibility.md and playbooks/LIBRETRO.md for evidence and
controller/profile details. Earlier blanket no-pickup statements in this dated
handoff are superseded by the user's new shared-supply/crown request.

## Shared collectibles after v0.5 (2026-11-01)

The user approved the policy in `docs/krusha-collectibles.md`. Read live source
and its linked validation report; v0.5 remains the frozen release.

- `src/krusha.c`: expanded whitelist; `806F544C` ammo classifier converts homing
  props to regular stock only at Krusha's collection. Native caps/HUD remain.
- Per-character crystal predicate `806F6E58` delegates character 5 to native
  global unlock `806F6EDC`; the latter loops only original characters 0..4 and
  camera/shockwave. `krushaRoarStart` checks the same gate, then 150-unit cost.
- Remove the old fairy actor hook at `806C5C20`: no deliberate missed photo.
  Native fairy flag, film, refill and tutorial now execute normally.
- Bean (map52/type198) and pearl (map44/type1B4) scripted contact operation10,
  arguments1,1 has a scoped 20-unit touch test. Preserve script visibility60,
  collision70, native interaction predicate806419F8, and clam286 open state2.
  Native scripts still set all rewards/flags. No sixth Golden Banana reward.
- Balloon handler806A7600 suppresses hit event4 at807FBD70 only for five colored
  balloons while Krusha is active. Handles matching old-Kong shots after tagging;
  leaves K. Rool's special balloon and original-Kong behavior native.
- Full loaded/update actor list: pointers at807FB930, stride8, countu16 at
  807FBB34, max64. Render list807FBFF0/count807FC3F0 is **not** all live actors!
  `Memory.scene()` now exposes both as `loaded_actors` and `actors`.
- Permanent flag banks reorder on autosaves. Use active file807467C8, slot IDs
  807EDEA8..AB and native computed bank size; see test `flag_addr`. Never assume
  a hardcoded flag bank remains current after a native pickup/autosave.
