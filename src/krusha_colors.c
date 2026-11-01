#include "../include/common.h"

/* One-based model 0xED follows the 236 native actor models. The resource hook
 * maps its file request (0xEC) into custom table 27, before native table access.
 * Its distinct model-cache key keeps DK/enemy rings independent, even alive
 * at the same time. No native model slot or player identity is overwritten. */
static s32 spawnShockwaveActor(s32 actor, s32 model, actorData* parent) {
    if (krushaEnabled() && parent && parent == (void*)Player &&
        parent->actorType == 7 && DetectAdventure()) model = 0xED;
    return spawnActor(actor, model);
}

void krushaColorsInstall(void) {
    /* The native call site retains parent in a2; spawnActor ignores it.
     * Replace only that JAL, retaining the native li a0,255 delay slot and
     * every subsequent transform/damage/lifetime instruction. */
    *(volatile u32*)0x80684744 = 0x0C000000 |
        (((u32)spawnShockwaveActor & 0x0FFFFFFF) >> 2);
    osWritebackDCache((void*)0x80684744, 4);
    osInvalICache((void*)0x80684744, 4);
}
