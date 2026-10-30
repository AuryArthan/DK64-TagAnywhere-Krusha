# Tree-tag origin warp

The inherited Tag Anywhere bug can send the player to approximately
`(0, 136, -26)` when a D-pad tag coincides with grabbing a tree. This was
reproduced in v0.4.1 without writing a character ID, action, animation, or game
code. Native button inputs caused the transition.

## Cause and scope

Native action `0x3B` (`806EDFF8`) rebuilds the player's model and skeleton via
`806C8E58` / `806C8F8C`. The player control routine runs afterward, before the
usual actor bone update. Its tree/vine finder (`8072F230`) calculates attachment
using player bone 1 (`8072FA14` / `80671C0C`). A grab during that interval can
therefore use the newly allocated skeleton before its world matrices are built.
The bad attachment persists as climbing state `0x59` at the origin.

Deferring the tag until native action dispatch did not resolve this ordering
problem and is **not** part of the fix.

## Fix

Replace only action-table slot `0x3B` at `80752D5C` with a wrapper that first runs
the complete original action. In adventure mode, for the current player, it
then sets the native tree/vine regrab cooldown (PaaD `+0x100`, signed 32-bit) to
one **only if it is zero**. The native player control routine skips grabbing
for that update and decrements the cooldown. The ordinary actor update builds
the new skeleton. Grabbing is available on the following update.

No position repair, proximity heuristic, character spoof, custom attachment,
extra skeleton build, or blanket prohibition on airborne tags is used. Longer
native cooldowns are preserved. The existing rule against tagging while already
climbing remains. The guard applies to all adventure Kongs with Krusha ON or
OFF; multiplayer and other game modes retain the original action behavior.
The action-table pointer receives an explicit data-cache writeback.

## Reproduction and tests

`tools/trace-tree-tag.py` cold-boots each ROM and creates its own native
checkpoint, then frame-steps nine jump/tag timings at the Japes entrance tree.
The unmodified v0.4.1 reference warped at delays 3, 4, 5, 6 and 7. The fixed ROM
kept valid positions at all nine timings. At delay 8 the player was already
climbing, so the normal tag restriction kept Krusha selected.

`tools/krusha-tree-fix-matrix.py` broadens the checks to every source character,
both tag directions, Standard and Widescreen, and the five-character Krusha OFF
mode. It also checks ordinary airborne tags, cooldown expiry, continued climbing,
and jumping off. `tools/krusha-tree-fix-regressions.py` runs the existing focused
gameplay, pickup, shop, bazooka, barrel, and native options tests in a separate
profile. Reports include the exact ROM SHA-256 and logged fixtures.

Review artifacts are under `runtime/krusha/tree-tag-fix-review/`. Original
v0.4.1 results and checkpoints are preserved. Emulator states are generated for
the exact ROM under test; only native EEPROM saves are portable between builds.
Real console hardware remains untested.
