import tkinter as tk
import tkinter.ttk as ttk
import numpy as np

class Renderer:
	def __init__(self, scale=1):
		#print("Entered Renderer.__init__()")
		self.scale = scale
		self.cols = 64
		self.rows = 32
		self.display = np.array([0 for _ in range(self.cols * self.rows)], np.byte)

		self.root = tk.Tk()
		self.frm = ttk.Frame(self.root, padding=10).grid()
		self.cvs = tk.Canvas(self.frm, height=self.rows*self.scale, width=self.cols*self.scale)
		self.cvs.grid()
	
	def toggle_pixel(self, x, y):
		#print("Entered Renderer.toggle_pixel()")
		if x >= self.cols:
			x -= self.cols
		elif x < 0:
			x += self.cols
		
		if y >= self.rows:
			y -= self.rows
		elif y < 0:
			y += self.rows

		# translate (x, y) coords to an array index
		pixel_location = x + (y * self.cols)

		# toggle pixel at the index
		self.display[pixel_location] ^= 1
		
		# used to set or clear V[0xF] in the DRW instruction
		return not self.display[pixel_location]
	
	def clear(self):
		#print("Entered Renderer.clear()")
		self.display = [0 for i in range(self.cols * self.rows)]
		self.render()

	def render(self):
		print("Entered Renderer.render()")
		# vblank
		self.cvs.create_rectangle(0, 0, self.cvs.winfo_reqwidth(), self.cvs.winfo_reqheight(), fill="white")

		for i in range(self.cols * self.rows):
			x = (i % self.cols) * self.scale
			y = (i // self.cols) * self.scale

			if self.display[i]:
				self.cvs.create_rectangle(x, y, x + self.scale, y + self.scale, fill="black")

	def test_render(self):
		#print("Entered Renderer.test_render()")
		self.toggle_pixel(0, 0)
		self.toggle_pixel(0, 5)
		self.toggle_pixel(9, 3)
		self.toggle_pixel(5, 2)
		self.toggle_pixel(63, 31)
		self.toggle_pixel(32, 16)

if __name__ == "__main__":
	r = Renderer(25)
	r.test_render()
	r.render()
	r.root.mainloop()