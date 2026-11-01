#include "../include/common.h"

/* Krusha is character 5 / actor 7 throughout adventure mode. Compatibility
 * decisions belong to the individual interaction, never a global ID swap. */
extern u8 vanillaSetAction(s16 action, void* actor, u8 player);
extern u8 vanillaScriptCondition(u16* instruction, void* script, s16 object_id);
extern s32 vanillaModelPickupAllowed(s16 object_id, u8 player, u16 type);
extern void vanillaFindPurchase(void* menu, void* progress, s32 arg2);
extern s32 vanillaAmmoCollectible(s32 item, s32 type, u8 homing);
extern s32 nativeCrystalsUnlocked(void);
extern u8 vanillaCrystalAbility(s16 character);
extern s32 nativeScriptInteractionAllowed(void);
extern void vanillaBananaBalloon(void* sprite);
extern void vanillaBarrelEligibility(void);
extern void krushaBarrelInstall(void);
extern void krushaBarrelOption(void);
extern void krushaRoarInstall(void);
extern void krushaRoarTick(void);
extern u8 krushaRoarStart(void);
extern void krushaHolsterModel(void* actor);
extern void krushaDrawGunModel(void* actor);
extern s32 vanillaBuildActorBones(void* actor);
extern void vanillaDialogueLine(void* owner, u8* text, u16 length);

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

s32 krushaCrystalsUnlocked(void) {
    /* Shared native capacity prerequisite: any original Kong's crystal move,
     * or the camera/shockwave unlock. Krusha alone never grants that unlock. */
    return nativeCrystalsUnlocked();
}

u8 krushaCrystalAbility(s16 character) {
    /* Also drives native crystal opacity and pickup capability bits. The
     * global predicate checks only characters 0..4, so it cannot recurse into
     * this sixth-character branch. Original Kongs retain their own gates. */
    if (enabled && character == 5 && DetectAdventure()) return krushaCrystalsUnlocked();
    return vanillaCrystalAbility(character);
}

s32 krushaAmmoCollectible(s32 item, s32 type, u8 homing) {
    /* Classify at collection, not when a crate spills: this also handles
     * homing props left by an original Kong before tagging to Krusha. Native
     * stock updates, limits and HUD then all use the regular ammo counter. */
    if (enabled && Character == 5 && DetectAdventure()) {
        switch (type) {
            case 0x91: case 0x15D: case 0x15E: case 0x15F: case 0x160:
                homing = 0;
                break;
        }
    }
    return vanillaAmmoCollectible(item, type, homing);
}

void krushaBananaBalloon(void* sprite) {
    /* Krusha's bazooka is absent from native balloon collision lists. Also
     * reject a matching Kong's shot left in flight before tagging to Krusha:
     * native balloon rewards use the current character's banana counters. */
    u8* actor = *(u8**)0x807FBB40;
    volatile u8* hit = (volatile u8*)0x807FBD70;
    u32 type = actor ? *(u32*)(actor + 0x58) : 0;
    s32 block = enabled && Character == 5 && DetectAdventure() && *hit == 4 &&
        (type == 91 || type == 111 || type == 112 || type == 113 || type == 114);
    if (block) *hit = 0;
    vanillaBananaBalloon(sprite);
    if (block) *hit = 4;
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
    /* This predicate runs before collection/despawn. Let native eligibility
     * and stock updates handle shared supplies and battle crowns. Everything
     * tied to an original Kong's progression remains excluded. */
    if (enabled && player == 0 && Character == 5 && DetectAdventure()) {
        switch (type) {
            case 0x11:  /* homing crate -> regular bazooka ammo */
                return vanillaModelPickupAllowed(object_id, player, 0x8F);
            case 0x8E:  /* shared crystals, after their normal global unlock */
                if (!krushaCrystalsUnlocked()) return 0;
                break;
            case 0x48:  /* Nintendo Coin: global progression, not currency */
            case 0x56:  /* orange grenades: separate from bazooka ammunition */
            case 0x57:  /* watermelon health */
            case 0x8F:  /* ammo crate, which spills five native ammo props */
            case 0x91:  /* peanut */
            case 0x98:  /* camera film: preserve native camera-unlock check */
            case 0xEC:  /* temporary minecart/race DK coin */
            case 0x13C: /* boss key */
            case 0x15D: /* feather */
            case 0x15E: /* grape */
            case 0x15F: /* pineapple: also Krusha's native ammo pickup */
            case 0x160: /* coconut: all five refill shared weapon ammo */
            case 0x18D: /* battle crown */
            case 0x198: /* bean: shared quest flag, original GB owner stays */
            case 0x1B4: /* pearl: shared quest flag, original GB owner stays */
            case 0x28F: /* Rareware Coin */
                break;
            default:
                return 0;
        }
    }
    return vanillaModelPickupAllowed(object_id, player, type);
}

void krushaDialogueLine(void* owner, u8* text, u16 length) {
    u8 line[512];
    s32 out = 0, changed = 0;
    if (!enabled || Character != 5 || CurrentMap != 15 || !DetectAdventure()) {
        vanillaDialogueLine(owner, text, length);
        return;
    }
    /* Snide's dialogue calls the visitor KONG literally (not the ~ name
     * token). The native formatter consumes this line synchronously, wraps
     * words, and owns its glyph allocations; the source asset stays intact. */
    for (s32 i = 0; i < length; i++) {
        s32 word = i + 4 <= length && text[i] == 'K' && text[i+1] == 'O' &&
            text[i+2] == 'N' && text[i+3] == 'G' &&
            (i == 0 || text[i-1] < 'A' || text[i-1] > 'Z') &&
            (i+4 == length || text[i+4] < 'A' || text[i+4] > 'Z');
        s32 count = word ? 8 : 1;
        if (out + count >= sizeof(line)) {
            vanillaDialogueLine(owner, text, length);
            return;
        }
        if (word) {
            const char* name = "KREMLING";
            for (s32 j = 0; j < 8; j++) line[out++] = name[j];
            i += 3;
            changed = 1;
        } else line[out++] = text[i];
    }
    line[out] = 0;
    vanillaDialogueLine(owner, changed ? line : text, changed ? out : length);
}

static s32 krushaQuestTouch(ModelTwoData* object, void* script) {
    u8* data = script;
    /* These two unowned items use scripted mesh contact, unlike the ordinary
     * pickup list. Krusha's multiplayer skeleton has different contact points.
     * Keep native visibility/collision gates and interaction-state exclusions;
     * provide only a small body-touch volume, never the reward/flag itself. */
    if (!Player || !data[0x70] || data[0x60] || !nativeScriptInteractionAllowed()) return 0;
    f32* position = (f32*)object;
    f32 dx = position[0] - Player->xPos;
    f32 dy = position[1] - Player->yPos;
    f32 dz = position[2] - Player->zPos;
    if (dx*dx + dy*dy + dz*dz > 400.0f) return 0;
    if (object->object_type == 0x1B4) {
        /* The shell's physics normally supplies this restriction. Retain its
         * actual open phase rather than collecting through a closed clam. */
        /* Use the loaded/update list, not the camera's render list: a clam
         * must keep its timing even when it is outside the current view. */
        u32* actors = (u32*)0x807FB930;
        s32 count = *(u16*)0x807FBB34;
        if (count > 64) count = 64;
        for (s32 i = 0; i < count; i++) {
            actorData* clam = (actorData*)actors[i * 2];
            if (!clam || clam->actorType != 286) continue;
            dx = position[0] - clam->xPos;
            dy = position[1] - clam->yPos;
            dz = position[2] - clam->zPos;
            if (dx*dx + dy*dy + dz*dz < 10000.0f) return clam->control_state == 2;
        }
        return 0;
    }
    return 1;
}

u8 krushaScriptCondition(u16* instruction, void* script, s16 object_id) {
    s32 operation = instruction[0] & 0x7FFF;
    if (enabled && Character == 5 && DetectAdventure() &&
        (operation == 0x38 || (operation == 0x12 && instruction[1] == 6) ||
         (operation == 0x10 && instruction[1] == 1 && instruction[2] == 1))) {
        ModelTwoData* objects = ObjectModel2Pointer;
        for (s32 i = 0; i < ObjectModel2Count; i++) {
            /* Script handles use runtime_id (0x88), not setup ID (0x8A). */
            if (objects[i].runtime_id != object_id) continue;
            u16 type = objects[i].object_type;
            if (operation == 0x10 &&
                ((CurrentMap == 44 && type == 0x1B4) || (CurrentMap == 52 && type == 0x198))) {
                s32 touch = krushaQuestTouch(&objects[i], script);
                return (instruction[0] & 0x8000) ? !touch : touch;
            }
            if (operation == 0x38 && type >= 0x210 && type <= 0x214)
                return (instruction[0] & 0x8000) ? 0 : 1;
            if (operation == 0x12 && type == 0x1C6) {
                /* Crown pads enumerate the five actors' standing-on-pad
                 * tests. Extend only the Chunky branch to actor 7; native
                 * contact, subposition and button predicates still apply.
                 * Neither the player ID nor the original script is changed. */
                u16 extended[4] = {instruction[0], 7, instruction[2], instruction[3]};
                return vanillaScriptCondition(extended, script, object_id);
            }
            break;
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
        hook(0x806F544C, krushaAmmoCollectible);
        hook(0x806F6E58, krushaCrystalAbility);
        hook(0x806A7600, krushaBananaBalloon);
        hook(0x8070DED4, krushaDialogueLine);
        hook(0x8063EA14, krushaScriptCondition);
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
