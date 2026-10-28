#include "../include/common.h"

extern void vanillaInstrumentInput(void);
extern void krushaNativeInstrumentControl(void);
extern s32 krushaInstrumentBlocked(void*);
extern s32 krushaInstrumentActorBlocked(void);
extern void krushaPlayActorAnimation(void*, s32);
extern void krushaPlayRawAnimation(void*, s16, f32, f32);
extern void krushaAnimationSpeed(void*, f32, f32);
extern void krushaHolsterModel(void*);
extern void krushaChangeCollectable(s32, u8, s16);
extern void krushaShowHUD(s32, u8, s32);
extern void krushaPlayScream(void);
extern void krushaRoarStageBegin(void*);
extern void krushaRoarStageTick(u32);
extern void krushaRoarStageEnd(void);
extern void krushaRoarBuildCameraMatrices(void*);

u32 krushaRoarCost = 150;

#define ROAR_START_FRAME (110.0f / 5.0f)
#define ROAR_SPEED 1.2f
#define ROAR_MAX_DURATION 240 // Failsafe; normal completion follows the clip.
#define INSTRUMENT_SCENE_MASK 0x10030
#define INSTRUMENT_PERFORMER 0x40000000

static u8* active_player;
static s32 active_map;
static u32 started;
static u32 ready_at;
static s32 cooldown_map = -1;
static u32 saved_scene_bits;
static u32 saved_performer_bit;

static void holdBackdrop(void) {
    /* Native instrument animation command 80618E4C: hide scenery, props and
     * ordinary actors while allowing the performing actor to remain visible. */
    *(u32*)0x807FBB60 &= ~INSTRUMENT_SCENE_MASK;
    *(u32*)(active_player + 0x60) |= INSTRUMENT_PERFORMER;
}

static void restoreBackdrop(void) {
    /* A map load initializes its own render flags and frees the previous actor.
     * Never restore the old map's state over that new scene or touch its actor. */
    if (CurrentMap == active_map) {
        u32* scene = (u32*)0x807FBB60;
        *scene = (*scene & ~INSTRUMENT_SCENE_MASK) | saved_scene_bits;
        if ((void*)active_player == Player) {
            u32* props = (u32*)(active_player + 0x60);
            *props = (*props & ~INSTRUMENT_PERFORMER) | saved_performer_bit;
        }
    }
}

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
    saved_scene_bits = *(u32*)0x807FBB60 & INSTRUMENT_SCENE_MASK;
    saved_performer_bit = *(u32*)(active_player + 0x60) & INSTRUMENT_PERFORMER;
    holdBackdrop();
    krushaHolsterModel(Player);
    krushaPlayActorAnimation(Player, 0); // Stop scripts, including gameplay effects.
    krushaPlayRawAnimation(Player, 0x2AA, ROAR_START_FRAME, 0.0f);
    krushaAnimationSpeed(Player, ROAR_SPEED, 0.0f);
    u8* animation = *(u8**)((u8*)Player + 4);
    u8* channel = *(u8**)animation;
    *(f32*)(channel + 0x14) = ROAR_START_FRAME; // Never wrap into the cut wind-up.
    Player->hSpeed = 0;
    active_player[0x144] = 1;
    Player->control_state = 0x67;
    Player->control_state_progress = 0;
    krushaRoarStageBegin(Player);
    krushaPlayScream(); // Only the supplied recording, at original pitch.
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
    holdBackdrop();
    krushaNativeInstrumentControl();
    u32 elapsed = frame() - started;
    krushaRoarStageTick(elapsed);
    u8* animation = *(u8**)(current + 4);
    u8* channel = *(u8**)animation;
    if (*(f32*)(channel + 4) >= *(f32*)(channel + 0x18) ||
        elapsed >= ROAR_MAX_DURATION) {
        *(s16*)(current + 0xE4) = 0;
        *(s16*)(current + 0xE8) = 0;
        *(u32*)(current + 0x60) &= ~1;
        krushaRoarStageEnd();
        restoreBackdrop();
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
        krushaRoarStageEnd();
        restoreBackdrop();
        active_player = 0;
        ready_at = 0;
    } else if (active_player) {
        holdBackdrop();
        krushaRoarStageTick(frame() - started);
    }
}

void krushaRoarInstall(void) {
    *(u32*)0x805FCA94 = 0x08000000 | (((u32)krushaRoarBuildCameraMatrices & 0x0FFFFFFF) >> 2);
    *(u32*)0x805FCA98 = 0;
    osWritebackDCache((void*)0x805FCA94, 8);
    osInvalICache((void*)0x805FCA94, 8);
    *(u32*)0x806E52D0 = 0x08000000 | (((u32)krushaRoarInput & 0x0FFFFFFF) >> 2);
    *(u32*)0x806E52D4 = 0;
    osWritebackDCache((void*)0x806E52D0, 8);
    osInvalICache((void*)0x806E52D0, 8);
    *(void**)0x80750E88 = krushaRoarControl;
}
