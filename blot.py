from MiniDisplay import *
from Screen import *
import time

screen = MiniDisplay()

def goHome():
	pass

menu = Menu("Welcome to Blot", [
		Menu("Calibrate", [
			ValueAdjust("Pen Up", 0, 75, 100),
			ValueAdjust("Pen Down", 0, 30, 100),
			ValueAdjust("Speed", 0, 120, 250, step=5)	
		]),
		MenuAction("Home", goHome)
	])
screen.show(menu)
screen.run()

time.sleep(10)

screen.backlight.off()

