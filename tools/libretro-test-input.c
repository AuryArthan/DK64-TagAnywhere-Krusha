/* Test-only libretro gamepad bridge. No game memory or ROM modification. */
#include <stdint.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
typedef int16_t (*input_fn)(unsigned,unsigned,unsigned,unsigned);
static input_fn frontend;
static volatile int32_t *pad;
static int16_t poll(unsigned port,unsigned device,unsigned index,unsigned id) {
    if (!pad) return frontend(port,device,index,id);
    if (port) return 0;
    if ((device&255)==1) {
        if(id==256) return (int16_t)pad[0];
        if(id<16) return (pad[0]>>id)&1;
    }
    if ((device&255)==5 && index<2 && id<2) return pad[1+index*2+id];
    return 0;
}
void retro_set_input_state(input_fn callback) {
    frontend=callback;
    const char *name=getenv("DK64_PADFILE");
    if(name) {
        int fd=open(name,O_RDONLY);
        if(fd>=0) { void *m=mmap(0,20,PROT_READ,MAP_SHARED,fd,0);close(fd);if(m!=MAP_FAILED)pad=m; }
    }
    void (*set)(input_fn)=dlsym(RTLD_NEXT,"retro_set_input_state");
    if(!set) abort();
    set(poll);
}
