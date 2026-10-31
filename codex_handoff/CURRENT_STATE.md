# Current state — 2026-10-31

## Accepted game

- Project: **Donkey Kong 64 — Krusha + Tag Anywhere**, by Arthan, extending
  Isotarge's Tag Anywhere. USA only; European/Japanese porting was explicitly dropped.
- Latest accepted checkpoint: **v0.4.2**; gameplay commit
  `18380a22d59c97b57957995ddc8f4d329c0bc9ab`.
- Latest documentation commit before this handoff:
  `3dd1a71e9e2777992e931e21bf5b4613fc563cf0`. Handoff commits will follow it;
  this is not an instruction to reset HEAD to that commit.
- Branch at handoff: `krusha-six-character-barrel`.
- Local upstream baseline: `e9ca72f5070c7e4bad69d37382c5a0798b06462f`.
- ROM: `rom/dk64-krusha-dev.z64` inside the repository.
- v0.4.2 ROM SHA-256:
  `dee2bbfcd04ba4ad1c0671e3f1ddd6d212ed1c94af0476caf12d9e862144d29d`.
- Size: 34,701,312 bytes; 16 KiB aligned; CIC-6105 header checksums verified.
- Native save/state filename prefix for this ROM:
  `Donkey Kong 64 (local build)-89C13EFB`.
- Normal launcher at workspace root: `./tools/play-krusha.sh`.
  The original parent workspace normal profile has a fresh exact-ROM **slot 5**,
  Krusha in Isles. New repo-local profiles are separate and start without that save/state.
- Latest detailed validation: `runtime/krusha/tree-tag-fix-review/index.html`
  and `RESULTS.md`, relative to the full workspace.

The exact game build passed **723 assertions**: nine reproduction timings,
541 matrix assertions (112 tree approaches and 44 ordinary airborne-tag cases),
33 assertions across eight vine cases, and 140 focused existing regressions.
Standard/Widescreen and Krusha ON/OFF were covered. No crashes or new regressions
were observed in the accepted checks. This is not a full 101% campaign,
all-minigames/bosses/multiplayer certification, or physical-hardware validation.
The prior v0.4.1 QA had 555 passing assertions and one tree-tag finding, now fixed.
Do not add those old-build counts to this build's validation total.

## User-approved behavior to preserve

Krusha is character index **5**, actor **7**, always unlocked, sixth after Chunky.
D-pad Left/Right (and forward L) tags; barrels also have six animated slots.
The saved KRUSHA option returns both selectors and the exterior barrel to five
characters when OFF. Original Kongs still require normal unlocks with Speed Mode OFF.

Krusha starts unarmed; native bazooka equip/fire/holster/aim and camera exits
must keep the mesh correct. He uses shared ammo, throws oranges, carries boulders,
uses numbered bananaports, and enters/exits shops safely. Shop stock is empty.
He **cannot collect anything yet**; other Kongs refill shared supplies. The fairy
camera consumes film but grants no capture flag/reward. Do not silently expand
progression or give him Chunky's collectible identity.

The shout uses the last 4/5 of burp clip 2AA, playback speed 1.2, and only the
supplied **TheScream3.wav** in stereo, normalized/encoded to a safe native ceiling.
No older harmonies, added echoes, alternate scream, or duplicate gain layers.
It costs 150 internal crystal units (one displayed crystal) and uses native
instrument enemy death, not a custom delete-all-enemies loop. Instrument-pad
songs/flags are not implemented. Keep the accepted darkening, spotlight,
centered camera, zoom, 360-degree orbit and shake. See live roar source for final
camera constants; earlier notes describe superseded requests.

Visible size is 110%, consistent across adventure/barrel/shop use. The barrel
shell is 115% with the approved portrait between Chunky and DK. Preserve the
approved exact startup lineup image and the Arthan credit. Widescreen HUD,
sprites, pause layouts, instruments and initial barrel transition are corrected;
Standard-mode placement should stay unchanged. Overscan is deliberately left
to emulator display settings instead of a ROM change.

## Scope and release status

The user is happy with this feature set for a first release. Original-N64 support
is an eventual goal, but hardware was unavailable. v0.4.1 was padding-only and
v0.4.2 keeps it. Do not claim console compatibility from emulator success.

The README covers this hack rather than copying the full upstream README;
five gameplay PNGs, a standalone build guide, milestone history and this handoff
are committed. There is no outstanding game fix.

Publication decision (subsequent user request): keep full source PRIVATE, reuse
public `https://github.com/AuryArthan/DK64-TagAnywhere-Krusha` for only the latest
BPS file. The private source destination has not yet been supplied; the source
repo's origin still points to Isotarge upstream, so do not push source there or
to the public patch repository.

Workspace `public-patch-release/` is a separate clone of that public repository.
Its fetched main was c25c5ca (old patch deleted). Local commit 726253d and annotated
tag v0.4.2 add only `DK64-TagAnywhere-Krusha.bps`, copied/hash-verified from the
frozen v0.4.2 checkpoint. The requested public upload has NOT happened: HTTPS
push dry-run failed because terminal GitHub authentication was unavailable.
Authenticate locally before completing it; do not request credentials in chat.
No force-push is needed. Recheck remote state if the user updates it via the web.
A local ZIP prepared earlier is optional and is not the user's chosen public format.

## Workflow migration after the handoff snapshot

Maintained setup/build/BPS/play/control and core/barrel/gun/options/tree/vine/shout
regression helpers now live in repository `tools/`. They resolve source paths
from this repo, not its parent. Consult `tools/README.md` for exact commands.
Runtime/tool downloads are ignored. Test saves are explicit private fixtures via
DK64_TEST_SAVE, and new output directories protect old reports. The runner is
`tools/run-regressions.py` with DK64_QA_OUT. Source layout changed; accepted game
code, v0.4.2 tag and ROM identity remain the same. Parent-workspace tools, saves
and historical evidence were retained. Future AI should use tracked workflows.

Migration verification: the same v0.4.2 ROM was rebuilt from a separate clone
(path with spaces), emulator/RDRAM startup succeeded there, and 140 migrated
gameplay regressions passed. See `docs/workflow-validation.md` for precise limits
and local output paths. No game release tag or source ROM was changed.

## Commit identity correction

At the user's explicit request, unpublished project commits and our annotated
taggers were rewritten to AuryArthan <sean.arthan@protonmail.com>. Upstream
contributors and already-published public-repository commits were preserved.
Git IDs changed, while all file trees and the v0.4.2 ROM stayed identical.
`identity-rewrite.json` maps old IDs (including historical report/checkpoint
references) to current IDs. Frozen raw reports and checkpoint bundles still
contain their original IDs; use the map rather than resetting to those old refs.
Recovery bundles are outside Git at runtime/identity-rewrite-backup in the
original workspace. Do not push those older-identity backup bundles.
