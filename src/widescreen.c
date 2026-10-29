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
extern s32 widescreenProject(f32, f32, f32, f32*, f32*, s32, f32, s32);
extern Gfx* widescreenImage(Gfx*, u16, s32, s32, s32, s32, s16, s16, f32, f32, s32, f32);
extern Gfx* widescreenAnimatedText(Gfx*, s16, s32, f32, f32, f32, f32);
static s32 rect_scope;

/* 4:3 framebuffer displayed at 16:9: x must be 3/4 of its old width.
 * Keep screen-space groups together around the original screen centre. World
 * sprites use the perspective projection and never pass through this path. */
static s32 active(void) { return *(volatile u8*)0x807444C0 != 0; }

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
        installed = 1;
    }
}
