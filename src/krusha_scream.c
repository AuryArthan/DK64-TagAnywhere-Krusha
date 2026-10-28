#include "../include/common.h"
#include "../assets/krusha/scream.h"

/* A separate one-sound bank: no original sample, instrument, or music bank is
 * replaced. The native audio DMA streams the VADPCM payload directly from ROM. */
extern void* krushaNativeStartSound(ALBank*, s16, u16, u8, f32, u8, void**);
extern void krushaNativeStopSound(void*);

static ALEnvelope scream_envelope = {0, KRUSHA_SCREAM_MICROSECONDS, 0, 127, 127};
static ALKeyMap scream_key = {0, 0, 0, 0, 60, 0};
static ALWaveTable scream_wave = {
    (u8*)KRUSHA_SCREAM_ROM, KRUSHA_SCREAM_BYTES, AL_ADPCM_WAVE, 1,
    {.adpcmWave = {0, (ALADPCMBook*)&scream_book}}
};
static ALSound scream_sound = {&scream_envelope, &scream_key, &scream_wave, 64, 127, 1};
static ALInstrument scream_instrument = {
    .volume = 127, .pan = 64, .priority = 64, .flags = 1,
    .soundCount = 1, .soundArray = {&scream_sound}
};
static ALBank scream_bank = {
    .instCount = 1, .flags = 1, .sampleRate = 22050,
    .percussion = 0, .instArray = {&scream_instrument}
};

/* Must outlive the audio voice: the native allocator clears this pointer when
 * it frees the sound. A stack-local handle would be unsafe. */
// Explicit initialization avoids a COMMON-symbol relocation in armips.
void* krushaScreamHandle = 0;
void* krushaScreamBoostHandle = 0;

void krushaPlayScream(void) {
    // Match playSound's native thread-priority protection around allocation.
    osSetThreadPri(0, 0x1A);
    if (krushaScreamHandle) krushaNativeStopSound(krushaScreamHandle);
    if (krushaScreamBoostHandle) krushaNativeStopSound(krushaScreamBoostHandle);
    // 65% blend at 2.1 overall gain exceeds one voice's 32767 ceiling.
    // Two synchronized native voices give 44729 total without changing pitch
    // or clipping the encoded recording. Each owns a persistent handle.
    krushaNativeStartSound(&scream_bank, 1, 32767, 63, 1.0f, 0, &krushaScreamHandle);
    krushaNativeStartSound(&scream_bank, 1, 11962, 63, 1.0f, 0, &krushaScreamBoostHandle);
    osSetThreadPri(0, 0xA);
}
