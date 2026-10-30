# Approved Krusha portrait and six-face barrel assets

`krusha-face-source.png` and `krusha-face-64.png` are byte-identical copies of the
user-approved tightened T files from `research/krusha/barrel-face-study/user_input/`:

- `krusha-T-user-short-upright_tight.png` — source for the startup silhouette.
- `krusha-T-user-short-upright_tight_64.png` — exact 64×64 barrel texture input.

Do not replace these with earlier generated portraits or the rejected community
cutout. The user approved these specific edited images. Their original files
remain unchanged outside the repository.

`build/barrel_assets.py` derives the model and native RGBA5551 halves on every
normal build. Colour uses the native 5-bit channels; alpha uses a 128 threshold
to exclude near-transparent PNG noise. Halves are 32×64 and vertically flipped
to match native barrel texture storage. The source PNGs themselves are untouched.
`layout.json` records geometry measurements and checksums.

The six-face model is 15% larger than vanilla, with twelve side facets and six
60-degree portrait cells. The portrait height remains the original 156 model
units. Its middle chord is 138 units versus the native approximately 141.07,
only about 2.2% narrower. No uniform portrait reduction is applied. UVs preserve
the underlying question mark's native physical height so it does not peek above
unlocked faces on the larger shell. Portrait order is DK, Diddy, Lanky, Tiny,
Chunky, Krusha, looping back to DK.

The five original bone/mesh masks remain native. Krusha's portrait uses the root
bone and is always visible when the custom model is loaded. No seventh skeletal
matrix or new character flag is required. Locked Kongs still show question marks.
The original five-face model and original geometry textures are not replaced.

The model and two image halves occupy a dedicated uncompressed pointer table 27
at ROM `0x02080000`. `krushaBarrelFile` redirects only enabled barrel model loads
and its two reserved texture IDs. All allocation, DMA, reference tracking and
cleanup use the native loader. With Krusha OFF, native model 0xC1 loads normally.
The custom region is checked not to overlap relocated pointer tables or the
existing scream audio at `0x02100000`.

## Startup lineup

`bin/Nintendo_Krusha.png` is a new 192×48 six-silhouette image; the original
`bin/Nintendo.png` remains unchanged. Existing heads are repacked, each just one
pixel narrower using nearest-neighbour sampling, so their RGB colours are retained.
Krusha's silhouette is derived only from the approved high-resolution alpha
outline and filled with gray **#ADADAD**, sampled from the user's color example.
No facial shading or detail appears in the silhouette. Keeping 192×48 avoids a
change to the native logo renderer or its aspect behavior. The normal build now
uses this new lineup; it is a startup credit graphic independent of the option.
