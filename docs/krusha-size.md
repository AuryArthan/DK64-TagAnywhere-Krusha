# Krusha appearance scale

The approved pre-enlargement build is annotated tag `v0.2`, commit
`a27e78c1fcd1648cab76895d53f9342a5a50a168`. The workspace checkpoint
`runtime/checkpoints/v0.2/` contains its exact ROM, BPS, offline source bundle,
native saves, matching emulator states and validation reports.

Krusha's complete model transform is now 1.1 times its former size in adventure
mode and in the sixth tag-barrel preview. The native shop presentation scales
remain intact: the final visual scale is 0.165 outdoors/in the barrel/in Candy's,
0.297 in Cranky's, and 0.264 in Funky's. The other characters and multiplayer
retain their original transforms. The existing KRUSHA option gates the change.

## Implementation

`krushaBuildActorBones` wraps the USA animation/bone update at 0x80614A64.
Only adventure Player actor 7 and tag preview actor 316 with identity 7 receive
the multiplier. The native `renderActor` first builds the actor's original root
matrix. During the skeleton update its nine rotation/scale components are saved
and multiplied by 1.1, then restored exactly after the native routine returns.
Translation stays unchanged. The enlarged animated bone matrices feed rendering,
held attachments and the roar camera's existing world-space body measurements.

Native animation scale fields, PaaD scale vectors and the persistent actor root
remain unchanged. Native relative/parent matrix handling remains native. There
is no multiplication of a previous frame's size and no adjustment that can leak
into a later character selection. Shop enlargement is retained once.

Early approaches changed persistent player/actor scale. Visible size checks
passed, but the automatic walk after leaving Cranky's stalled. Those approaches
were removed. A comparison using the original constructor and ordinary shop
visits isolated the persistent-transform problem. The final implementation
enlarges the skeleton update while retaining the original root for movement.
Diagnostic RAM edits were confined to discarded sessions; final checks use an
unmodified ROM, controller input, position fixtures and native loading-zone
redirects.

## Inspection and verification

`tools/krusha-scale-test.py` cold boots the exact development ROM, measures the
three basis lengths of the actual world-space skeletal matrix, and captures PNGs.
It checks repeated tags, unchanged DK size, bazooka fire/holster, camera/shout
recovery, sixth barrel preview/selection, all three shops and restored control
on exit. The native PaaD scale vectors are logged separately. Screenshots and
measurements are in `runtime/krusha/scale-review/`; the before measurements use
the immutable v0.2 ROM. Old-ROM emulator states must not be loaded into the new
ROM; the native EEPROM remains portable.

The final ROM passed 85 focused size/gameplay checks and 21 camera checks.
Across 438 consecutive shout frames in three camera setups the enlarged body
stayed visible, centered and retained the bounded shake/recovery. The size checks
also verified native control was restored after every shop exit. The BPS patch
was checked by reconstructing the exact ROM and verifying its CRCs.

`tools/krusha-size-shots.py` provides additional inspection views using normal
C-button zoom selection outdoors and logged position fixtures in the shops.
It keeps the native shop cameras; native conversation close-ups are retained
alongside the clearer inspection views. No appearance or camera writes are
used to prepare the screenshots.
