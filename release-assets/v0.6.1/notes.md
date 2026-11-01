## Donkey Kong 64 — Krusha + Tag Anywhere v0.6.1

Krusha as a sixth adventure character, built on Isotarge's Tag Anywhere.

### Changes since v0.6

- Krusha's charged B attack now has a gray expanding ring, matching his approved startup silhouette (`#ADADAD`), instead of DK's yellow.
- Preserve native damage, expansion, animation, crystal cost and fade. The five original Kongs retain their own colors.
- Use an independent model/cache identity so Krusha's ring cannot recolor a DK or enemy ring. Approved barrel portraits and startup artwork are unchanged.

**121 gameplay assertions plus 28 asset assertions passed** on this exact ROM: standalone Mupen64Plus/Glide64mk2 and libretro Mupen64Plus-Next/GLideN64, Standard/Widescreen, all six characters, repeated switching, core gameplay and native Krusha ON/OFF barrel/save persistence. This is targeted regression coverage, not full-campaign or physical-console certification.

### Installation

Apply **DK64-TagAnywhere+Krusha.bps** to a clean, original **Donkey Kong 64 USA big-endian .z64** ROM. Tag Anywhere and all previous Krusha features are included. Do not apply over v0.6 or another hack.

- Source ROM SHA-1: `CF806FF2603640A748FCA5026DED28802F1F4A50`
- Patched ROM SHA-256: `437d3de4f9679763df9293518cda6c31c4d4321bb32c61566eb02faeb64f6532`
- Recommended: **Mupen64Plus + Glide64mk2**, or **Mupen64Plus-Next + GLideN64**, CountPerOp = 1, 8 MB RAM, EEPROM 16K. Keep GLideN64 framebuffer emulation enabled.
- Use the game's Widescreen option for 16:9; leave the emulator's separate widescreen hack off.
- Native EEPROM progress can carry over. Cold boot v0.6.1 and create fresh save states.

The shared collectibles/fairy photography and earlier compatibility fixes remain included. Original hardware remains untested; 16 KiB ROM alignment and valid CIC-6105 checksums are retained.

Krusha patched in by Arthan. Based on Isotarge's Tag Anywhere and its contributors. Original game and characters by Nintendo/Rare.

Patch SHA-256: `fffc40d9f9e6e21a4911d6628322be00e7ac5a5fd0c23b20b138878c601b5abf`
