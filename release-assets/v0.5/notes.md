## Donkey Kong 64 — Krusha + Tag Anywhere v0.5

Krusha as a sixth adventure character, built on Isotarge's Tag Anywhere. Always available through D-pad tagging and six-character tag barrels, with a native bazooka, camera, vocal instrument move and a saved KRUSHA ON/OFF option.

### Changes since v0.4.2

- Fix widescreen fairy-camera and upgraded weapon-scope obstruction under GLideN64, and make underwater tint cover the full viewport.
- Let Krusha collect melon health, standard weapon ammunition and separate grenade oranges, and enter crown arenas to earn their shared rewards.
- Prevent Chunky from tagging while carrying boulders, matching Krusha.
- Have Snide call Krusha a Kremling while keeping original Kong dialogue intact.
- Declare the required 16-Kbit EEPROM save size for automatic detection in supporting emulators/loaders.

The exact ROM passed **221 assertions**: 81 Mupen64Plus-Next checks (including threaded graphics and native EEPROM persistence) and 140 existing standalone Mupen64Plus gameplay regressions. Japes crown victory, reward, return and resumed movement were tested. This is not a complete-campaign or physical-console certification.

### Installation and emulator settings

Apply **DK64-TagAnywhere+Krusha.bps** to a clean, original **Donkey Kong 64 USA big-endian .z64** ROM. Tag Anywhere is included; do not apply over another hack or older patched ROM.

- Source ROM SHA-1: `CF806FF2603640A748FCA5026DED28802F1F4A50`
- Patched ROM SHA-256: `98e0b5cc3a0b5e9067ce0595e57217518e248822056a31d01ccceaac18da535a`
- Recommended: **Mupen64Plus + Glide64mk2**, or **Mupen64Plus-Next + GLideN64** (libretro/RetroArch), with **CountPerOp = 1**, 8 MB RAM and EEPROM 16K saves. Keep GLideN64 framebuffer emulation enabled.
- Use the game's Widescreen setting for 16:9; leave the emulator's separate widescreen hack off.
- Back up native saves before changing builds; cold boot v0.5 and create fresh save states.

Kong-specific collectibles remain excluded for Krusha. Other Kongs still refill crystals and camera film; Krusha's photos do not grant fairy capture rewards, and his shout does not perform instrument-pad puzzle songs. Shops have no dedicated Krusha stock. Original N64 hardware remains untested; 16 KiB ROM alignment and valid CIC-6105 checksums are retained.

Krusha patched in by Arthan. Based on Isotarge's Tag Anywhere and its contributors. Original game and characters by Nintendo/Rare.

Patch SHA-256: `c52e247636d91e990b29f20835207f2fca6d48509d587c2ee3422c4f5b6c0dd8`
