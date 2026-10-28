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
