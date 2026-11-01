## Donkey Kong 64 — Krusha + Tag Anywhere v0.6

Krusha as a sixth adventure character, built on Isotarge's Tag Anywhere.

### Changes since v0.5

- Collect Crystal Coconuts and camera film, and photograph Banana Fairies with native capture flags and post-photo refill.
- Unlock the shout and crystal pickups with the normal shared crystal prerequisite. Fresh Speed Mode OFF files start at zero crystals with the shout unavailable.
- Convert homing ammo pickups into regular bazooka ammunition for Krusha; original Kongs retain normal homing ammo behavior.
- Allow shared keys, unique Nintendo/Rareware coins, pearls, the bean and temporary DK coins, retaining native access/reward prerequisites.
- Keep all colored bananas/balloons, Golden Bananas, colored/rainbow coins, blueprints and medals excluded. Candy's headphones do not refill shout crystals.
- Protect colored balloons from an original Kong's projectile left in flight when tagging to Krusha.

**249 assertions passed across 13 completed reports** on this exact ROM, covering standalone Mupen64Plus/Glide64mk2 and libretro Mupen64Plus-Next/GLideN64, Standard/Widescreen supplies and fairy capture/refill, quest rewards, fresh Speed Mode OFF, and ON/OFF selector/barrel/native-save persistence. Logged position/resource/prerequisite fixtures were used; arcade/Jetpac themselves were not completed. This is not complete-campaign or original-console certification.

### Installation

Apply **DK64-TagAnywhere+Krusha.bps** to a clean, original **Donkey Kong 64 USA big-endian .z64** ROM. Tag Anywhere is included; do not apply over another hack or an older patched ROM.

- Source ROM SHA-1: `CF806FF2603640A748FCA5026DED28802F1F4A50`
- Patched ROM SHA-256: `b933a3ec36f8e8b8cbcf8a06c4014b49625696077b7878dcb33fca1ac946f57f`
- Recommended: **Mupen64Plus + Glide64mk2**, or **Mupen64Plus-Next + GLideN64** (libretro/RetroArch), **CountPerOp = 1**, 8 MB RAM and EEPROM 16K. Keep GLideN64 framebuffer emulation enabled.
- Use the game's Widescreen setting for 16:9; leave the emulator's separate widescreen hack off.
- Native saves can carry over; cold boot v0.6 and create fresh save states.

Krusha still has no dedicated shop stock or instrument-pad puzzle songs. Shared quest pickups do not grant every original Kong's ability or open every boss/minigame. Earlier v0.5 rendering fixes are retained. Original N64 hardware remains untested; 16 KiB ROM alignment and valid CIC-6105 checksums are retained.

Krusha patched in by Arthan. Based on Isotarge's Tag Anywhere and its contributors. Original game and characters by Nintendo/Rare.

Patch SHA-256: `4178fc17e01fa577cc1977396db08d34b5b7507fdcc4e4207acdb0f214e8cd88`
