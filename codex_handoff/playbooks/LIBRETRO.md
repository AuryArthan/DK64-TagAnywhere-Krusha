# Playbook: Mupen64Plus-Next regression testing

Use `tools/README.md` and `docs/emulator-compatibility.md` for installation,
commands, final ROM hash, current supported settings and exact test evidence.
This playbook records setup pitfalls found during the Batocera report.

Color-effect tests (2026-11-01): frontend frame advance takes two VI steps per
native DK64 update in this core. Bound transient-effect checks by native game
time or allow enough frontend steps; the standalone step count can expire
before an otherwise correct ring disappears. `krusha-colors-test.py` accounts
for this. A screenshot/partial test showing the correct ring is not a completed
cleanup regression.

- The local frontend is RetroArch1.18.0 with a SHA-pinned Linuxx86-64 official
  Mupen64Plus-Next core. A tiny linked proxy supplies only the libretro input
  callback; it does not emulate or patch the game. Its dependency path is local,
  so rerun setup to compile the proxy when moving the cache.
- Controller keys match the standalone test helper. Synthetic frontend keyboard
  input was unreliable after the GL context was recreated. The proxy avoids
  that problem; frontend hotkeys use RetroArch's localUDP55357 command interface.
  Do not run two such controllers on the same port, X display or profile.
- `control-libretro.py` pins the real core's ELF SHA before using its RDRAM pointer
  lookup at loadbase+0xA25ED48. Upgrading a core requires revalidating that lookup.
  The nightly URL moves: checksum rejection is deliberate, not a reason to skip
  verification. Core metadata `.info` is local; `core_info_savestate_bypass=true`
  ensures the test frontend exposes the core's exported serialization support.
- Keep XDG configuration/data/cache, save/state paths and core options under
  the selected profile. Disable RetroArch's sorting into core subdirectories.
  The window can be recreated at1280x720 on a640x480 Xvfb display; the controller
  explicitly resizes/focuses it before capturing. Early cropped black captures
  during setup were not game bugs.
- Native libretro save memory is0x48800 bytes: EEPROM first0x800, then mempaks,
  SRAM and FlashRAM. Copy only from an explicit private EEPROM fixture, into
  a new test profile. Never alter the player's save or ship it in Git.
- Modified ROMs absent from the core database default to4-Kbit EEPROM. The
  development build's `ED` header + save-type nibble2 selects16-Kbit EEPROM.
  Verify startup log `Save type: 1`. This fixed missing native Speed Mode data;
  don't compensate by writing unlocks/options into RAM for a persistence test.
- For menu QA, allow the native title carousel animation to settle. After map34
  loads, the automatic entry walk starts after the first apparently-idle frame.
  Wait past150 native frames and for idle12 before fixture positioning/tagging.
  A photo's native shutter cooldown can consume an early C-Up exit; use bounded
  native-input retries, not an action-state write or a game timing patch.
- Snide's textbox actor is299. Actor335 is his menu,173 is a cutscene controller.
  The glyph linked lists live at textbox PaaD+C -> line+C -> glyph; each glyph's
  char is+12 and next is+A0, line next is+1C. Pause the emulator while traversing
  them, and unpause in a finally block. Native text wrapping can then be asserted
  directly as well as inspected visually.
- Test crown entry by standing on the real pad and pressingZ; no identity writes.
  Its scripts enumerate actors2..6 with condition12. The patch extends the
  actor6 branch only on pad model2 type1C6, through a copied actor7 instruction.
  Japes crown is permanent flag261; use the normal arena timer, punches/jumps,
  reward/return and celebration. Idle waiting while doing manual tooling can
  lose the battle; that is not proof of a game bug. Crowns use ordinary arena
  restrictions on instrument input, so don't rely on repeated shouts to win.

Use a fresh explicit DK64_RUNTIME for a different ROM hash. The graphics helper
creates exact-ROM slots0..2, then its interactions phase reuses that same profile.
The resume guard checks the prior report hash; don't transplant old states or
replace their report with a new hash. Native EEPROM/save persistence is a separate
cold-boot test and uses no savestates. Require complete:true, matching ROM hash
and every assertion passing; also inspect the mask/tint screenshots.

Current original-machine cache: repository runtime/libretro-investigation.
The standalone emulator/Xvfb cache remains in the parent workspace tools/;
set DK64_TOOL_ROOT to that cache here. A fresh clone uses its own repo tools/.
These paths are observations, not instructions to reuse old test profiles.
