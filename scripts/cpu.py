from pydoc import render_doc
import random
import numpy as np
from pynput import keyboard as kb

class CPU:
	def __init__(self, renderer, keyboard):#, speaker): # TODO speaker
		#print("Entered CPU.__init__()")
		random.seed()
		self.renderer = renderer
		self.keyboard = keyboard
#		self.speaker = speaker # TODO

		# Memory
		self.memory = np.array([0 for i in range(4096)], np.uint8)

		# Array of 16 8-bit registers
		self.V = np.array([0 for i in range(16)], np.uint8)

		# Stores memory addresses
		self.I = np.uint16(0)

		# Special 8-bit timer arrays
		self.delay_timer = np.uint8(0)
		self.sound_timer = np.uint8(0)

		# 16-bit program counter, always starts from 0x200 because lower values are reserved for the original interpreter
		self.pc = np.uint16(0x200)

		# Stack, not initialised with a size to avoid empty results
		self.stack = np.array([0 for i in range(16)])
		self.sp = np.uint8(0)

		# Some instructions require a pause
		self.paused = False

		# Instructions per cycle
		self.speed = 10

	def load_sprites_into_memory(self):
		#print("Entered CPU.load_sprites_into_memory()")
		# Array of hex bytes for each sprite, all 5 bytes long
		# Values are given at http://devernay.free.fr/hacks/chip8/C8TECH10.HTM#font
		SPRITES = [
			0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
			0x20, 0x60, 0x20, 0x20, 0x70, # 1
			0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
			0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
			0x90, 0x90, 0xF0, 0x10, 0x10, # 4
			0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
			0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
			0xF0, 0x10, 0x20, 0x40, 0x40, # 7
			0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
			0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
			0xF0, 0x90, 0xF0, 0x90, 0x90, # A
			0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
			0xF0, 0x80, 0x80, 0x80, 0xF0, # C
			0xE0, 0x90, 0x90, 0x90, 0xE0, # D
			0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
			0xF0, 0x80, 0xF0, 0x80, 0x80  # F
		]

		# These sprites, according to the reference, are stored in the interpreter section of memory
		for i, j in enumerate(SPRITES):
			self.memory[i] = j
	
	def load_program_into_memory(self, program):
		#print("Entered CPU.load_program_into_memory()")
		for i, j in enumerate(program, 0x200):
			self.memory[i] = j

	def load_ROM(self, romPath):
		#print("Entered CPU.load_ROM()")
		with open(romPath, "rb") as f:
			program = np.fromfile(f, np.uint8)
		self.load_program_into_memory(program)
	
	def cycle(self):
		print("Entered CPU.cycle()")
		for _ in range(self.speed):
			if not self.paused:
				# CHIP-8 instructions are 2 bytes long. Therefore, we read two bytes from memory and combine them to get a full instruction.
				opcode = (self.memory[self.pc] << 8) | (self.memory[self.pc + 1])
				self.execute_instruction(opcode)
		
		if not self.paused:
			self.update_timers()
		
#		self.play_sound()
		self.renderer.render()
	
	def update_timers(self):
		#print("Entered CPU.update_timers()")
		if self.delay_timer > 0: self.delay_timer -= 1
		if self.sound_timer > 0: self.sound_timer -= 1
	
	def play_sound(self):
		if self.sound_timer > 0:
			self.speaker.play(440) # TODO
		else:
			self.speaker.stop() # TODO
	
	def execute_instruction(self, opcode):
		print("Entered CPU.execute_instruction()")
		# Each instruction is 2 bytes long, so we increment the PC by 2
		self.pc += 2

		x = (opcode & 0x0F00) >> 8 # lower 4 bits of the high byte
		y = (opcode & 0x00F0) >> 4 # upper 4 bits of the low byte

		# And now the logic for each instruction
		high_nybble = opcode & 0xF000

		if high_nybble == 0x0000:
			low_byte = opcode & 0x00FF

			if low_byte == 0xE0:                                         # CLS
				self.renderer.clear()
			
			elif low_byte == 0xEE:                                       # RET
				self.pc = self.stack[self.sp]
				self.sp -= 1
			
			else:
				print("Error: Unrecognised instruction.")

		elif high_nybble == 0x1000:                                      # JP addr
			self.pc = opcode & 0x0FFF
		
		elif high_nybble == 0x2000:                                      # CALL addr
			self.sp += 1
			self.stack[self.sp] = self.pc
			self.pc = opcode & 0x0FFF
		
		elif high_nybble == 0x3000:                                      # SE Vx, byte
			if self.V[x] == opcode & 0x00FF:
				self.pc += 2
		
		elif high_nybble == 0x4000:                                      # SNE Vx, byte
			if self.V[x] != opcode & 0x00FF:
				self.pc += 2
		
		elif high_nybble == 0x5000:
			low_nybble = opcode & 0x000F

			if low_nybble == 0x00:                                       # SE Vx, Vy
				if self.V[x] == self.V[y]:
					self.pc += 2
			
			else:
				print("Error: Unrecognised instruction.")
		
		elif high_nybble == 0x6000:                                      # LD Vx, byte
			self.V[x] = opcode & 0x00FF
		
		elif high_nybble == 0x7000:                                      # ADD Vx, byte
			self.V[x] += opcode & 0x00FF
		
		elif high_nybble == 0x8000:
			low_nybble = opcode & 0x000F

			if low_nybble == 0x0:                                        # LD Vx, Vy
				self.V[x] = self.V[y]
			
			elif low_nybble == 0x1:                                      # OR Vx, Vy
				self.V[x] |= self.V[y]
			
			elif low_nybble == 0x2:                                      # AND Vx, Vy
				self.V[x] &= self.V[y]
			
			elif low_nybble == 0x3:                                      # XOR Vx, Vy
				self.V[x] ^= self.V[y]
			
			elif low_nybble == 0x4:                                      # ADD Vx, Vy
				sum = self.V[x] + self.V[y]

				if sum > 255:
					self.V[0xF] = 1
				else:
					self.V[0xF] = 0
				
				self.V[x] = sum & 0xFF

			elif low_nybble == 0x5:                                      # SUB Vx, Vy
				if self.V[x] > self.V[y]:
					self.V[0xF] = 1
				else:
					self.V[0xF] = 0
				self.V[x] -= self.V[y]
			
			elif low_nybble == 0x6:                                      # SHR Vx{, Vy}
				if self.V[x] & 0x0001 == 1:
					self.V[0xF] = 1
				else:
					self.V[0xF] = 0
				self.V[x] >>= 1
			
			elif low_nybble == 0x7:                                      # SUBN Vx, Vy
				if self.V[y] > self.V[x]:
					self.V[0x0F] = 1
				else:
					self.V[0x0F] = 0
				self.V[x] = self.V[y] - self.V[x]
			
			elif low_nybble == 0xE:                                      # SHL Vx{, Vy}
				if self.V[x] & 0x1000 == 1:
					self.V[0xF] = 1
				else:
					self.V[0xF] = 0
				self.V[x] <<= 1
			
			else:
				print("Error: Unrecognised instruction.")
		
		elif high_nybble == 0x9000:
			low_nybble = opcode & 0x000F

			if low_nybble == 0x00:                                       # SNE Vx, Vy
				if self.V[x] != self.V[y]:
					self.pc += 2
			else:
				print("Error: Unrecognised instruction.")
		
		elif high_nybble == 0xA000:                                      # LD I, addr
			self.I = opcode & 0x0FFF
		
		elif high_nybble == 0xB000:                                      # JP V0, addr
			self.pc = self.V[0] + (opcode & 0x0FFF)
		
		elif high_nybble == 0xC000:                                      # RND Vx, byte
			rand = random.randbytes(1)[0]
			self.V[x] = rand & (opcode & 0x00FF)
		
		elif high_nybble == 0xD000:                                      # DRW Vx, Vy, nybble
			low_nybble = opcode & 0x000F

			for row in range(low_nybble):
				byte = self.memory[self.I + row]
				for col in range(8):
					if (byte & 0x80) > 0:
						if self.renderer.toggle_pixel(self.V[x] + col, self.V[y] + row):
							self.V[0xF] = 1
						else:
							self.V[0xF] = 0
					byte <<= 1
			#self.renderer.render()
			
		elif high_nybble == 0xE000:
			low_byte = opcode & 0x00FF

			if low_byte == 0x9E:                                         # SKP Vx
				if self.keyboard.is_key_pressed(self.V[x]):
					self.pc += 2
			
			elif low_byte == 0xA1:                                       # SKNP Vx
				if not self.is_key_pressed(self.V[x]):
					self.pc += 2
			
			else:
				print("Error: Unrecognised instruction.")
		
		elif high_nybble == 0xF000:
			low_byte = opcode & 0xFF
			
			if low_byte == 0x07:                                         # LD Vx, DT
				self.V[x] = self.delay_timer
			
			elif low_byte == 0x0A:                                       # LD Vx, K
				self.paused = True
				with kb.Events() as events:
					event = events.get(1e6)
				self.paused = False
				self.V[x] = self.keyboard.KEYMAP[event.key.char]
			
			elif low_byte == 0x15:                                       # LD DT, Vx
				self.delay_timer = self.V[x]
			
			elif low_byte == 0x18:                                       # LD ST, Vx
				self.sound_timer = self.V[x]
			
			elif low_byte == 0x1E:                                       # ADD I, Vx
				self.I += self.V[x]
			
			elif low_byte == 0x29:                                       # LD F, Vx
				self.I += self.V[x] * 5
			
			elif low_byte == 0x33:                                       # LD B, Vx
				bcd = self.int_to_bcd(self.V[x])
				self.memory[self.I] = (bcd >> 0) & 0xF
				self.memory[self.I + 1] = (bcd >> 4) & 0xF
				self.memory[self.I + 2] = (bcd >> 8) & 0xF
			
			elif low_byte == 0x55:                                       # LD [I], Vx
				for reg_no in range(x):
					self.memory[self.I + reg_no] = self.V[reg_no]
			
			elif low_byte == 0x65:                                       # LD Vx, [I]
				for reg_no in range(x):
					self.V[reg_no] = self.memory[self.I + reg_no]
			
			else:
				print("Error: Unrecognised instruction.")
		
		else:
			print("Error: Unrecognised instruction.")
	
	# Love me a good double-dabble
	# This doesn't work for values > 1999, but luckily for us we don't need to consider values over 255 since n is only 8 bits long
	def int_to_bcd(self, n):
		#print("Entered CPU.int_to_bcd()")
		combinedReg = 0b0000 << 16 | 0b0000 << 12 | 0b0000 << 8 | n # Initialisation - one nybble for hundreds, tens and units and one byte for n

		for _ in range(8):
			# get individual parts of the combined register
			hundredsNybble = (combinedReg & 0xF0000) >> 16
			tensNybble     = (combinedReg & 0x0F000) >> 12
			unitsNybble    = (combinedReg & 0x00F00) >> 8
			binaryByte     = (combinedReg & 0x000FF) >> 0

			# dabble
			if hundredsNybble >= 5:
				hundredsNybble += 3
			if tensNybble >= 5:
				tensNybble += 3
			if unitsNybble >= 5:
				unitsNybble += 3

			# double
			combinedReg = hundredsNybble << 16 | tensNybble << 12 | unitsNybble << 8 | binaryByte << 0 # stitching the combined reg back together
			combinedReg <<= 1

		# remove the 8 rightmost bits because they were used to store the number in binary, which we no longer need
		combinedReg >>= 8
		
		return combinedReg