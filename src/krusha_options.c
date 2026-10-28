#include "../include/common.h"

extern void vanillaOptionsInput(void* actor, s32 input);
extern void krushaSetEnabled(s32 enabled);
extern s32 krushaMenuTransform(void*, f32, f32, f32*, f32*, s32, s8, f32);
extern Gfx* krushaMenuDrawList(Gfx*, void*, char**, s32, u32*, s16, f32*, f32, s16);
extern Gfx* krushaPrintStyledText(Gfx*, s16, s16, s16, char*, u32);

void krushaOptionsInput(void* actor, s32 input) {
    u8* data = *(u8**)((u8*)actor + 0x174);
    *(s8*)0x800338FC = 5;
    if (*(f32*)data == 0.0f && *(f32*)(data + 4) == 0.0f && data[0x17] == 4) {
        if ((input & 0x30) && !(*(s16*)0x80033670 & 0x30)) {
            krushaSetEnabled(!krushaEnabled());
            playSound(0x74, 0x7FFF, 63.0f, 1.0f, 0, 0);
        }
        // Index four was the hidden language option in the USA menu.
        input &= ~0x30;
    }
    vanillaOptionsInput(actor, input);
}

Gfx* krushaOptionsDraw(void* actor, Gfx* dl) {
    void* data = *(void**)((u8*)actor + 0x174);
    char** strings = *(char***)0x80033F28;
    char* labels[5];
    f32 x, y, width;
    u32 selected;
    *(s8*)0x800338FC = 5;
    *(u32*)0x807FBB60 &= ~0x10;
    for (s32 i = 0; i < 4; i++) labels[i] = strings[42 + i];
    labels[4] = "KRUSHA";
    krushaMenuTransform(data, 160.0f, 20.0f, &x, &y, 5, 0, 1.5f);
    dl = krushaPrintStyledText(dl, 1, 640, y * 4.0f, strings[41], 0x81);
    dl = krushaMenuDrawList(dl, data, labels, 5, &selected, 1, &width, 80.0f, -1);
    *(s16*)0x80033674 = 1000;
    krushaMenuTransform(data, 160.0f, 150.0f, &x, &y, 2, 0, 1.5f);
    x = (x - width) * 4.0f;
    y *= 4.0f;
    char* value = 0;
    switch (selected) {
        case 0: value = strings[47 + *(u8*)0x807444C0]; break;
        case 1: value = strings[49 + StorySkip]; break;
        case 2: *(s16*)0x80033674 = 0; break;
        case 3: value = strings[52 + *(u8*)0x80744530]; break;
        case 4: value = krushaEnabled() ? "ON" : "OFF"; break;
    }
    if (value) dl = krushaPrintStyledText(dl, 1, x, y + 64, value, 0x81);
    return dl;
}
