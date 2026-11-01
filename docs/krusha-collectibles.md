# Krusha collectible policy — approved 2026-11-01

User-approved policy, implemented in development after v0.5. The v0.5 release
asset and tag remain unchanged; validation results belong to the new ROM hash.
Baseline: v0.5, ROM SHA256
`98e0b5cc3a0b5e9067ce0595e57217518e248822056a31d01ccceaac18da535a`.

Approved rule: permit shared supplies and shared progression items; exclude
original-Kong inventories and rewards. Explicitly exclude rainbow coins too.
The tables describe intended behavior. See the implementation/testing report for
actual checks and limits; this approval is not a claim of full-campaign testing.

## Ordinary supplies

| Item | Policy | v0.5 / reason |
| --- | --- | --- |
| Crystal Coconuts | Allow; highest priority | Missing from the whitelist. Refill the existing shared pool used by the shout. Shout and pickup remain unavailable until the native shared crystal unlock; fresh Speed Mode OFF starts at zero. |
| Watermelon slices | Allow | Already allowed/tested, including enemy drops. |
| Melon crates | Allow breaking them and collecting their slices | Container interaction is separate from slice eligibility; do not treat a crate as an inventory item. |
| Normal ammo crates and loose ammo | Allow | Already allowed/tested. The five projectile-shaped pickups refill shared normal ammo; their shapes do not make their inventory Kong-specific. |
| Homing-ammo crates | Allow as REGULAR ammunition | Krusha credits homing pickups as regular bazooka ammo at collection, including drops left by another Kong. No homing firing mechanics or new weapon upgrade. |
| Orange grenades | Allow | Already allowed/tested; separate from bazooka ammo. |
| Camera film | Allow, once the camera is unlocked | Missing from the whitelist; existing shared film pool/capacity. |
| Candy's headphones | Block | User chose no headphone refill: Krusha shouts rather than plays music. Keep sixth instrument stock at zero; do not refill crystals from headphones. |

## Progression and quest items

| Item | Policy | Reason / boundary |
| --- | --- | --- |
| Battle crowns | Allow | Shared completion flags; already supported/tested in v0.5. |
| Boss keys | Allow collection | Shared completion flags. Does not imply making every boss playable as Krusha; key collection, celebration and return need testing. |
| Banana Fairies | Allow photographing and earning the shared capture flag | Not Kong-owned. Remove the old deliberate miss hook; retain native targeting, shutter, capture flag, save and post-photo refill. |
| Nintendo Coin | Allow | Unique shared progression token, not spendable colored currency. Keep arcade access/reward prerequisites intact. |
| Rareware Coin | Allow | Same distinction; keep Jetpac access/reward prerequisites intact. |
| Pearls (Gloomy Galleon) | Allow pickup | Global pearl flags, despite their association with Tiny's quest. Preserve Tiny's Golden Banana ownership and native quest restrictions; do not promise Krusha can reach every pearl or complete the reward conversation. |
| Bean (Fungi Forest) | Allow pickup | Shared quest item, despite its association with Tiny. Preserve the original Golden Banana owner and native delivery/reward conditions. |
| Colored banana singles | Block | Original Kong's banana counter. |
| Colored banana bunches | Block | Same, including bunches spawned by other interactions. |
| Colored banana balloons | Block all interaction | Ghosted/inert like a wrong-color balloon for an original Kong: no popping or banana awards from Krusha's bazooka. |
| Golden Bananas | Block all | Explicit user requirement, including bonus/quest rewards and the Rareware Golden Banana. |
| Colored banana coins | Block all five colors | Original Kong's wallet. |
| Rainbow coins / 5-Banana Coins | Block | Explicit exception; credit the five original wallets. Audit spawned/dig-up actor route too. |
| Blueprints | Block all five colors | Belong to an original Kong and lead to that Kong's Golden Banana. Include Kasplat drops. |
| Banana medals | Block | Original Kong/level completion, including physical Hideout Helm medals. An uncolored-looking medal is still not a sixth-character reward. |

## Temporary challenge items and objects

| Item | Policy | Boundary |
| --- | --- | --- |
| DK coins in races/minecarts/minigames | Allow within their challenge | Temporary challenge score, not colored shop currency. This does not authorize new access to every minigame. |
| Temporary checkpoints, hoops, stars, KONG letters, challenge bananas | Preserve each challenge's intended collection rules if Krusha can enter | These are challenge mechanics rather than persistent adventure inventory. A colored-banana-shaped challenge object must be distinguished from real Kong banana progression. Do not globally remove character requirements. |
| Apple carried to the worm (Fungi Forest) | Leave Chunky's quest restricted initially | A carried quest actor and delivery script, not a normal pickup counter. Optional later extension; Krusha's existing boulder carry does not prove this works. |
| Boulders, vases, cannonballs, throwable barrels, animal crates | Outside this pickup change | Interactable actors/transformations. Preserve existing supported behavior and character restrictions unless separately requested. |
| Multiplayer-only powerups | Outside this adventure change | Do not broaden multiplayer patches through an adventure collectible whitelist. |
| Shop moves, weapons, belts, health/instrument upgrades; camera/shockwave unlock | Outside this pickup change | Purchases/unlock scripts, not loose pickups. Krusha still has no dedicated shop stock; shared prerequisites should remain meaningful. |

## Evidence and implementation cautions

- `src/krusha.c`, `krushaModelPickupAllowed`, permits model2 types 0x11,
  0x48, 0x56, 0x57, 0x8E, 0x8F, 0x91, 0x98, 0xEC, 0x13C,
  0x15D–0x160, 0x18D, 0x198, 0x1B4 and 0x28F for enabled adventure
  Krusha. The original eligibility function still owns the remaining gates.
  Homing crates use normal-crate eligibility; homing loose props are classified
  as normal ammo at collection. Multiplayer coin 0x1D2 is deliberately excluded.
- `build/model2_names.py` identifies homing crate 0x11, crystals 0x8E, film
  0x98, boss key 0x13C, bean 0x198 and pearl 0x1B4. These are names/IDs,
  not proof that merely adding each ID is safe or sufficient.
- The local partial decompilation (`../dk64_decompillation/`) has native
  eligibility in `src/global_asm/code_F9450.c`, function 806F6644. Crystals
  and film have additional capability checks; homing crates check weapon
  upgrades. Its `hud.c` also gates crystal capacity on native unlocks.
- Native headphones in `src/global_asm/done/code_AAAF0.c`, function
  806A7BDC, read active character instrument ownership and refill HUD item 7.
  Crystals use HUD item 5. Avoid a sixth-index instrument-table access.
- The decompilation's `enums.h` contains individual pearl flags, per-Kong
  blueprints/medals and global coin/key flags. Collection can follow actor,
  model2, scripted reward or photographic paths, so a model2-only test is
  insufficient for this broader policy.
- Nintendo's [official manual](https://www.nintendo.com/eu/media/downloads/games_8/emanuals/nintendo_8/Manual_Nintendo64_DonkeyKong64_EN.pdf),
  printed pp. 14–17, confirms the principal item categories and distinguishes
  colored resources from shared supplies, special rewards and headphones.

## Implementation boundaries

- Crystal eligibility hooks native per-character predicate `806F6E58` only for
  character 5 and calls the native shared predicate `806F6EDC`. That predicate
  checks the five original crystal moves or camera/shockwave unlock. Shout
  start checks the same prerequisite and the existing 150-unit cost. Nothing
  grants crystals on a fresh file or deletes crystals from an existing save.
- Film keeps native camera ownership, stock and capacity rules. The old
  `806C5C20` fairy actor override that deliberately turned Krusha captures into
  misses is removed. Targeting, shutter, capture flags and native refill run
  unchanged, including the first-photo tutorial.
- Bean and pearl pickups use native scripted contact rather than the ordinary
  pickup list. A targeted body-touch condition is added only for the bean in
  map 52 and pearls in map 44. Visibility, collision and interaction-state gates
  remain; a pearl also requires its actual clam's open phase. Native scripts
  own the flags, disappearance and rewards. No Golden Banana reward is added.
- Colored balloon actor logic retains its native motion, appearance and
  collision rules. An additional hit guard suppresses a colored balloon reward
  while Krusha is active, including matching projectiles left in flight by
  another Kong. K. Rool's special balloon is outside this guard.
- Headphones remain native actor logic. Krusha has neither instrument ownership
  nor instrument energy, so they cannot refill his shout crystals. No crystal
  conversion is added to headphones.
- Unique Nintendo/Rareware coin reward scripts and challenge rules stay native;
  this does not open arcade/Jetpac/boss access or give Krusha shop stock.

See [validation](krusha-collectibles-validation.md) for the exact ROM identity,
checks and limits. The approved v0.5 tag and downloadable patch remain frozen.
