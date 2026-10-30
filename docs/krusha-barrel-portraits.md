# Krusha exterior tag-barrel portrait and startup lineup

The adventure barrel now depicts the approved tightened T portrait as a sixth
face between Chunky and Donkey Kong. With Krusha OFF, the original five-face
barrel is used at its original size. Interior six-character selection and existing
Krusha animations retain their prior implementation.

The barrel shell is enlarged by the allowed 15%. Six portrait cells and twelve
facets give each face two curved segments, following the same bulged profile as
vanilla. Portraits keep their native absolute height; the new middle chord is
approximately 2.2% narrower than the old one. This uses enlargement and closer
spacing before any meaningful face-size reduction. Faces do not overlap.

The original portrait display-list sections keep their five native visibility
masks. Krusha's additional decal is attached to the root, so it requires no new
skeletal matrix and no collectible/unlock flag. A fresh locked-Kong barrel can
still expose its four original question marks while DK and Krusha stay available.
The shell's question-mark UV height is kept at its original physical scale to
prevent its top/dot showing beyond the unchanged-size unlocked portraits.

Normal builds use `build/barrel_assets.py` and the committed approved PNGs in
`assets/krusha/barrel/`. Three uncompressed files are appended in previously unused
pointer table 27. A loader trampoline redirects model-table 5 index 0xC0 only when
Krusha is enabled, and the two reserved geometry-texture IDs 7001/7002 always map
to the custom halves. Other resource requests pass straight to the original loader.
Using its native allocation and reference tracking avoids private heap ownership
or per-frame model rebuilding. The original model and geometry textures remain
byte-identical in their original tables.

The startup graphic `bin/Nintendo_Krusha.png` is now the user's exact adjusted
232×48 PNG (`extended-six-heads_adjusted.png`). It is preserved without any
regeneration, resizing or recoloring. The native CPU framebuffer copy derives
its width, centered position (44,96), and row stride from the PNG. One source
texel maps to one native 320×240 framebuffer pixel. The original Nintendo image,
widescreen code and approved barrel assets remain unchanged.

Validation tools in the workspace:

- `tools/krusha-barrel-asset-check.py` checks preservation of native assets,
  complete portrait conversion, texture references, layout and unchanged audio.
- `DK64_BARREL_PORTRAIT_REVIEW=1 tools/krusha-options-test.py` exercises native
  ON/OFF menus, EEPROM persistence, five/six selection and which exterior loads.
- `tools/krusha-barrel-portrait-test.py` captures full rotations and checks locked
  portraits, native entry/exit, Krusha's moves and Standard/Widescreen.
- `tools/krusha-barrel-extra-test.py` exercises all character selections, native
  animations, locked-Kong skipping and another level's barrel.

Inspection screenshots, exact-ROM reports and the approved native-format preview
are packaged in `runtime/krusha/barrel-portrait-review/` at workspace level.

The startup revision is checked separately with
`tools/krusha-startup-logo-test.py`: cold boots at 320×240 and 640×480 compare all
11,136 source texels against the CPU-written framebuffer, followed by normal
menu/adventure entry and Krusha barrel selection. Its evidence is in
`runtime/krusha/startup-logo-adjusted-review/`; earlier barrel reports remain intact.
