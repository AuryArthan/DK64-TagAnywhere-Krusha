# v0.6 shared collectible validation — 2026-11-01

The user approved this exact tested build as **v0.6**. It implements the
[collectible policy](krusha-collectibles.md); the v0.5 tag and release BPS remain
unchanged. GitHub publication is prepared locally and runs after the user pushes
the tag and release workflow.

## Exact artifact

- ROM SHA256: `b933a3ec36f8e8b8cbcf8a06c4014b49625696077b7878dcb33fca1ac946f57f`
- MD5/native EEPROM prefix: `45ced182aba73f860e8ad339814f3837` / `45CED182`
- Size: 34,701,312 bytes; 16 KiB alignment retained.
- CIC-6105 checksums verified, along with `ED`/EEPROM16K metadata.
- Release BPS: `release-assets/v0.6/DK64-TagAnywhere+Krusha.bps`, SHA256
  `4178fc17e01fa577cc1977396db08d34b5b7507fdcc4e4207acdb0f214e8cd88`.
  Applying it to the required original USA ROM reproduces every target byte.
- Frozen v0.5 patch SHA256 remains
  `c52e247636d91e990b29f20835207f2fca6d48509d587c2ee3422c4f5b6c0dd8`.

## Gameplay checks

Tests use standalone Mupen64Plus/Glide64mk2 and pinned libretro
Mupen64Plus-Next/GLideN64 on Linux. Standard and Widescreen are exercised for
new supplies and real fairy captures. Reports record the executed ROM hash.
Only exact-ROM states generated from a cold boot of this artifact are reused.
The fresh-file test instead starts from an erased EEPROM and follows the long
opening story through ordinary menu/controller input.

Raw reports, screenshots and action logs are ignored/private beneath
`runtime/qa/collectibles-20261101/final-build/`. The maintained tools and
[workflow](../tools/README.md) describe how to reproduce them with a private ROM
and an explicit EEPROM fixture.

| Check | Assertions | Result |
| --- | ---: | --- |
| Cold boot and existing core gameplay | 34 | Passed |
| Standard/Widescreen crystal, film, homing conversion and original-DK controls | 28 | Passed |
| Locked/unlocked crystal prerequisites, locked film and headphones/DK refill | 14 | Passed |
| Standard/Widescreen real fairy targeting, shutter, shared capture and refill | 16 | Passed |
| All balloon colors by contact, bazooka collision, matching-DK positive control and late-shot tagging | 23 | Passed |
| Erased EEPROM, native introduction, fresh Speed Mode OFF Krusha and zero crystals/locked shout | 13 | Passed |
| Shared Helm key, native opened-door prerequisites, Speed Mode OFF celebration and excluded medal | 8 | Passed |
| Nintendo/Rareware native reward scripts with win-return prerequisites | 14 | Passed |
| All five pearls, closed-clam gate, bean enemy/reveal gate and excluded Golden Banana rewards | 21 | Passed |
| Mupen64Plus-Next cold boot, native options and adventure checkpoint | 5 | Passed |
| Mupen64Plus-Next Standard/Widescreen supplies and original-DK ammo comparison | 28 | Passed |
| Mupen64Plus-Next Standard/Widescreen real fairy captures and return/refill | 16 | Passed |
| Native KRUSHA ON/OFF, five/six selectors/barrels and full-restart option persistence | 29 | Passed |

**249 assertions passed across 13 completed reports on this exact ROM.**
[Machine-readable summary](qa/krusha-collectibles-20261101.json) records every
accepted assertion and raw report hash. Earlier/intermediate builds and failed
fixture attempts are excluded. A separate rebuild produced identical ROM bytes.
No gameplay crashes were observed in these accepted runs.

The core checks cover movement/jumping, six-way D-pad tagging, camera entry/
photo/exit, shout start/finish, pause/resume, boulder lift/drop/throw, swimming,
climbing, native orange pickup, excluded colored coins/bananas, and all three
shop visits. Headphone testing uses Fungi's actual active headphone actor;
Galleon's inactive/gated setup entry is not evidence of a missing headphone.
The balloon late-shot test uses a real DK coconut, tags natively to Krusha
while it remains in flight, and positions it for native collision. It writes
neither a collision result nor a reward flag.

## Fixtures and limits

Position, resource-stock, aspect and prerequisite flags are explicit test
fixtures. Mechanics still use native input/contact/projectiles/scripts/shutter.
There are no test writes to identity, action, animation, code, or collection
results. Fairy fixtures keep a real moving fairy in the lens over the native
shutter interval; the game performs targeting and capture itself. A successful
photo can run the native first-photo refill/tutorial before control returns.

Keys require a valid native access/reward-script context. Teleporting straight
behind a locked coin door can collect a visible model while skipping the door
script's key-flag monitor. The diagnostic controls compare DK and Krusha with
the same opened-door prerequisite; no key result flag is supplied as a fixture.
Unique coin checks use the native arcade/Jetpac win-return prerequisite, and
are not claims of completing those minigames as Krusha.

The full legacy v0.5 graphics suite is not claimed as completed on this ROM.
Early input attempts during the camera shutter/gun-draw transitions were rejected
normally by the game; the harness now waits for native frames. Accepted pickup/
fairy tests use their own completed cold-boot seed and matching-ROM state.

This is focused gameplay/regression testing, not a complete campaign, every
boss/minigame, multiplayer, Batocera OS or original-console certification.
No new boss/minigame access, Tiny quest abilities, shop inventory or sixth
Golden Banana rewards were added. Existing character-specific requirements
remain relevant even when Krusha is allowed to pick up a shared item.

The player's v0.5 native EEPROM was copied into the new normal profiles without
overwriting files; both originals and old states remain. QA progression was
not copied into a player profile. Create new savestates for this ROM.
