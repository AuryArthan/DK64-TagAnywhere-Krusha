#include "../include/common.h"

extern void widescreenNativeOrtho(Mtx*, f32, f32, f32, f32, f32, f32, f32);
extern void widescreenNativeSpriteRect(Gfx**, s16, s16);
extern Gfx* widescreenNativeCameraMask(Gfx*);
extern Gfx* widescreenNativeSniperMask(Gfx*, void*);
extern Gfx* widescreenNativeShutterMask(Gfx*, void*);
extern Gfx* widescreenNativeLogo(Gfx*);
extern void widescreenNativeQueue(void*, void*, u8);
extern Gfx* widescreenNativeCounter(Gfx*, s16, s16, s16*, s16, u8*);
extern Gfx* widescreenNativeText(Gfx*, u8, s16, s16, char*);
extern void widescreenNativePerspective(Mtx*, u16*, f32, f32, f32, f32, f32);
extern Gfx* widescreenNativeHUDCounter(s32, void*, Gfx*);
extern Gfx* widescreenNativeHUDGroup(s32, void*, Gfx*);
extern void widescreenNativeHUDIcon(void*, s32);
extern Gfx* widescreenNativeHealth(Gfx*, void*, void*, void*);
extern s32 widescreenProject(f32, f32, f32, f32*, f32*, s32, f32, s32);
extern Gfx* widescreenImage(Gfx*, u16, s32, s32, s32, s32, s16, s16, f32, f32, s32, f32);
extern Gfx* widescreenAnimatedText(Gfx*, s16, s32, f32, f32, f32, f32);
static s32 rect_scope;

/* 4:3 framebuffer displayed at 16:9: x must be 3/4 of its old width.
 * Keep screen-space groups together around the original screen centre. World
 * sprites use the perspective projection and never pass through this path. */
static s32 active(void) { return *(volatile u8*)0x807444C0 != 0; }

enum { HUD_EDGE_X = 32, HUD_EDGE_Y = 6 };

void widescreenPerspective(Mtx* matrix, u16* norm, f32 fov, f32 aspect,
                          f32 near, f32 far, f32 scale) {
    /* Native cutscenes remove widescreen correction. Keep the full 16:9
     * factor throughout instruments and tag-barrel entry/selection/exit,
     * including the entry cutscene and its gradual aspect restoration. */
    if (active() && DetectAdventure() && Player &&
        *(u8*)0x807FC928 == 1 &&
        (((u8*)Player)[0x154] == 103 || ((u8*)Player)[0x154] == 66)) {
        f32 native_scale = *(f32*)0x80747CD0;
        if (native_scale > 0.5f && native_scale < 2.0f)
            aspect *= (4.0f / 3.0f) / native_scale;
    }
    widescreenNativePerspective(matrix, norm, fov, aspect, near, far, scale);
}

static s32 hudOffsets(s32 item, f32* x, f32* y) {
    if (!active() || !DetectAdventure() || *(u8*)0x807FC928 != 1 ||
        item < 0 || item >= 15 || !HUD) return 0;
    *x = HUD[item].screen_x <= 80 ? -HUD_EDGE_X :
        (HUD[item].screen_x >= 240 ? HUD_EDGE_X : 0);
    *y = HUD[item].screen_y < 100 ? -HUD_EDGE_Y :
        (HUD[item].screen_y >= 180 ? HUD_EDGE_Y : 0);
    return 1;
}

static s32 hud_group_scope;

Gfx* widescreenHUDCounter(s32 item, void* counter, Gfx* dl) {
    f32 x, y;
    if (hud_group_scope || !hudOffsets(item, &x, &y))
        return widescreenNativeHUDCounter(item, counter, dl);
    s32* position = *(s32**)((u8*)counter + 0x14);
    s32 saved_x = position[0], saved_y = position[1];
    position[0] += (s32)x; position[1] += (s32)y;
    dl = widescreenNativeHUDCounter(item, counter, dl);
    position[0] = saved_x; position[1] = saved_y;
    return dl;
}

Gfx* widescreenHUDGroup(s32 item, void* counter, Gfx* dl) {
    f32 x, y;
    if (!hudOffsets(item, &x, &y))
        return widescreenNativeHUDGroup(item, counter, dl);
    /* This renderer derives all five GB icons from the same counter origin.
     * Shift the group once so its numbers and icons stay together. */
    s32* position = *(s32**)((u8*)counter + 0x14);
    s32 saved_x = position[0], saved_y = position[1];
    position[0] += (s32)x; position[1] += (s32)y;
    hud_group_scope++;
    dl = widescreenNativeHUDGroup(item, counter, dl);
    hud_group_scope--;
    position[0] = saved_x; position[1] = saved_y;
    return dl;
}

void widescreenHUDIcon(void* sprite_ptr, s32 argument) {
    if (!active() || !DetectAdventure() || !HUD || *(u8*)0x807FC928 != 1) {
        widescreenNativeHUDIcon(sprite_ptr, argument);
        return;
    }
    u8* sprite = sprite_ptr;
    void* owner = *(void**)(sprite + 0x35C);
    f32 x = 0, y = 0;
    if (active() && DetectAdventure() && HUD && *(u8*)0x807FC928 == 1) {
        for (s32 item = 0; item < 15; item++) {
            u8* counter = HUD[item].counter_pointer;
            for (s32 n = 0; counter && n < 128; n++) {
                if ((void*)counter == owner) { hudOffsets(item, &x, &y); break; }
                counter = *(u8**)(counter + 0x18);
            }
            if (counter && (void*)counter == owner) break;
        }
    }
    f32* position = (f32*)(sprite + 0x340);
    f32 saved_x = position[0], saved_y = position[1];
    /* Sprite matrices use quarter-pixel origins; counter origins use pixels. */
    position[0] += x * 4.0f; position[1] += y * 4.0f;
    widescreenNativeHUDIcon(sprite, argument);
    position[0] = saved_x; position[1] = saved_y;
}

Gfx* widescreenHealth(Gfx* dl, void* progress, void* kong, void* camera) {
    static Mtx projection[2] __attribute__((aligned(16)));
    Gfx* first = dl;
    dl = widescreenNativeHealth(dl, progress, kong, camera);
    if (!active() || !DetectAdventure() || *(u8*)0x807FC928 != 1) return dl;
    Mtx* matrix = &projection[*(u8*)0x807444FC & 1];
    s32 replaced = 0;
    for (Gfx* cmd = first; cmd < dl; cmd++) {
        if (cmd->words.w0 == 0xDA380007 && cmd->words.w1 == 0x020000C0) {
            f32 m[4][4];
            guMtxL2F(m, (Mtx*)(*(u8**)0x8076A048 + 0xC0));
            m[3][1] -= (HUD_EDGE_Y * 4.0f) * m[1][1];
            guMtxF2L(m, matrix);
            cmd->words.w1 = (u32)matrix & 0x1FFFFFFF;
            replaced = 1;
        }
    }
    if (replaced) {
        dl->words.w0 = 0xDA380007; dl->words.w1 = 0x020000C0; dl++;
    }
    return dl;
}

void widescreenOrtho(Mtx* matrix, f32 left, f32 right, f32 bottom, f32 top,
                     f32 near, f32 far, f32 scale) {
    /* Captured framebuffers and the separate sky/background projection must
     * keep covering the full viewport. These are not HUD artwork. */
    u32 address = (u32)matrix;
    if (active() && address != 0x80767E28 && address != 0x80768FD8 &&
        address != 0x807FD928) {
        f32 pad = (right - left) / 6.0f;
        left -= pad;
        right += pad;
    }
    widescreenNativeOrtho(matrix, left, right, bottom, top, near, far, scale);
}

static Gfx* maskSides(Gfx* dl, s32 player) {
    if (!active()) return dl;
    u8* changes = *(u8**)0x807FC924;
    if (!changes) return dl;
    s16* rect = (s16*)(changes + player * 0x2F0 + 0x270);
    s32 margin = (rect[2] - rect[0] + 7) / 8;
    /* The aspect-correct corner artwork ends inside the viewport. Cover its
     * outside edges; native mask code immediately restores its drawing state. */
    gDPPipeSync(dl++);
    gDPSetCycleType(dl++, G_CYC_1CYCLE);
    gDPSetScissor(dl++, G_SC_NON_INTERLACE, rect[0], rect[1], rect[2], rect[3]);
    gDPSetRenderMode(dl++, G_RM_OPA_SURF, G_RM_OPA_SURF2);
    gDPSetCombineMode(dl++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
    gDPSetPrimColor(dl++, 0, 0, 0, 0, 0, 255);
    gDPFillRectangle(dl++, rect[0], rect[1], rect[0] + margin, rect[3]);
    gDPFillRectangle(dl++, rect[2] - margin, rect[1], rect[2], rect[3]);
    gDPPipeSync(dl++);
    return dl;
}

Gfx* widescreenCameraMask(Gfx* dl) {
    return widescreenNativeCameraMask(maskSides(dl, 0));
}

Gfx* widescreenSniperMask(Gfx* dl, void* actor) {
    u8* data = *(u8**)((u8*)actor + 0x174);
    return widescreenNativeSniperMask(maskSides(dl, data[0x1A4]), actor);
}

Gfx* widescreenShutterMask(Gfx* dl, void* actor) {
    u8* data = *(u8**)((u8*)actor + 0x174);
    return widescreenNativeShutterMask(maskSides(dl, data[0x1A4]), actor);
}

static s32 rectX(s32 x) {
    s32 centre = *(s16*)0x80744490 * 2;
    x = centre + ((x - centre) * 3) / 4;
    if (x < 0) x = 0;
    if (x > 4095) x = 4095;
    return x;
}

static void textureRects(Gfx* first, Gfx* end) {
    /* RDP texture rectangles bypass the RSP projection matrices. Transform
     * their endpoints and inverse texture step together, including flipped
     * sprites. Leave fills, scissors and texture coordinates untouched. */
    for (Gfx* cmd = first; cmd < end; cmd++) {
        if ((cmd->words.w0 >> 24) == 0xE4 && cmd + 2 < end) {
            cmd->words.w0 = (cmd->words.w0 & 0xFF000FFF) |
                (rectX((cmd->words.w0 >> 12) & 0xFFF) << 12);
            cmd->words.w1 = (cmd->words.w1 & 0xFF000FFF) |
                (rectX((cmd->words.w1 >> 12) & 0xFFF) << 12);
            s32 step = ((s16)(cmd[2].words.w1 >> 16) * 4) / 3;
            if (step < -32768) step = -32768;
            if (step > 32767) step = 32767;
            cmd[2].words.w1 = ((u32)(u16)step << 16) | (cmd[2].words.w1 & 0xFFFF);
            cmd += 2;
        }
    }
}

void widescreenSpriteRect(Gfx** list, s16 x, s16 y) {
    Gfx* first = *list;
    widescreenNativeSpriteRect(list, x, y);
    if (active() && !rect_scope) textureRects(first, *list);
}

Gfx* widescreenText(Gfx* dl, u8 font, s16 x, s16 y, char* text) {
    Gfx* first = dl;
    rect_scope++;
    dl = widescreenNativeText(dl, font, x, y, text);
    rect_scope--;
    if (active() && !rect_scope) textureRects(first, dl);
    return dl;
}

Gfx* widescreenLogo(Gfx* dl) {
    Gfx* first = dl;
    rect_scope++;
    dl = widescreenNativeLogo(dl);
    rect_scope--;
    if (active()) textureRects(first, dl);
    return dl;
}

static Gfx* raceMap(Gfx* dl, void* actor) {
    Gfx* first = dl;
    dl = ((Gfx*(*)(Gfx*, void*))0x8002CBEC)(dl, actor);
    /* The map/markers use the corrected projection, but the coloured box and
     * border are RDP fills. Transform those together with the map artwork. */
    for (Gfx* cmd = first; cmd < dl; cmd++) {
        if ((cmd->words.w0 >> 24) == 0xF6) {
            s32 right = (cmd->words.w0 >> 12) & 0xFFF;
            s32 left = (cmd->words.w1 >> 12) & 0xFFF;
            if (right - left >= (*(s16*)0x80744490 - 20) * 4) continue;
            cmd->words.w0 = (cmd->words.w0 & 0xFF000FFF) | (rectX(right) << 12);
            cmd->words.w1 = (cmd->words.w1 & 0xFF000FFF) | (rectX(left) << 12);
        }
    }
    return dl;
}

Gfx* widescreenCounter(Gfx* dl, s16 x, s16 y, s16* shown, s16 count, u8* timer) {
    Gfx* first = dl;
    dl = widescreenNativeCounter(dl, x, y, shown, count, timer);
    if (active()) {
        /* Scissors are RDP coordinates, so the projected digits otherwise
         * slide outside their old animation window. Keep the final native
         * viewport-scissor restoration unchanged, including split screens. */
        for (Gfx* cmd = first; cmd + 1 < dl; cmd++) {
            if ((cmd->words.w0 >> 24) == 0xED) {
                s32 left = (cmd->words.w0 >> 12) & 0xFFF;
                s32 right = (cmd->words.w1 >> 12) & 0xFFF;
                if (right - left >= (*(s16*)0x80744490 - 20) * 4) continue;
                cmd->words.w0 = (cmd->words.w0 & 0xFF000FFF) | (rectX(left) << 12);
                cmd->words.w1 = (cmd->words.w1 & 0xFF000FFF) | (rectX(right) << 12);
            }
        }
    }
    return dl;
}

static Gfx* searchlight(Gfx* dl, void* actor_ptr) {
    u8* actor = actor_ptr;
    u8* data = *(u8**)(actor + 0x174);
    f32 x, y;
    widescreenProject(*(f32*)(actor + 0x7C), *(f32*)(actor + 0x80),
        *(f32*)(actor + 0x84), &x, &y, 0, 1.0f, *(u8*)0x807FC929);
    /* This is a world-attached aiming cursor, not a screen-anchored HUD
     * element. Cancel position contraction while retaining normal artwork. */
    f32 centre = *(s16*)0x80744490 * 0.5f;
    s16 px = (centre + (x - centre) * (4.0f / 3.0f)) * 4.0f;
    s16 py = y * 4.0f;
    gDPPipeSync(dl++);
    gDPSetCombineMode(dl++, G_CC_DECALRGBA, G_CC_DECALRGBA);
    gDPSetRenderMode(dl++, G_RM_XLU_SURF, G_RM_XLU_SURF2);
    gSPDisplayList(dl++, (Gfx*)0x01000118);
    /* Exact DK64 matrix commands. This repository's SDK matrix macro uses
     * the older flag/layout variant despite its F3DEX2 opcode definitions. */
    dl->words.w0 = 0xDA380007;
    dl->words.w1 = 0x020000C0;
    dl++;
    if (actor[0x154] == 0 || actor[0x154] == 1) {
        s16 offsets[4][3] = {{-52,-52,225},{52,-52,315},{52,52,45},{-52,52,135}};
        for (s32 i = 0; i < 4; i++) {
            dl = widescreenImage(dl, ((*(u32*)0x8076A064 >> 1) % 12) + 0x83,
                0, 2, 32, 16, px + offsets[i][0], py + offsets[i][1],
                3.2f, 3.2f, offsets[i][2], 0.0f);
        }
    }
    dl->words.w0 = 0xDA380003;
    dl->words.w1 = 0x02000180;
    dl++;
    if (actor[0x154] == 0 || actor[0x154] == 1) {
        dl = widescreenAnimatedText(dl, data[0x23], 8, 30.0f, 36.0f, 0.0f, 1.5f);
        dl = widescreenCounter(dl, 38, 50, (s16*)(data + 0x26), *(s16*)(data + 0x28), data + 0x24);
    }
    return dl;
}

void widescreenQueue(void* draw, void* actor, u8 layer) {
    /* The same overlay addresses have other meanings in other maps. */
    if (active() && (CurrentMap == 27 || CurrentMap == 185) &&
        draw == (void*)0x8002CBEC) draw = raceMap;
    if (active() && (CurrentMap == 103 || (CurrentMap >= 138 && CurrentMap <= 140)) &&
        draw == (void*)0x8002CC08) draw = searchlight;
    widescreenNativeQueue(draw, actor, layer);
}

static void install(u32 address, void* function) {
    volatile u32* code = (volatile u32*)address;
    code[0] = 0x08000000 | (((u32)function & 0x0FFFFFFF) >> 2);
    code[1] = 0;
    osWritebackDCache((void*)address, 8);
    osInvalICache((void*)address, 8);
}

void widescreenTick(void) {
    static s32 installed;
    if (!installed) {
        install(0x80006DE4, widescreenOrtho);
        install(0x8070F2FC, widescreenSpriteRect);
        install(0x806FF144, widescreenCameraMask);
        install(0x806FF75C, widescreenSniperMask);
        install(0x806FFB2C, widescreenShutterMask);
        install(0x8068C350, widescreenQueue);
        install(0x8068DC54, widescreenCounter);
        install(0x806FD490, widescreenText);
        install(0x80006050, widescreenPerspective);
        install(0x806F9D8C, widescreenHUDCounter);
        install(0x806FA1A4, widescreenHUDGroup);
        install(0x8071BE04, widescreenHUDIcon);
        install(0x807085D0, widescreenHealth);
        installed = 1;
    }
}
