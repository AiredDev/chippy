import time
from renderer import Renderer
from keyboard import Keyboard
# from speaker import Speaker # TODO
from cpu import CPU

renderer = Renderer(10)
keyboard = Keyboard()
# speaker = Speaker() # TODO
cpu = CPU(renderer, keyboard)#, speaker) # TODO

FPS = 60

def init():
	start = time.time() * 1000 # milliseconds since the epoch
	fps_interval = 1000 / FPS
	#print("Entered init()")

	cpu.load_sprites_into_memory()
	cpu.load_ROM("roms/BLITZ")

	renderer.root.after(1, step, start, fps_interval)
	renderer.root.after(1, init)
		
def step(startTime, interval):
	#print("Entered step()")
	now = time.time() * 1000
	elapsed = now - startTime
	print(elapsed)

	if elapsed > interval:
		renderer.root.after(1, cpu.cycle)
	
	#renderer.root.after(1, cpu.cycle)

def on_close_window():
	#print("Entered on_close_window()")
	global closed
	closed = True
	renderer.root.destroy()

def test_render():
	#print("Entered test_render()")
	renderer.test_render()
	renderer.render()

#t = threading.Thread(target=init)
#t.start()

renderer.root.bind("<Button-1>", lambda e: init())
#renderer.root.bind("<Button-1>", lambda e: test_render())
#renderer.root.bind("<Button-3>", lambda e: renderer.clear())
renderer.root.mainloop()