# Krusha development checkpoints

These are the saved gameplay milestones. Version labels follow the existing Git
tags, including the historical `v3.1` spelling. Older checkpoints are preserved.

## v0.6.1 — Krusha identity color

Give the charged B shockwave its own gray model/texture frames, matching the
approved startup silhouette (#ADADAD). Preserve native attack behavior, all
five original ring colors and the approved barrel/portrait assets.
See the [color audit](krusha-character-colors.md). Previous version tags and patches are preserved.

## v0.6 — shared collectibles and fairy capture

Allow unlocked Crystal Coconuts and camera film; restore native fairy capture,
saving and post-photo refill. Gate Krusha's shout and crystal eligibility behind
the shared native crystal unlock, preserving an empty crystal supply on a fresh
Speed Mode OFF file. Credit homing pickups as regular bazooka ammunition at
collection time, including drops left by another Kong. Preserve original-Kong
homing ammunition, native resource caps, colored-balloon restrictions, blocked
Kong-specific collectibles and unusable headphones. Extend shared pickup policy
to keys, global quest tokens and temporary challenge DK coins without opening
new boss/minigame access. [Policy](krusha-collectibles.md).

## v0.5 — Mupen64Plus-Next compatibility and shared pickups

Correct widescreen camera/scope RDP commands and full-width underwater tint.
Allow Krusha health, standard ammo and separate grenade refills, plus native
battle-arena entry and crown rewards. Preserve colored collectible exclusions.
Block Chunky tags during heavy carrying and address Krusha as a Kremling in
Snide's dialogue. Add standard EEPROM 16-Kbit header metadata for automatic save
size detection on supporting emulators/loaders. See [validation and settings](emulator-compatibility.md).
Validated with 221 assertions on the exact v0.5 ROM across both tested emulator
configurations. Existing version tags and the v0.4.2 patch are preserved.

## v0.4.2 — Tree-tag fix

Fixed the inherited map-origin warp when tagging into a tree grab. Use one
native regrab-cooldown update after the model swap, preserving normal airborne
tagging and longer existing cooldowns. Validated with 723 focused assertions,
including Standard/Widescreen and Krusha ON/OFF. See [implementation notes](tree-tag-fix.md).

## v0.4.1 — Flashcart packaging preparation

Appended 7,904 zero bytes to v0.4, aligning the ROM to 16 KiB without changing
any existing bytes or runtime behavior. This prepares for loader transfer
requirements; original-console compatibility is still unverified.

## v0.4 — Exterior barrel portrait and startup lineup

Added the approved Krusha face between Chunky and DK on adventure tag barrels,
with a 15% larger shell and closely matched native portrait dimensions. Krusha
OFF retains the original barrel. Extended the startup head silhouettes with
Krusha, then adopted Arthan’s adjusted image without resampling its pixels.

## v3.1 — Consistent shout animation speed

Fixed occasional accelerated screams by resetting the inherited actor animation
rate and cancelling its pending speed blend. This follows v0.3 despite the tag’s
historical name.

## v0.3 — Widescreen HUD and presentation

Corrected horizontal scaling of HUD/menu sprites and pause inventory elements,
shifted the adventure HUD toward the screen edges, and corrected character
perspective during instruments and tag-barrel entry. Standard mode keeps its
existing presentation. A reported performance problem was resolved by restarting
the host computer; it did not require a ROM performance change.

## v0.2.1 — Larger Krusha

Enlarged Krusha by 10%, keeping adventure, barrel previews and shop visits
consistent while preserving native movement and doorway exits.

## v0.2 — Vocal instrument and cinematic presentation

Restored an instrument-equivalent attack using Krusha’s charged-attack burp clip.
Iterated the animation trim and speed, ending with its last four-fifths at 120%.
Replaced early layered audio experiments with the supplied TheScream3 recording
alone, in stereo at the maximum safe native level. Added darkening, spotlight,
centered zoom/orbit and camera shake. Added the Arthan startup credit.

## v0.1 — Sixth tag-barrel character

Added Krusha as a selectable sixth barrel slot with his own native victory and
waiting animations, native navigation and locked-Kong behavior. The persistent
ON/OFF setting also controls the barrel.

## v0.0 — Adventure foundation

Established a user-tested Krusha adventure build on Tag Anywhere: always-available
D-pad selection, safe camera/shop behavior, bananaports, boulder handling, native
bazooka and appropriate armed/unarmed models, barrel entry, and the saved option.
Krusha keeps his own identity and does not inherit another Kong’s collectibles.

The development process used local Mupen64Plus gameplay, controller-driven tests,
logged RAM fixtures to reach scenarios, fresh-ROM save states, and portable
native EEPROM saves. Partial decompilation and reverse-engineering references
helped identify the original engine paths. These checkpoints are emulator-tested;
physical console hardware was not available.
