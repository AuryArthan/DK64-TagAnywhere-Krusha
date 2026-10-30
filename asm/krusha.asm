; Displaced prologues from the unmodified USA 1.0 executable. These
; trampolines preserve the original arguments and original return address.
widescreenNativeOrtho:
    ADDIU sp, sp, -0x68
    MTC1 a1, f12
    J 0x80006DEC
    NOP

widescreenNativePerspective:
    ADDIU sp, sp, -0x68
    MTC1 a2, f12
    J 0x80006058
    NOP

widescreenNativeHUDCounter:
    ADDIU sp, sp, -0x78
    SW ra, 0x24(sp)
    J 0x806F9D94
    NOP

widescreenNativeHUDGroup:
    ADDIU sp, sp, -0x90
    SW a0, 0x90(sp)
    J 0x806FA1AC
    NOP

widescreenNativeHUDIcon:
    ADDIU sp, sp, -0xB0
    SW ra, 0x1C(sp)
    J 0x8071BE0C
    NOP

widescreenNativeHealth:
    ADDIU sp, sp, -0x100
    SW ra, 0x8C(sp)
    J 0x807085D8
    NOP

widescreenNativePauseSprite:
    ADDIU sp, sp, -0x48
    SW ra, 0x1C(sp)
    J 0x806AB4F4
    NOP

widescreenNativePauseCounter:
    ADDIU sp, sp, -0x58
    LW t6, 0x74(sp)
    J 0x806AB810
    NOP

widescreenNativePauseFraction:
    ADDIU sp, sp, -0xF0
    SW ra, 0x3C(sp)
    J 0x806AA0A4
    NOP

widescreenNativeCounter:
    ADDIU sp, sp, -0x78
    SW s0, 0x1C(sp)
    J 0x8068DC5C
    NOP

widescreenNativeText:
    ADDIU sp, sp, -0x80
    SW fp, 0x38(sp)
    J 0x806FD498
    NOP

widescreenNativeLogo:
    ADDIU sp, sp, -0xE8
    SW s0, 0x20(sp)
    J 0x80032934
    NOP

widescreenNativeQueue:
    LUI a3, 0x8075
    ADDIU a3, a3, 0x01E0
    J 0x8068C358
    NOP

widescreenNativeSpriteRect:
    LUI t2, 0x8075
    LW t2, 0x50D0(t2)
    J 0x8070F304
    NOP

widescreenNativeCameraMask:
    ADDIU sp, sp, -0x40
    MOVE v0, a0
    J 0x806FF14C
    NOP

widescreenNativeSniperMask:
    ADDIU sp, sp, -0x78
    LUI t8, 0x8080
    J 0x806FF764
    NOP

widescreenNativeShutterMask:
    ADDIU sp, sp, -0x40
    SW ra, 0x34(sp)
    J 0x806FFB34
    NOP

vanillaBuildActorBones:
    ADDIU sp, sp, -0x18
    SW ra, 0x14(sp)
    J 0x80614A6C
    NOP

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

vanillaBarrelFile:
    ADDIU sp, sp, -0x58
    SW ra, 0x2C(sp)
    J 0x8066B100
    NOP

vanillaBarrelSpawn:
    ADDIU sp, sp, -0x40
    SW s7, 0x34(sp)
    J 0x80682E40
    NOP

vanillaBarrelLayout:
    ADDIU sp, sp, -0x78
    LUI v0, 0x8080
    J 0x80682ABC
    NOP

vanillaBarrelControl:
    ADDIU sp, sp, -0x50
    SW ra, 0x24(sp)
    J 0x806836D8
    NOP

vanillaBarrelName:
    ADDIU sp, sp, -0x18
    SLL v1, a1, 2
    J 0x80683A88
    NOP

vanillaBarrelAnimation:
    ADDIU sp, sp, -0x18
    SW ra, 0x14(sp)
    J 0x80682DFC
    NOP

vanillaOptionsInput:
    ADDIU sp, sp, -0x30
    SW ra, 0x24(sp)
    J 0x8002D8B4
    NOP

vanillaInstrumentInput:
    LUI v0, 0x8080
    LBU v0, 0xC929(v0)
    J 0x806E52D8
    NOP

vanillaBuildCameraMatrices:
    ADDIU sp, sp, -0xC0
    SW ra, 0x9C(sp)
    J 0x805FCA9C
    NOP
