from MiniScreen import *
import time

screen = MiniScreen()

def p():
	print("ji")

menu = Menu("Welcome to Blot", [
	Menu("Calibrate Pen Up", [
		MenuAction("Pen Up", p),
		MenuAction("Pen Down", p),
	]),
	Menu("Calibrate Speed", [
		MenuAction("Slower", p),
		MenuAction("Faster", p),
	]),
])
screen.show(menu)
screen.run()

time.sleep(10)

screen.backlight.off()

