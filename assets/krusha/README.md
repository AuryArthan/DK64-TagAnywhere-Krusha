# Supplied Krusha scream

`TheScream.wav` is the user's original recording, copied unchanged from
`input_files/TheScream3.wav`. The user requested a 65% contribution from this
recording and 35% from the preceding native layered roar.

`scream.json` records checksums and conversion settings. The normal ROM build
uses the checked-in `TheScream.adpcm` and generated `scream.h`; no external audio
file, encoder, or host sound playback is needed to play the resulting ROM.
The source WAV is retained so later versions can be regenerated.

To regenerate from the workspace root:

```sh
python3 dk64-tag-anywhere/build/prepare_scream.py input_files/TheScream3.wav
```

The converter uses FFmpeg and the MPL-2.0 VADPCM encoder from
https://github.com/depp/vadpcm at commit
`413d52043a928c5fac066ccda1e69b73c7f7132b`, installed at
`tools/vadpcm/build/vadpcm`. Conversion produces 22050 Hz mono, preserves pitch
and duration, removes DC, and applies short click-prevention fades. The encoder
reported approximately 42 dB signal-to-quantization-noise ratio on this file.

A separate resident one-sound bank streams the 44163-byte VADPCM payload from
ROM offset `0x02100000`. The original game sound banks remain intact. The N64
sound allocator owns and releases each voice, using a persistent handle. Mixer
volumes are 65% for this sample and 35% for every layer and echo of the old roar;
these are amplitude weights without per-source loudness normalization.

The current playback multiplies the whole 65/35 blend by **1.5**: sample
volume 31,949, and the preceding roar layers/echoes at 52.5% of their
original volumes. This gain is applied by the resident sound code; the source
recording and encoded VADPCM payload remain unchanged.

The latest requested increase multiplies that whole blend by another **1.4**
(**2.1x** overall). The supplied recording uses two synchronized native voices
at volumes 32,767 and 11,962 to exceed one voice's ceiling safely. Each has
an independently owned persistent handle. Other layers/echoes play at 73.5%
of their original levels; source and encoded recording remain unchanged.
