# v0.4.1 flashcart packaging

The final build is padded with zeros to a 16 KiB boundary, after all assets are
written and before header CRC validation. This accommodates documented loader
transfer requirements; it is not a universal guarantee of hardware support.
Primary SDK reference: https://github.com/DragonMinded/libdragon/blob/trunk/tools/n64tool.c

For v0.4.1, this appends 7,904 bytes to approved v0.4. Every existing byte and
address remains unchanged. No runtime hardware fixes are included. Use an
Expansion Pak and compatible flashcart with EEPROM16K saves. Original-console
compatibility is unverified; no physical hardware was available for testing.
