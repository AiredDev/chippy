from pynput import keyboard

class Keyboard:
	def __init__(self):
		#print("Entered Keyboard.__init__()")
		self.KEYMAP = {
			'1': 0x1, # 1
			'2': 0x2, # 2
			'3': 0x3, # 3
			'4': 0xC, # 4
			'q': 0x4, # Q
			'w': 0x5, # W
			'e': 0x6, # E
			'r': 0xD, # R
			'a': 0x7, # A
			's': 0x8, # S
			'd': 0x9, # D
			'f': 0xE, # F
			'z': 0xA, # Z
			'x': 0x0, # X
			'c': 0xB, # C
			'v': 0xF  # V
		}

		self.keys_pressed = [False for _ in range(0xF)]

		# some CHIP-8 instructions require waiting for the next keypress
		self.on_next_key_press = None

		listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
		listener.start()
	def on_press(self, key):
		#print("Entered Keyboard.on_press()")
		key = self.KEYMAP.get(key)
		if key:
			self.keys_pressed[key] = True

		if (self.on_next_key_press is not None and key):
			# calls a function, if on_next_key_press is defined as a function
			self.on_next_key_press(key)
			self.on_next_key_press = None
	def on_release(self, key):
		#print("Entered Keyboard.on_release()")
		key = self.KEYMAP.get(key)
		if key:
			self.keys_pressed[key] = False
	def is_key_pressed(self, key):
		#print("Entered Keyboard.is_key_pressed()")
		return self.keys_pressed[key]