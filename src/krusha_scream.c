#include "../include/common.h"
#include "../assets/krusha/scream.h"

/* The supplied stereo recording only. Each original channel has its own
 * native VADPCM voice; no vocal overlays, gain duplicates or extra effects. */
extern void* krushaNativeStartSound(ALBank*, s16, u16, u8, f32, u8, void**);
extern void krushaNativeStopSound(void*);

static ALEnvelope scream_envelope = {0, KRUSHA_SCREAM_MICROSECONDS, 0, 127, 127};
static ALKeyMap scream_key = {0, 0, 0, 0, 60, 0};
static ALWaveTable left_wave = {
    (u8*)KRUSHA_SCREAM_LEFT_ROM, KRUSHA_SCREAM_LEFT_BYTES, AL_ADPCM_WAVE, 1,
    {.adpcmWave = {0, (ALADPCMBook*)&scream_left_book}}
};
static ALWaveTable right_wave = {
    (u8*)KRUSHA_SCREAM_RIGHT_ROM, KRUSHA_SCREAM_RIGHT_BYTES, AL_ADPCM_WAVE, 1,
    {.adpcmWave = {0, (ALADPCMBook*)&scream_right_book}}
};
static ALSound left_sound = {&scream_envelope, &scream_key, &left_wave, 64, 127, 1};
static ALSound right_sound = {&scream_envelope, &scream_key, &right_wave, 64, 127, 1};
static ALInstrument left_instrument = {
    .volume = 127, .pan = 64, .priority = 64, .flags = 1,
    .soundCount = 1, .soundArray = {&left_sound}
};
static ALInstrument right_instrument = {
    .volume = 127, .pan = 64, .priority = 64, .flags = 1,
    .soundCount = 1, .soundArray = {&right_sound}
};
static ALBank left_bank = {
    .instCount = 1, .flags = 1, .sampleRate = 22050,
    .percussion = 0, .instArray = {&left_instrument}
};
static ALBank right_bank = {
    .instCount = 1, .flags = 1, .sampleRate = 22050,
    .percussion = 0, .instArray = {&right_instrument}
};

/* Persistent, independently owned handles, cleared by the native allocator.
 * Explicit initialization avoids COMMON-symbol relocation in armips. */
void* krushaScreamHandle = 0;
void* krushaScreamRightHandle = 0;

void krushaPlayScream(void) {
    osSetThreadPri(0, 0x1A);
    if (krushaScreamHandle) krushaNativeStopSound(krushaScreamHandle);
    if (krushaScreamRightHandle) krushaNativeStopSound(krushaScreamRightHandle);
    // Maximum valid native volume. The encoded stereo waveform is jointly
    // peak-normalized with a small margin, preserving its original balance.
    krushaNativeStartSound(&left_bank, 1, 32767, 0, 1.0f, 0, &krushaScreamHandle);
    krushaNativeStartSound(&right_bank, 1, 32767, 127, 1.0f, 0, &krushaScreamRightHandle);
    osSetThreadPri(0, 0xA);
}
