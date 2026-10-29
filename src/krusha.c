#include "../include/common.h"

/* Krusha is character 5 / actor 7 throughout adventure mode. Compatibility
 * decisions belong to the individual interaction, never a global ID swap. */
extern u8 vanillaSetAction(s16 action, void* actor, u8 player);
extern u8 vanillaScriptCondition(u16* instruction, void* script, s16 object_id);
extern s32 vanillaModelPickupAllowed(s16 object_id, u8 player, u16 type);
extern void vanillaFindPurchase(void* menu, void* progress, s32 arg2);
extern void vanillaFairyActor(void);
extern void vanillaBarrelEligibility(void);
extern void krushaBarrelInstall(void);
extern void krushaBarrelOption(void);
extern void krushaRoarInstall(void);
extern void krushaRoarTick(void);
extern u8 krushaRoarStart(void);
extern void krushaHolsterModel(void* actor);
extern void krushaDrawGunModel(void* actor);
extern s32 vanillaBuildActorBones(void* actor);

/* Enlarge the skeleton while its world matrices are built. Restore the root
 * transform before native movement uses it, so the visible increase cannot
 * change locomotion or stall the automatic walk out of a doorway. */
s32 krushaBuildActorBones(void* actor_ptr) {
    u8* actor = actor_ptr;
    u32 type = *(u32*)(actor + 0x58);
    s32 enlarge = (type == 7 && actor_ptr == Player) ||
        (type == 316 && *(u16*)*(u8**)(actor + 0x174) == 7);
    if (!enlarge || !krushaEnabled() || !DetectAdventure()) {
        return vanillaBuildActorBones(actor_ptr);
    }
    f32* matrix = (f32*)(actor + 0xC);
    f32 saved[3][3];
    for (s32 i = 0; i < 3; i++) for (s32 j = 0; j < 3; j++) {
        saved[i][j] = matrix[i * 4 + j];
        matrix[i * 4 + j] *= 1.1f;
    }
    s32 result = vanillaBuildActorBones(actor_ptr);
    for (s32 i = 0; i < 3; i++) for (s32 j = 0; j < 3; j++) {
        matrix[i * 4 + j] = saved[i][j];
    }
    return result;
}

/* Global flag 0x24 is unused by the original game. Store the DISABLED state so
 * existing saves default to Krusha on without an extra initialization flag. */
static s32 option_loaded = 0;
static s32 enabled = 1;

s32 krushaEnabled(void) { return enabled; }

void krushaSetEnabled(s32 value) {
    enabled = value != 0;
    setFlag(0x24, !enabled, 1);
    SaveToGlobal();
}

void krushaBarrelEligibility(void) {
    u8* barrel = *(u8**)0x807FBB40;
    if (enabled && DetectAdventure() && Character == 5 && Player &&
        barrel && (*(u32*)(barrel + 0x58) == 98 ||
                   *(u32*)(barrel + 0x58) == 136 || *(u32*)(barrel + 0x58) == 137)) {
        u8* data = *(u8**)((u8*)Player + 0x174);
        u8* changes = *(u8**)0x807FC924;
        if (changes[0x2C0] == 1 && !(*(u32*)(data + 0x1F4) & 0x40) &&
            !(*(u32*)(data + 0x1F0) & 0x40)) {
            *(u32*)(barrel + 0x60) |= 0x8000;
            *(u16*)(barrel + 0x132) = data[0xCA] ? 4 : 1;
            return;
        }
    }
    vanillaBarrelEligibility();
}

void krushaFairyActor(void) {
    if (enabled && Character == 5 && DetectAdventure() && Player) {
        u8* data = *(u8**)((u8*)Player + 0x174);
        /* The camera still takes photographs. Treat a fairy photo as a miss
         * before its actor awards a permanent flag or disappears. */
        if ((*(u32*)(data + 0x1F0) & 0x8000) && data[0x1EC] == 1) {
            data[0x1EC] = 2;
        }
    }
    vanillaFairyActor();
}

void krushaFindPurchase(void* menu, void* progress, s32 arg2) {
    if (enabled && Character == 5 && DetectAdventure()) {
        /* Shop stock is [5][7]. Index 5 reads the next shop's stock table.
         * Use the ordinary 'nothing for sale' conversation instead. */
        u8* data = menu;
        *(s16*)(data + 4) = 0;
        data[0xB] = 0xFF;
        data[0x10] = CollectableBase.Melons;
        *(s16*)0x80750AC8 = 0;
        return;
    }
    vanillaFindPurchase(menu, progress, arg2);
}

static void hook(u32 address, void* target) {
    volatile u32* code = (volatile u32*)address;
    code[0] = 0x08000000 | (((u32)target & 0x0FFFFFFF) >> 2);
    code[1] = 0;
    osWritebackDCache((void*)address, 8);
    osInvalICache((void*)address, 8);
}

u8 krushaSetAction(s16 action, void* actor, u8 player) {
    /* Route the sixth character around the undefined native instrument
     * cutscene. Input and script requests use the same safe roar initializer. */
    if (enabled && player == 0 && Character == 5 && action == 0x53 && DetectAdventure()) return krushaRoarStart();
    return vanillaSetAction(action, actor, player);
}

s32 krushaModelPickupAllowed(s16 object_id, u8 player, u16 type) {
    /* This predicate runs BEFORE the prop is marked collected/despawned. It
     * covers colored pickups and shared consumables without changing flags. */
    if (enabled && player == 0 && Character == 5 && DetectAdventure()) return 0;
    return vanillaModelPickupAllowed(object_id, player, type);
}

u8 krushaScriptCondition(u16* instruction, void* script, s16 object_id) {
    if (enabled && Character == 5 && (instruction[0] & 0x7FFF) == 0x38 && DetectAdventure()) {
        ModelTwoData* objects = ObjectModel2Pointer;
        for (s32 i = 0; i < ObjectModel2Count; i++) {
            /* 0x210..0x214: the five numbered adventure bananaport pads. */
            // Scripts use the runtime handle at 0x88, not setup ID 0x8A.
            if (objects[i].runtime_id == object_id &&
                objects[i].object_type >= 0x210 && objects[i].object_type <= 0x214) {
                return (instruction[0] & 0x8000) ? 0 : 1;
            }
        }
    }
    return vanillaScriptCondition(instruction, script, object_id);
}

/* Actor 61's collision dispatch list. Duplicate only its Chunky branch for
 * actor 7; preserve the default and projectile branches and all native pickup,
 * carry, throw and drop handling. No other heavy-object checks are changed. */
static const u32 boulder_collisions[] = {
    0x00060000, 0x8074AFDC,
    0x00070000, 0x8074AFDC,
    0xFFFF0000, 0x8074B000,
    0xFFFD0000, 0x8074AC28,
    0, 0,
};

void krushaAdventure(void) {
    static s32 installed = 0;
    static s32 last_character = -1;
    static void* last_player = 0;
    static void* last_model = 0;
    if (!installed) {
        hook(0x80614A64, krushaBuildActorBones);
        hook(0x806EB0C0, krushaSetAction);
        hook(0x806F6644, krushaModelPickupAllowed);
        hook(0x8063EA14, krushaScriptCondition);
        hook(0x806C5C20, krushaFairyActor);
        hook(0x80680774, krushaBarrelEligibility);
        krushaBarrelInstall();
        krushaRoarInstall();
        installed = 1;
    }
    if (CurrentMap == 80 && !option_loaded) {
        enabled = !checkFlag(0x24, 1);
        option_loaded = 1;
    }
    krushaBarrelOption();
    krushaRoarTick();
    *(const u32**)0x8074C7EC = enabled ? boulder_collisions : (const u32*)0x8074B00C;
    /* The roar uses shared crystals, not a borrowed Kong's instrument stock.
     * Keep the nonexistent instrument prop/stock paths disabled. */
    if (enabled && DetectAdventure()) {
        // The native bazooka uses shared standard ammo and actor-7 projectiles.
        MovesBase[5].weapon_bitfield |= 1;
        MovesBase[5].ammo_belt = MovesBase[0].ammo_belt;
        MovesBase[5].instrument_bitfield = 0;
        MovesBase[5].instrument_energy = 0;
        if (Character == 5 && Player && *(void**)Player) {
            void* model = *(void**)Player;
            if (last_character != 5 || last_player != Player || last_model != model) {
                u8* data = *(u8**)((u8*)Player + 0x174);
                if (data[0x8C]) krushaDrawGunModel(Player);
                else krushaHolsterModel(Player);
            }
            last_model = model;
        }
    }
    last_character = Character;
    last_player = Player;
}
