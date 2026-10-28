#include "../include/common.h"
#include "../assets/krusha/scream.h"

extern void krushaMoveAndScaleActor(void*, void*, f32);
extern void krushaNativeActorDelete(void*);
extern void krushaGetChunkLighting(f32*, f32*, f32*, s16);
extern void krushaSetChunkLighting(f32, f32, f32, s16);
extern void vanillaBuildCameraMatrices(void*);
extern f32 sinf(f32);
extern f32 cosf(f32);

static u8* owner;
static u8* camera_owner;
static u8* spotlight;
static s32 stage_map;
static u32 stage_frame;
static f32 saved_fov;
static f32 orbit_angle;
static f32 saved_light[3];
static s16 light_chunk = -1;

static u32 frame(void) { return *(u32*)0x8076A064; }

static s32 sameScene(void) {
    return owner && CurrentMap == stage_map && frame() >= stage_frame;
}

static s32 spotlightAlive(void) {
    if (!spotlight) return 0;
    u8** actors = (u8**)0x807FBFF0;
    u16 count = *(u16*)0x807FC3F0;
    for (u16 i = 0; i < count && i < 256; i++) {
        if (actors[i] == spotlight) return *(u32*)(spotlight + 0x58) == 310;
    }
    return 0;
}

static f32 smooth(f32 t) {
    if (t < 0) t = 0;
    if (t > 1) t = 1;
    return t * t * (3.0f - 2.0f * t);
}

static void lightPerformer(void) {
    s16 chunk = *(s16*)(owner + 0x12C);
    s32 count = *(s32*)0x807F6C28;
    if (count < 1) count = 1;
    if (chunk < 0 || chunk >= count) chunk = -1;
    if (chunk != light_chunk) {
        if (light_chunk != -1) {
            krushaSetChunkLighting(saved_light[0], saved_light[1], saved_light[2], light_chunk);
        }
        light_chunk = chunk;
        if (chunk != -1) {
            krushaGetChunkLighting(&saved_light[0], &saved_light[1], &saved_light[2], chunk);
        }
    }
    if (light_chunk != -1) krushaSetChunkLighting(1.0f, 1.0f, 1.0f, light_chunk);
}

void krushaRoarStageBegin(void* actor) {
    owner = actor;
    stage_map = CurrentMap;
    stage_frame = frame();
    camera_owner = *(u8**)0x807FC924;
    saved_fov = *(f32*)(camera_owner + 0x27C);
    orbit_angle = 0;
    light_chunk = -1;
    spotlight = 0;
    /* Same actor/model and scale as native instrument animation command
     * 80618F74. Keep ownership here instead of occupying the player's vehicle. */
    if (spawnActor(310, 0xA8)) {
        spotlight = *(u8**)0x807FBB44;
        u8* animation = *(u8**)(owner + 4);
        krushaMoveAndScaleActor(spotlight, owner, *(f32*)(animation + 0x34));
        *(u32*)(spotlight + 0x60) |= 0x40000000;
    }
    // Native instrument command 80619018 temporarily raises the chunk light.
    lightPerformer();
}

void krushaRoarStageTick(u32 elapsed) {
    if (!sameScene() || (void*)owner != Player) return;
    if (spotlightAlive()) {
        u8* animation = *(u8**)(owner + 4);
        krushaMoveAndScaleActor(spotlight, owner, *(f32*)(animation + 0x34));
    }
    lightPerformer();
    if (camera_owner == *(u8**)0x807FC924) {
        u8* animation = *(u8**)(owner + 4);
        u8* channel = *(u8**)animation;
        f32 position = *(f32*)(channel + 4);
        f32 last = *(f32*)(channel + 0x18);
        // Reach the close view over the supplied recording, then gently
        // pull back over the final fourteen skeletal frames of the recovery.
        f32 sound_ticks = (KRUSHA_SCREAM_MICROSECONDS - 20000) * (30.0f / 1000000.0f);
        f32 zoom = smooth(elapsed / sound_ticks);
        f32 release = smooth((position - (last - 14.0f)) / 14.0f);
        f32 amount = zoom * (1.0f - release);
        // Another 20% in apparent size beyond the preceding close-up.
        // Orbit 110 degrees, easing home with the zoom.
        *(f32*)(camera_owner + 0x27C) = saved_fov * (1.0f - (1.0f - 0.35f / 1.2f) * amount);
        orbit_angle = 1.919862177f * amount;
    }
}

/* Apply the orbit only while the native renderer builds the view matrices.
 * Camera collision, following, input yaw and future frames retain their own
 * coordinates; never feed the rotated eye back into the camera controller. */
void krushaRoarBuildCameraMatrices(void* display) {
    if (!sameScene() || (void*)owner != Player || owner[0x154] != 0x67 ||
        camera_owner != *(u8**)0x807FC924 || CutsceneActive || orbit_angle == 0) {
        vanillaBuildCameraMatrices(display);
        return;
    }
    f32* eye = (f32*)(camera_owner + 0x210);
    f32* target = (f32*)(camera_owner + 0x228);
    f32 saved_eye[3], saved_target[3];
    f32 x = *(f32*)(owner + 0x7C), z = *(f32*)(owner + 0x84);
    f32 c = cosf(orbit_angle), s = sinf(orbit_angle);
    for (s32 i = 0; i < 3; i++) {
        saved_eye[i] = eye[i];
        saved_target[i] = target[i];
    }
    eye[0] = x + (saved_eye[0] - x) * c - (saved_eye[2] - z) * s;
    eye[2] = z + (saved_eye[0] - x) * s + (saved_eye[2] - z) * c;
    target[0] = x + (saved_target[0] - x) * c - (saved_target[2] - z) * s;
    target[2] = z + (saved_target[0] - x) * s + (saved_target[2] - z) * c;
    vanillaBuildCameraMatrices(display);
    for (s32 i = 0; i < 3; i++) {
        eye[i] = saved_eye[i];
        target[i] = saved_target[i];
    }
}

void krushaRoarStageEnd(void) {
    if (sameScene()) {
        if (spotlightAlive()) krushaNativeActorDelete(spotlight);
        if (light_chunk != -1) {
            krushaSetChunkLighting(saved_light[0], saved_light[1], saved_light[2], light_chunk);
        }
        if (camera_owner == *(u8**)0x807FC924 && ((void*)owner == Player || !CutsceneActive)) {
            *(f32*)(camera_owner + 0x27C) = saved_fov;
        }
    }
    // Map loading owns the old actor heap, camera and lighting arrays.
    spotlight = 0;
    owner = 0;
    camera_owner = 0;
    orbit_angle = 0;
    light_chunk = -1;
}
