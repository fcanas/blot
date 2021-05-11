from MiniScreen import *
import time

screen = MiniScreen()

def penUp:
	print("pen up")
	
def penDown:
	print("pen down")

def menu_exit:
	screen.backlight.off()
	
exit = MenuAction("Exit", menu_pop)

def menu_pop:
	screen.backlight.off()
	time.sleep(1)
	screen.backlight.on()

menu = Menu("Welcome to Blot", [
	Menu("Calibrate Pen Up", [
		MenuAction("Pen Up", penUp),
		MenuAction("Pen Up", penDown),
		exit
	]),
	exit
])
menu.show(screen)

time.sleep(10)

screen.backlight.off()

