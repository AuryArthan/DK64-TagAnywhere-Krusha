def patchStaticCode(filename):
	with open(filename, "r+b") as fh:
		# RDRAM Address - 0x5FB300 = ROM address
		# Only the fairy-camera entry check: allow character 5, still exclude
		# Rambi/Enguarde. No change to collectible or character identities.
		fh.seek(0x806E98A0 - 0x805FB300)
		assert fh.read(4) == bytes.fromhex("2b210005"), "Camera guard differs from USA 1.0"
		fh.seek(0x806E98A0 - 0x805FB300)
		fh.write(bytes.fromhex("2b210006"))

		# Startup image: CPU copy into the native 320x240 framebuffer.
		# Keep 1 source texel = 1 framebuffer pixel; extend, do not rescale.
		# The four-pixel unrolled loop requires a width divisible by four.
		from PIL import Image
		with Image.open("bin/Nintendo_Krusha.png") as logo:
			width, height = logo.size
		assert height == 48 and width % 4 == 0 and width <= 320
		left, top = (320-width)//2, (240-height)//2
		patches = [
			(0x805FB8A8, 0x3401F080, 0x34010000 | ((top*320+left)*2)),
			(0x805FB8B8, 0x240500C0, 0x24050000 | width),
			(0x805FB900, 0x24630100, 0x24630000 | ((320-width)*2)),
		]
		for address, expected, replacement in patches:
			fh.seek(address - 0x805FB300)
			assert int.from_bytes(fh.read(4), "big") == expected, "Startup copy differs from USA 1.0"
			fh.seek(address - 0x805FB300)
			fh.write(replacement.to_bytes(4, "big"))

		# Heap Shrink
		fh.seek(0x15212)
		fh.write(bytearray([0x80,0x5D])) # Heap Shrink: lui t5, 0x805d

		# Starting Map & Exit
		# fh.seek(0x119247)
		# fh.write(bytearray([0x22])) # File Start Map
		# fh.seek(0x11925B)
		# fh.write(bytearray([0x0])) # File Start Exit

		# Load race overlay when no overlay specified
		# fh.seek(0x15108) # RDRAM 80631048
		# fh.write(bytearray([0x24, 0x09, 0x00, 0x05])) # ADDIU $t1 $zero 0x0005

		# Increase Object Model 2 Per Map Count
		fh.seek(0x36D24)
		fh.write(bytearray([0x24, 0x0a, 0x02, 0x12])) # li $t2, 465 (original, Jungle Japes)
		fh.seek(0x36D34)
		fh.write(bytearray([0x24, 0x0b, 0x02, 0x12])) # li $t3, 450 (original, All Other Maps)
		fh.seek(0x36CF4)
		fh.write(bytearray([0x24, 0x19, 0x02, 0x12])) # li $t9, 500 (original, Frantic Factory)
		fh.seek(0x36D14)
		fh.write(bytearray([0x24, 0x09, 0x02, 0x12])) # li $t1, 485 (original, Gloomy Galleon)
		fh.seek(0x36D04)
		fh.write(bytearray([0x24, 0x08, 0x02, 0x12])) # li $t0, 500 (original, Angry Aztec)
		fh.seek(0x36CE4)
		fh.write(bytearray([0x24, 0x18, 0x02, 0x12])) # li $t8, 530 (original, Fungi Forest)
