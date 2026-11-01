#include "../include/common.h"

/* Keep the native 0x40-byte barrel data layout. Its five actor pointers are
 * followed immediately by the spotlight pointer; the sixth actor lives here,
 * rather than overwriting that pointer or any of the cutscene data. Only one
 * adventure barrel selector can be open at a time. */
typedef struct {
    void* player;
    u16 timer;
    s8 selected;
    s8 previous;
    void* actors[5];
    void* spotlight;
    s8 direction;
} BarrelData;

typedef struct { s16 model, actor; u8 mesh, pad; } BarrelCharacter;
static const BarrelCharacter characters[6] = {
    {4, 2, 2, 0}, {1, 3, 1, 0}, {6, 4, 3, 0},
    {9, 5, 4, 0}, {12, 6, 0, 0}, {0xDB, 7, 0, 0},
};
/* Preserve the five native instrument masks. Krusha has no sixth stem. */
static const u32 music_masks[6] = {2, 0x48, 4, 0x20, 0x10, 0};
static BarrelData* owner;
static void* sixth;

extern void vanillaBarrelSpawn(BarrelData*);
extern void vanillaBarrelLayout(BarrelData*);
extern void vanillaBarrelControl(BarrelData*);
extern char* vanillaBarrelName(BarrelData*, s32);
extern void vanillaBarrelAnimation(void*, void*, s32);
extern void krushaPlayActorAnimation(void*, s32);
extern s32 krushaNativeBarrelFlag(s32, s32);
extern void krushaInitCharacterMesh(void*, u16);
extern void krushaNativeActorDelete(void*);
extern f32 krushaSin(s16);
extern f32 krushaCos(s16);
extern void* vanillaBarrelFile(s32 table, s32 index, u8 synchronous, u8 unique);

/* Table 27 is a dedicated uncompressed asset table. Native file allocation,
 * DMA, ownership and cleanup still handle every file. The original table-5
 * barrel and all five original faces remain byte-for-byte available when OFF.
 * Reserved texture IDs belong to the six-face barrel and gray shockwave. */
void* krushaBarrelFile(s32 table, s32 index, u8 synchronous, u8 unique) {
    if (table == 5 && index == 0xC0 && krushaEnabled()) {
        table = 27;
        index = 0;
    } else if (table == 25 && (index == 7001 || index == 7002)) {
        table = 27;
        index -= 7000;
    } else if (table == 5 && index == 0xEC) {
        table = 27;
        index = 3;
    } else if (table == 25 && index >= 7003 && index <= 7008) {
        table = 27;
        index -= 6999;
    }
    return vanillaBarrelFile(table, index, synchronous, unique);
}

static void patch(u32 address, u32 word) {
    *(volatile u32*)address = word;
    osWritebackDCache((void*)address, 4);
    osInvalICache((void*)address, 4);
}

static void jump(u32 address, void* target) {
    patch(address, 0x08000000 | (((u32)target & 0x0FFFFFFF) >> 2));
    patch(address + 4, 0);
}

static void pointer(u32 hi, u32 lo, const void* target) {
    u32 address = (u32)target;
    patch(hi, (*(u32*)hi & 0xFFFF0000) | ((address + 0x8000) >> 16));
    patch(lo, (*(u32*)lo & 0xFFFF0000) | (address & 0xFFFF));
}

static void* actor(BarrelData* data, s32 index) {
    if (index == 5) return data == owner ? sixth : 0;
    return data->actors[index];
}

s32 krushaBarrelFlag(s32 type, s32 index) {
    /* Native entry records a tag flag. There is no sixth flag to write. */
    return index == 5 ? -1 : krushaNativeBarrelFlag(type, index);
}

void krushaBarrelAnimation(void* model, void* data, s32 action) {
    if (krushaEnabled() && DetectAdventure() &&
        *(u32*)((u8*)model + 0x58) == 316 && *(u16*)data == 7) {
        if (action == 0x8B) {
            // Native multiplayer victory: Krusha's own clip 693. The original
            // barrel entry 1DD uses Chunky's clip 2EB and Chunky's voice cues.
            krushaPlayActorAnimation(model, 0x43A);
            return;
        }
        if (action == 0x8A || action == 0x8C) {
            // His own waiting pose also replaces Chunky's deselection clip.
            krushaPlayActorAnimation(model, 0x1DC);
            return;
        }
    }
    vanillaBarrelAnimation(model, data, action);
}

void krushaBarrelLayout(BarrelData* data) {
    if (!krushaEnabled() || !DetectAdventure()) {
        vanillaBarrelLayout(data);
        return;
    }
    u8* barrel = *(u8**)0x807FBB40;
    f32 amount = data->timer / 20.0f;
    f32 step = 4096.0f / 6.0f;
    f32 base = *(s16*)(barrel + 0xE6) + data->selected * step - amount * step * data->direction;
    for (s32 i = 0; i < 6; i++) {
        u8* model = actor(data, i);
        if (!model) continue;
        s16 angle = ((s32)(base - i * step)) & 0xFFF;
        *(f32*)(model + 0x7C) = *(f32*)(barrel + 0x7C) + krushaSin(angle) * 45.0f;
        *(f32*)(model + 0x80) = *(f32*)(barrel + 0x80) - 10.0f;
        *(f32*)(model + 0x84) = *(f32*)(barrel + 0x84) + krushaCos(angle) * 45.0f;
        f32 focus = i == data->selected ? 1.0f - amount : i == data->previous ? amount : 0.0f;
        focus = (focus - 0.6f) * 2.5f;
        if (focus < 0) focus = 0;
        if (focus > 1) focus = 1;
        model[0x15F] = 3 + 12.0f * focus;
    }
}

void krushaBarrelSpawn(BarrelData* data) {
    owner = data;
    sixth = 0;
    vanillaBarrelSpawn(data);
    if (!krushaEnabled() || !DetectAdventure()) return;
    if (!spawnActor(316, 0xDB)) return;
    u8* model = *(u8**)0x807FBB44;
    sixth = model;
    *(s16*)(model + 0xE6) = *(s16*)(*(u8**)0x807FBB40 + 0xE6);
    *(u32*)(model + 0x60) |= 0x40000000;
    void* data_model = *(void**)(model + 0x174);
    *(u16*)data_model = 7;
    krushaInitCharacterMesh(model, 7);
    krushaBarrelAnimation(model, data_model, data->selected == 5 ? 0x8B : 0x8A);
    krushaBarrelLayout(data);
}

void krushaBarrelControl(BarrelData* data) {
    if (!krushaEnabled() || !DetectAdventure() || data != owner || !sixth) {
        vanillaBarrelControl(data);
        return;
    }
    /* Native control indexes actors[selected]. During this synchronous call,
     * slot five aliases the saved spotlight field. Layout and name rendering
     * use actor() instead. Restore the real spotlight before actor rendering.
     * On exit native cleanup deletes the aliased sixth actor and the original
     * five; delete the real spotlight once here. No allocation layout changes. */
    void* spotlight = data->spotlight;
    data->spotlight = sixth;
    vanillaBarrelControl(data);
    if ((*(u8**)0x807FBB40)[0x154] == 1) {
        data->spotlight = spotlight;
    } else {
        krushaNativeActorDelete(spotlight);
        data->spotlight = 0;
        sixth = 0;
        owner = 0;
    }
}

char* krushaBarrelName(BarrelData* data, s32 index) {
    if (index == 5 && data == owner && sixth) return "KRUSHA";
    return vanillaBarrelName(data, index);
}

void krushaBarrelInstall(void) {
    jump(0x8066B0F8, krushaBarrelFile);
    jump(0x80682E38, krushaBarrelSpawn);
    jump(0x80682AB4, krushaBarrelLayout);
    jump(0x806836D0, krushaBarrelControl);
    jump(0x80683A80, krushaBarrelName);
    jump(0x80682DF4, krushaBarrelAnimation);
    pointer(0x80683584, 0x8068358C, characters);
    pointer(0x806839C4, 0x806839E4, (u8*)characters + 2);
    pointer(0x806835EC, 0x806835FC, music_masks);
    pointer(0x80683844, 0x80683848, music_masks);
    patch(0x80683620, 0x0C000000 | (((u32)krushaBarrelFlag & 0x0FFFFFFF) >> 2));
}

void krushaBarrelOption(void) {
    static s32 previous = -1;
    s32 count = krushaEnabled() && DetectAdventure() ? 6 : 5;
    if (count == previous) return;
    patch(0x806837D4, 0x240C0000 | (count - 1));
    patch(0x806837EC, 0x28410000 | count);
    previous = count;
}
