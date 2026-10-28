# Supplied Krusha scream

`TheScream.wav` is an unchanged copy of `input_files/TheScream3.wav`.
The instrument shout plays **only this recording**, preserving its original
stereo balance, pitch and duration. There are no native vocal overlays,
harmonics, added reverb/echoes, EQ, high-pass filters or duplicated gain voices.
The recording's own sound and effects are retained.

Playback uses one native voice per original channel, panned hard left/right,
at the maximum valid native volume **32767**. Both channels share one constant
normalization gain, preserving their balance. Encoding checks the decoded
VADPCM waveform against a **-0.5 dBFS ceiling** to leave a small peak margin.
The current encoded peak is about -0.60 dBFS; codec signal/noise is about 42 dB.

DK64's current audio path uses 22050 Hz audio and native VADPCM conversion. Two predictor
books and two channel streams are packaged in the committed `scream.h` and
`TheScream.adpcm`, starting at ROM `0x02100000`. `scream.json` records checksums,
channel offsets, normalization and decoded peaks. Ordinary ROM builds need no
audio encoder or external source file. Predictor books are aligned for DMA.

To regenerate from the workspace root:

```sh
python3 dk64-tag-anywhere/build/prepare_scream.py input_files/TheScream3.wav
```

This uses FFmpeg and the MPL-2.0 VADPCM encoder from
https://github.com/depp/vadpcm, commit
`413d52043a928c5fac066ccda1e69b73c7f7132b`, at
`tools/vadpcm/build/vadpcm`. Each native channel owns a persistent handle;
replay stops any previous channel voice, and the allocator clears both handles
on completion. No original game sound or music bank is replaced.
