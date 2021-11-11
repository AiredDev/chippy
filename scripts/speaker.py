import winsound

class Speaker:
	def play(self, frequency, duration):
		winsound.Beep(frequency, duration)

s = Speaker()
s.play(100, 1000)