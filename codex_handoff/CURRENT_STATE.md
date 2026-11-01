# Current state — v0.6.1 checkpoint, 2026-11-01

## Accepted v0.6.1 checkpoint

The user approved the gray charged-B shockwave as **v0.6.1** and requested
its patch for release on push. The gray is **RGB 173,173,173 / #ADADAD**, sampled from tracked
`bin/Nintendo_Krusha.png` (the user's filename is relative to the source repo).
Read [the color audit](../docs/krusha-character-colors.md) for the implementation,
other color uses and QA. v0.6.1 ROM SHA256:
`437d3de4f9679763df9293518cda6c31c4d4321bb32c61566eb02faeb64f6532`.
MD5 is `a593924704abf4786d7272b3410e9ade`; native EEPROM prefix **A5939247**.
Both normal launcher profiles received a non-overwriting copy of their own
v0.6 player's EEPROM under this new ROM hash/prefix. Original saves and states
remain intact; no old-ROM states were copied. QA uses separate ignored profiles
under `runtime/qa/character-colors-20261101/`.

The source adds a separate gray ring model/cache identity and six RGBA32
frames, retaining native alpha/fade, geometry, damage, cost and timing. Other
Kongs' rings and original enemy effects remain native. No additional incorrect
Krusha identity-color fallback was found in the audited adventure paths.
Item/ownership colors, slam upgrade colors and shared particles keep their
semantic/native colors. This does not recolor Krusha's blue skin or portrait.

This exact v0.6.1 ROM passed **121 gameplay assertions across four
reports**, plus **28 asset assertions**. Standalone core/all-six-ring/options
and Mupen64Plus-Next/GLideN64 focused rings completed with every check passing;
Standard/Widescreen and native Krusha OFF/ON barrels/persistence were covered.
A separate rebuild matched every byte. The committed
[QA summary](../docs/qa/krusha-character-colors-20261101.json) records final
reports/hashes. No full campaign or physical-hardware certification. Do not
count interrupted probes, the first short Next step budget, or v0.6's old
249 assertions toward this new ROM.

The v0.6.1 patch is `release-assets/v0.6.1/DK64-TagAnywhere+Krusha.bps`,
SHA256 `fffc40d9f9e6e21a4911d6628322be00e7ac5a5fd0c23b20b138878c601b5abf`.
The frozen backup is `../runtime/checkpoints/v0.6.1/`. Tested gameplay source:
`1f8f8423cecf12fe1e5714d84b0f09ccb267509c`. The annotated v0.6.1 tag points to
`2d0e424ce76f7299c7e23741c807d47574d3e231`; its later preparation commit adds the pinned publisher/workflow.
The publisher is `tools/publish-v061.py`, with workflow
`.github/workflows/release-v061.yml`. Push the tag first, then the branch:

```sh
git push origin refs/tags/v0.6.1
git push origin HEAD
```

See release-assets/README.md. Publication
is prepared locally, not verified as hosted. No GitHub push was performed here.
Earlier tags, patches and backups remain intact. No new gameplay change was
made while versioning this already-tested ROM.

The following v0.6 and older sections are historical. Their publication commands
are not instructions to republish an older release as latest.

## Accepted v0.6 checkpoint

The user approved the tested [collectible policy](../docs/krusha-collectibles.md)
implementation as **v0.6**, and requested a BPS release on push. ROM SHA256 is
`b933a3ec36f8e8b8cbcf8a06c4014b49625696077b7878dcb33fca1ac946f57f`,
MD5 `45ced182aba73f860e8ad339814f3837` (native EEPROM prefix **45CED182**).
The v0.6 patch is tracked at `release-assets/v0.6/DK64-TagAnywhere+Krusha.bps`,
SHA256 `4178fc17e01fa577cc1977396db08d34b5b7507fdcc4e4207acdb0f214e8cd88`.
The annotated `v0.6` tag points to `3fc3627e09c9a581c9326e50548df3a2379783a7`.
`tools/publish-v06.py` and `.github/workflows/release-v06.yml` verify and publish
only this approved tag/patch. The checkpoint and workflow are prepared locally;
hosted publication has not been verified in this session. A user push may
already have happened; check current evidence before treating publication as an
outstanding task. Do not claim hosted publication from local validation.
The frozen backup is `../runtime/checkpoints/v0.6/`. Earlier tags/assets stay intact.
Tested gameplay source commit: `79cdc585abd75afa8fe1d00d0c17804e9cf1fed3`.

Implemented: shared crystals with native unlock/shout gate, film, real fairy
captures/refill, homing pickups converted to regular bazooka stock, shared
key/quest/challenge pickup eligibility, scoped bean/pearl contact, colored
balloon hit protection (including shots left in flight when tagging). Headphones
stay unusable; original-Kong progression and rainbow coins stay blocked. No new
boss/minigame access, shop stock, Tiny abilities or instrument-pad songs.

This exact v0.6 ROM passed **249 assertions across 13 complete reports**:
standalone core/supplies/locks/balloons/quests/keys/coins/new-game/options plus
Mupen64Plus-Next native boot and Standard/Widescreen supplies/fairy captures.
A separate rebuild matched every byte. No complete campaign or hardware claim.

Read [validation](../docs/krusha-collectibles-validation.md) for the final checks
and their limits. Do not add v0.5 or intermediate-ROM test counts to this build.
Both normal launcher profiles received a non-overwriting copy of the player's
v0.5 native EEPROM under the new prefix; originals/states were retained. No
cross-ROM savestates were imported. QA profiles remain private/ignored under
`runtime/qa/collectibles-20261101/`; their progression is not a player save.

## Release preparation and continuation

Release preparation commit: `ad2697625c1343d3c6c674de8c99107871df8746`.
It follows the v0.6 checkpoint tag and adds the publisher/workflow. Preserve both:
the tag identifies the versioned game, while the branch includes publication tools.
To publish when explicitly requested, push the existing tag, then the branch:

```sh
git push origin v0.6
git push origin HEAD
```

The workflow is **Publish v0.6 BPS**. See
[release instructions](../release-assets/README.md), including offline checks.
A tag-only push does not publish: the workflow was added in the later branch commit.
Further handoff/documentation commits do not change the tested ROM or move v0.6.
The frozen backup records the release-preparation state, not later docs updates.
No outstanding gameplay fix is recorded; continue the latest user request.

## Historical v0.5 checkpoint — 2026-10-31

The following sections are dated history, superseded by v0.6 above wherever they
conflict. Do not apply their old restrictions or resume their publication plans.

The user approved the tested compatibility build as **v0.5** and requested a
release-on-push BPS asset, like v0.4.2. This supersedes the historical snapshot
below: current ROM SHA256 is `98e0b5cc3a0b5e9067ce0595e57217518e248822056a31d01ccceaac18da535a`,
221 assertions passed across standalone Mupen64Plus/Glide64mk2 and libretro
Mupen64Plus-Next/GLideN64. Native EEPROM prefix is 3481FB2A. Shared health/ammo/
grenade pickups and crowns are now allowed; colored progression stays excluded.
README recommendations are deliberately concise and name the tested plugins.

The v0.5 patch is tracked at release-assets/v0.5/DK64-TagAnywhere+Krusha.bps,
SHA256 `c52e247636d91e990b29f20835207f2fca6d48509d587c2ee3422c4f5b6c0dd8`.
The annotated v0.5 tag points to `fb4a7f5e3d8131f3d0d3bc6f703fdd0e5a300d42`.
`tools/publish-v05.py` and `.github/workflows/release-v05.yml` publish only that
verified tag/patch. The frozen local backup is `../runtime/checkpoints/v0.5/`
(relative to this repository); it includes the Git bundle, exact ROM and saves.
User push is
needed for the hosted release; do not claim GitHub publication from local checks.
No existing tag or v0.4.2 release asset is overwritten. Original hardware remains
untested. Read release-assets/README.md for the publication instructions.

## Historical orientation (older decisions superseded above)

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
BPS file. The private source destination is now configured as origin:
`https://github.com/AuryArthan/DK64-TagAnywhere-Krusha.git`.
Isotarge's original repository is retained as upstream. The user will push;
configuring these remotes did not upload anything. Never push private source
to the public patch repository.

Workspace `public-patch-release/` is a separate clone of that public repository.
Its fetched main was c25c5ca (old patch deleted). Local commit 87d9c0a and annotated
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

## Publication plan changed after the first push

The user now wants source and patch releases together in the code repository,
with public visibility intended. A v0.4.2 release-on-push workflow and the exact
`DK64-TagAnywhere+Krusha.bps` are committed under `.github/workflows/` and
`release-assets/`. Read release-assets/README.md. Local API credentials remain
unavailable; the assistant did not publish a live release. A subsequent user push
runs the workflow with GitHub's automatic token. Repository visibility is not
changed by the workflow and anonymous API access was unavailable at preparation.
The earlier separate public patch clone remains local, with its old upload still
unperformed; it is no longer the chosen primary publication destination.

Repository rename: the unified source/release repository is now intended to be
`AuryArthan/DK64-TagAnywhere-Krusha` (without -code). Origin and release-publisher
repository guards/links were updated. The old separate `public-patch-release/`
clone is retired; its URL may now identify the unified repository after the
user's GitHub rename. Do not push its obsolete patch-only history to that URL.

## Unreleased development after v0.4.2: Mupen64Plus-Next fixes

The user reported seven Batocera/libretro issues. All seven now have source
fixes; read [the compatibility report](../docs/emulator-compatibility.md) for
implementation, screenshots, precise test evidence and emulator settings.
The development ROM SHA256 is
`98e0b5cc3a0b5e9067ce0595e57217518e248822056a31d01ccceaac18da535a`, MD5
`3481FB2ACB5E7FDA38BCC30C7F474008`, still34701312 bytes/16KiB aligned/CIC6105.
Its native standalone EEPROM prefix is `Donkey Kong 64 (local build)-3481FB2A`.
This is untagged development; accepted v0.4.2 and its public release asset remain
unchanged. Never use v0.4.2 or intermediate-build states to test this ROM.

The user's new pickup request supersedes the earlier blanket exclusion:
Krusha can now refill health, standard weapon ammo and separate grenade oranges,
and earn battle crowns. Colored coins/bananas and other Kong-specific progression
stay excluded; film/crystal pickups are still excluded. No global identity spoof.
Crown pads keep their native contact/button tests; Japes arena victory, reward,
return and resumed movement were tested. Snide says KREMLING for Krusha and KONG
for original Kongs. Chunky now shares Krusha's heavy-carry tag restriction.

The widescreen camera/scope obstruction was reproduced in GLideN64 and fixed
by correcting F3DEX2 OtherMode encodings in maskSides. Water tint now uses a
full-width projection independently of the HUD. Standard mode remains native.
The build also declares standard16-Kbit EEPROM metadata (`ED`, high version
nibble2): unrecognized ROMs otherwise defaulted to4-Kbit EEPROM in this core.
Automatic save-size detection and full-restart native option persistence passed.

Use optional `tools/setup-libretro-test.sh`, `control-libretro.py`,
`libretro-compat-test.py`, `libretro-save-test.py` for future core-specific QA.
The test core is SHA-pinned because its RDRAM pointer lookup is ELF-specific.
An input-only C proxy supplies a virtual controller; the official core does
all emulation/rendering. Frontend hotkeys use localUDP55357; do not run two such
controllers on the same port/profile/display. See tools/README.md. The original
standalone toolchain remains available. User hardware/Batocera version were not
provided; local tests used Linux/RetroArch/GLideN64, not a Batocera installation.

Final validation for that development ROM:81 libretro assertions (graphics23,
threaded graphics18, interactions26, complete-restart native EEPROM14) plus140
standalone regressions, **221 total**. All reports completed with matching98e0...
ROM hash and all assertions passing. No observed crashes. This does not repeat
v0.4.2's full tree/vine matrix or certify a complete campaign/original console.
Raw current evidence is in repo runtime/libretro-investigation/{verified-final-
profile,verified-threaded-profile,save-persistence-profile} and runtime/qa/
mupen-next-fixes-20261031. Public summaries and selected captures are committed.
The old v0.4.2 player's native EEPROM was copied, without overwriting any files,
into both repo and parent workspace runtime/roms/98e0.../saves/ under its new
3481FB2A filename. Originals and old states were retained; no old state was copied.
The user's usual parent tools/play-krusha.sh now launches the new development
ROM with that native save. No GitHub push, new version tag, or release update.
