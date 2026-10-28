#include "../include/common.h"
#include "../include/krusha_camera_mesh.h"

extern f32 sinf(f32);
extern f32 cosf(f32);

/* World-space vertices of the visible, animated body. The holstered
 * bazooka is excluded. Native bone matrices already include actor scale/yaw. */
static f32 body_points[sizeof(krusha_mesh_points) / sizeof(krusha_mesh_points[0])][3];

static s32 valid(void* p) { return (u32)p >= 0x80000000 && (u32)p < 0x807FF000; }
static f32 dot(f32* a, f32* b) { return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]; }
static f32 absf(f32 a) { return a < 0 ? -a : a; }

static s32 poseBounds(u8* actor, f32* center) {
    u8* model = *(u8**)actor;
    u8* ledge = *(u8**)(actor + 0x140);
    if (!valid(model) || model[0x20] != 23 || !valid(ledge)) return 0;
    u8 bank = *(u8*)0x807444FC;
    if (*(u32*)(ledge + 0x88) != *(u32*)0x8076A064) bank ^= 1;
    Mtx* matrices = *(Mtx**)(ledge + 0x74 + bank * 4);
    if (!valid(matrices)) return 0;
    f32 lo[3] = {1e9f, 1e9f, 1e9f}, hi[3] = {-1e9f, -1e9f, -1e9f};
    s32 count = 0;
    for (u32 b = 0; b < sizeof(krusha_mesh_groups) / sizeof(krusha_mesh_groups[0]); b++) {
        const KrushaMeshGroup* group = &krusha_mesh_groups[b];
        f32 matrix[4][4];
        guMtxL2F(matrix, matrices + group->bone);
        for (s32 p = group->first; p < group->first + group->count; p++) {
            for (s32 axis = 0; axis < 3; axis++) {
                f32 v = matrix[3][axis];
                for (s32 i = 0; i < 3; i++) v += krusha_mesh_points[p][i] * matrix[i][axis];
                if (absf(v - *(f32*)(actor + 0x7C + axis * 4)) > 250.0f) return 0;
                body_points[count][axis] = v;
                if (v < lo[axis]) lo[axis] = v;
                if (v > hi[axis]) hi[axis] = v;
            }
            count++;
        }
    }
    for (s32 i = 0; i < 3; i++) center[i] = (lo[i] + hi[i]) * 0.5f;
    return count;
}

static f32 basis(f32* eye, f32* target, f32* right, f32* up, f32* back) {
    for (s32 i = 0; i < 3; i++) back[i] = eye[i] - target[i];
    f32 distance = sqrtf(dot(back, back));
    if (distance < 1.0f) distance = 1.0f;
    for (s32 i = 0; i < 3; i++) back[i] /= distance;
    f32 horizontal = sqrtf(back[0]*back[0] + back[2]*back[2]);
    if (horizontal < 0.001f) horizontal = 0.001f;
    right[0] = back[2] / horizontal; right[1] = 0; right[2] = -back[0] / horizontal;
    up[0] = back[1]*right[2];
    up[1] = back[2]*right[0] - back[0]*right[2];
    up[2] = -back[1]*right[0];
    return distance;
}

static void project(s32 count, f32* eye, f32* right, f32* up, f32* back, f32* bounds) {
    bounds[0] = bounds[1] = 1e9f; bounds[2] = bounds[3] = -1e9f;
    for (s32 p = 0; p < count; p++) {
        f32 v[3];
        for (s32 i = 0; i < 3; i++) v[i] = body_points[p][i] - eye[i];
        f32 depth = -dot(v, back);
        if (depth < 1.0f) depth = 1.0f;
        f32 x = dot(v, right) / depth, y = dot(v, up) / depth;
        if (x < bounds[0]) bounds[0] = x;
        if (y < bounds[1]) bounds[1] = y;
        if (x > bounds[2]) bounds[2] = x;
        if (y > bounds[3]) bounds[3] = y;
    }
}

static f32 tangent(f32 degrees) {
    f32 angle = degrees * (3.141592654f / 360.0f);
    return sinf(angle) / cosf(angle);
}

void krushaRoarFrame(u8* actor, u8* camera, f32 angle, f32 height_weight, f32 weight) {
    f32* eye = (f32*)(camera + 0x210);
    f32* target = (f32*)(camera + 0x228);
    f32 origin[3], center[3], original_target[3];
    for (s32 i = 0; i < 3; i++) {
        origin[i] = *(f32*)(actor + 0x7C + i * 4);
        center[i] = origin[i];
        original_target[i] = target[i];
    }
    center[1] += 15.0f;
    s32 count = poseBounds(actor, center);
    f32 dx = eye[0] - origin[0], dz = eye[2] - origin[2];
    f32 radius = sqrtf(dx*dx + dz*dz);
    if (radius < 1.0f) { dx = 0; dz = 1; radius = 1; }
    // A normal camera pressed against a wall must not orbit inside his body.
    f32 scale = radius < 75.0f ? 1.0f + (75.0f / radius - 1.0f) * weight : 1.0f;
    f32 c = cosf(angle), s = sinf(angle);
    eye[0] = origin[0] + (dx*c - dz*s) * scale + (center[0] - origin[0]) * weight;
    eye[2] = origin[2] + (dx*s + dz*c) * scale + (center[2] - origin[2]) * weight;
    eye[1] -= 21.0f * height_weight; // Raise four units from the accepted 25-unit drop.

    f32 aim[3];
    for (s32 i = 0; i < 3; i++) aim[i] = center[i];
    f32 right[3], up[3], back[3], bounds[4];
    if (count) {
        // Center the projected body rectangle, including pose/depth asymmetry,
        // rather than the gameplay camera's forward-looking aim point.
        for (s32 pass = 0; pass < 3; pass++) {
            f32 distance = basis(eye, aim, right, up, back);
            project(count, eye, right, up, back, bounds);
            f32 x = (bounds[0] + bounds[2]) * 0.5f * distance;
            f32 y = (bounds[1] + bounds[3]) * 0.5f * distance;
            for (s32 i = 0; i < 3; i++) aim[i] += right[i]*x + up[i]*y;
        }
    }
    for (s32 i = 0; i < 3; i++) target[i] = original_target[i] + (aim[i] - original_target[i]) * weight;

    if (count) {
        basis(eye, target, right, up, back);
        project(count, eye, right, up, back, bounds);
        f32 aspect_scale = *(f32*)0x80747CD0;
        if (aspect_scale < 0.5f || aspect_scale > 2.0f) aspect_scale = 1.0f;
        f32 aspect = *(f32*)(camera + 0x280) * aspect_scale;
        if (aspect < 0.5f) aspect = 1.333333333f;
        f32 needed = absf(bounds[0]) > absf(bounds[2]) ? absf(bounds[0]) : absf(bounds[2]);
        needed /= aspect;
        if (absf(bounds[1]) > needed) needed = absf(bounds[1]);
        if (absf(bounds[3]) > needed) needed = absf(bounds[3]);
        needed /= 0.86f; // Small border around the animated body.
        f32* fov = (f32*)(camera + 0x27C);
        if (needed > tangent(*fov)) {
            // Preserve the requested zoom whenever it fits. Open only enough
            // to keep the body inside the view; avoid cumulative FOV changes.
            f32 lo = *fov, hi = 100.0f;
            for (s32 i = 0; i < 8; i++) {
                f32 mid = (lo + hi) * 0.5f;
                if (tangent(mid) < needed) lo = mid; else hi = mid;
            }
            *fov = hi;
        }
    }
}
