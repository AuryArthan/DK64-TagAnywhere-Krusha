; Displaced prologues from the unmodified USA 1.0 executable. These
; trampolines preserve the original arguments and original return address.
vanillaSetAction:
    ANDI t8, a2, 0xFF
    LUI a3, 0x8080
    J 0x806EB0C8
    NOP

vanillaScriptCondition:
    ADDIU sp, sp, -0x78
    SW ra, 0x24(sp)
    J 0x8063EA1C
    NOP

vanillaModelPickupAllowed:
    ADDIU sp, sp, -0x18
    ANDI t6, a2, 0xFFFF
    J 0x806F664C
    NOP

vanillaFindPurchase:
    ADDIU sp, sp, -0x30
    SW s3, 0x20(sp)
    J 0x80025FBC
    NOP

vanillaFairyActor:
    ADDIU sp, sp, -0x58
    SW ra, 0x2C(sp)
    J 0x806C5C28
    NOP

vanillaBarrelEligibility:
    LUI t6, 0x8080
    LW t6, 0xC924(t6)
    J 0x8068077C
    NOP

; The barrel has five faces. Start its selection cursor on DK for an incoming
; Krusha; only this local search key changes, never the player's actor ID.
krushaBarrelSelection:
    LH v0, 0x5A(t4)
    ADDIU t7, r0, 7
    BNE v0, t7, @@resume
    NOP
    ADDIU v0, r0, 2
@@resume:
    AND t6, t5, at
    J 0x80683574
    NOP

vanillaOptionsInput:
    ADDIU sp, sp, -0x30
    SW ra, 0x24(sp)
    J 0x8002D8B4
    NOP
