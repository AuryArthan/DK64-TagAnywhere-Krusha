#include "../include/common.h"

extern void vanillaInstrumentInput(void);
extern void krushaNativeInstrumentControl(void);
extern s32 krushaInstrumentBlocked(void*);
extern s32 krushaInstrumentActorBlocked(void);
extern void krushaPlayActorAnimation(void*, s32);
extern void krushaPlayRawAnimation(void*, s16, f32, f32);
extern void krushaHolsterModel(void*);
extern void krushaChangeCollectable(s32, u8, s16);
extern void krushaShowHUD(s32, u8, s32);

/* Native vocal, lowered in pitch. Kept separate for later sample replacement
 * and for audibility testing with the actual N64 mixer. */
u32 krushaRoarSound = 0x276;
f32 krushaRoarPitch = 0.48f;
u32 krushaRoarCost = 150;

static u8* active_player;
static s32 active_map;
static u32 started;
static u32 ready_at;
static s32 cooldown_map = -1;

static u32 frame(void) { return *(u32*)0x8076A064; }

static s32 isKrusha(void) {
    return krushaEnabled() && DetectAdventure() && Character == 5 && Player;
}

u8 krushaRoarStart(void) {
    if (!isKrusha() || active_player || frame() < ready_at || CutsceneActive ||
        CurrentMap == 1 || CurrentMap == 5 || CurrentMap == 15 || CurrentMap == 25 ||
        Player->held_actor || Player->control_state == 0x67) return 0;
    if (CollectableBase.Crystals < krushaRoarCost) {
        playSound(0x98, 0x7FFF, 63.0f, 1.0f, 0, 0);
        return 0;
    }
    if (krushaRoarCost) {
        krushaChangeCollectable(5, 0, -(s16)krushaRoarCost);
        krushaShowHUD(5, 0, 0);
    }
    active_player = (u8*)Player;
    active_map = CurrentMap;
    started = frame();
    krushaHolsterModel(Player);
    krushaPlayActorAnimation(Player, 0); // Stop scripts, including gameplay effects.
    krushaPlayRawAnimation(Player, 0x2AA, 0.0f, 1.0f);
    Player->hSpeed = 0;
    active_player[0x144] = 1;
    Player->control_state = 0x67;
    Player->control_state_progress = 0;
    playSound(krushaRoarSound, 0x7FFF, 63.0f, krushaRoarPitch, 0xA, 0);
    return 1;
}

void krushaRoarInput(void) {
    if (!isKrusha() || *(void**)0x807FBB40 != Player) {
        vanillaInstrumentInput();
        return;
    }
    u8* data = *(u8**)((u8*)Player + 0x174);
    u8* changes = *(u8**)0x807FC924;
    /* Retain the native instrument's cutscene/platform/input restrictions.
     * Its five-Kong instrument energy and prop lookups are not entered. */
    if ((*(u16*)0x807FD63C & 8) && (*(u16*)0x807FD63A & 0x2000) && frame() >= 3 &&
        !(*(u32*)0x807FBB64 & 0x4000) && !(*(u32*)0x807FBB68 & 1) &&
        changes[0x2C0] != 2 && !data[0x245] &&
        !krushaInstrumentBlocked(Player) && !krushaInstrumentActorBlocked()) {
        krushaRoarStart();
    }
}

void krushaRoarControl(void) {
    u8* current = *(u8**)0x807FBB40;
    if (!isKrusha() || current != active_player) {
        krushaNativeInstrumentControl();
        return;
    }
    /* State 67 is the actual native instrument effect: enemy spawners apply
     * their normal instrument death, including immunity/range rules. Reuse
     * common rendering/input/chunk handling, without its five-Kong song case. */
    current[0x155] = 0;
    krushaNativeInstrumentControl();
    if (frame() - started >= 110) {
        *(s16*)(current + 0xE4) = 0;
        *(s16*)(current + 0xE8) = 0;
        *(u32*)(current + 0x60) &= ~1;
        unkSizeFunction(current); // Native return to appropriate ground/water state.
        active_player = 0;
        ready_at = frame() + 15;
    }
}

void krushaRoarTick(void) {
    if (CurrentMap != cooldown_map) {
        cooldown_map = CurrentMap;
        ready_at = 0;
    }
    if (active_player && (Player != (void*)active_player || CurrentMap != active_map ||
                          Character != 5 || active_player[0x154] != 0x67)) {
        active_player = 0;
        ready_at = 0;
    }
}

void krushaRoarInstall(void) {
    *(u32*)0x806E52D0 = 0x08000000 | (((u32)krushaRoarInput & 0x0FFFFFFF) >> 2);
    *(u32*)0x806E52D4 = 0;
    osWritebackDCache((void*)0x806E52D0, 8);
    osInvalICache((void*)0x806E52D0, 8);
    *(void**)0x80750E88 = krushaRoarControl;
}
