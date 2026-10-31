# Decisions, failed ideas and debugging traps

## Preserve these boundaries

The user values playable results and actual emulator testing, not just successful
compilation. Keep the original ROM unchanged, preserve release checkpoints and
user saves, and avoid unrelated changes. The user prefers routine authorized
work to continue without repeated permission questions. This does not authorize
a future GitHub push or external publication; that was described as later work.

Do not install global packages unnecessarily: pinned local tool/emulator copies
already work. Do not assume a new machine grants X sockets or `/proc` access;
request the applicable execution permission if blocked and explain the concrete
need. A restricted-sandbox error is not evidence of a game crash.

## Game-engine experiments already resolved

- Global Chunky identity spoofing at bananaports inherited Chunky's collectibles;
  use the interaction-specific script condition instead.
- Native Krusha instrument/camera/shop paths index five-Kong assumptions. Keep
  the dedicated guards, native camera routing, empty shop stock and custom roar.
- A visible bazooka is not proof it is equipped. Check gun flag, mesh and native
  projectile/ammo use. Selection and camera exit must leave the appropriate model.
- Barrel Chunky-like animation was rejected. Krusha now uses his own native
  waiting/victory material. Preserve six-slot navigation and locked question marks.
- Enlarging the root persistently disrupted movement/shop exits. Current scaling
  is limited to building skeleton matrices, with root restoration.
- Shout history contains many trims/gains/orbits. Final accepted state is in live
  source and CURRENT_STATE, not the first revision in a long technical note.
- The 5×-speed shout came from inherited actor animation speed/blend. Reset both;
  changing only the clip's nominal speed was insufficient.
- Instrument darkening/spotlight hides normal native enemy staging artifacts.
  The camera must track the animated mesh, not merely the player root.
- Tree-tag deferred-dispatch prototypes failed: one frame guard suppressed all
  normal tags; allowing a frame delta still warped at several timings. Final
  native regrab cooldown fixes the unsafe transform-read interval. Failed patches
  and traces remain in tree-tag-fix-review; do not apply them.

## Harness failures, not ROM bugs

- **Wrong decimal state:** vine 0x57 is 87 decimal. An assertion against decimal
  57 failed after a perfectly valid grab. Fixed without changing the ROM.
- **Vine jump-off:** holding A through a fixture approach can grab and immediately
  leap off; seeing leaving-vine state does not mean attachment failed.
- **Barrel entry:** one Diddy jump from z=2320 missed and left him standing under
  the idle barrel. The repeated-selection fixture starts 10 units closer and logs
  bounded retries. Do not silently count a miss as success or patch mechanics to
  satisfy a brittle input script.
- **Title menu readiness:** map 80 exists before the carousel is interactive.
  A fixed delay missed Left; later A opened Adventure instead of Options. The
  matrix now waits for page 1 and native ready byte 800337F0, confirms selection
  4 (Other Options), then enters page 9. Check the map before reusing menu pointers.
- **Persisted options:** after a cold restart, explicitly choose the requested
  widescreen state. Do not blindly toggle an already-OFF Krusha setting ON.
- **Isles doorway:** north from the load spawn (about 2792,500,2136) enters the
  real Training Grounds door. A map-soak fixture must move off it before redirecting
  another loading zone. Safe open-ground fixture: (2940,500,2220).
- **New game route:** the opening story returns control in Treehouse map 171;
  use its ordinary exit to Training Grounds 176. It does not teleport straight
  to the latter. An intro deadline/route error was not a game softlock.
- **Audio matching:** correlation over repeated performances chose L and R from
  different repetitions. Isolate one performance; the accepted stereo test aligned
  both at sample 8893. Validate actual native mix/voice cleanup, not only a WAV file.

## Environment / evidence traps

OSD enabled caused emulator pause segfaults in the initial setup; keep `--noosd`.
A reported broad slowdown also affected old ROMs and disappeared after a host
restart; the user confirmed it was not the hack. Stop test emulators/X servers
cleanly so they do not leave background load.

Use sequential emulator runs by default. Concurrent software rendering made
wall-time inputs less reliable; different displays/profiles prevent collisions
but do not guarantee full-speed timing. Prefer frame advance or native ready
conditions for boundary tests. A passing GUI screenshot alone is not a RAM/state
assertion, and a fixture failure alone is not a game defect.

Never load an old-ROM save state to validate a new hack: it restores old code,
pointers and allocation state. Native EEPROM is the portable progress format;
copy it into a new profile under the ROM's correct filename, preserving originals.
Reports need the ROM hash actually executed. Many test scripts catch exceptions
and still exit zero; inspect JSON `complete`, every `passed`, and `error`.

Several historical suites/packagers hardcode output under named old reviews and
may overwrite them even if DK64_RUNTIME is set. Read a script first, redirect or
adapt paths to a new scratch run, and preserve old evidence. Do not rerun a giant
historical pipeline merely to orient yourself.
