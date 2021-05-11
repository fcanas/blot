import time
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

class Menu:
    def __init__(self, title, options, selectedIndex=0):
        self.title = title
        self.options = options
        self.selectedIndex = selectedIndex
    
    def show(self, screen):
        screen.blank()
        screen.printLn(self.title, "#CCCCCC")
        for idx in range(len(self.options)):
            screen.printLn(self.options[idx].title, selected=(idx==self.selectedIndex))
        screen.commit()

class MenuAction:
    def __init__(self, title, action):
        self.title = title
        self.action = action


# Basic abstraction for Adafruit Mini PiTFT screen
# Derived from https://learn.adafruit.com/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi
# Original code copyright 2021 ladyada for Adafruit Industries, MIT License
# 
class MiniScreen:

    def blank(self):
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=(0, 0, 0))
        self.x = 0
        self.y = self.top
    
    def commit(self):
        self.disp.image(self.image, self.rotation)
    
    def __init__(self):

        # Create the ST7789 display:
        self.disp = st7789.ST7789(
            board.SPI(), # Setup SPI bus using hardware SPI
            cs=digitalio.DigitalInOut(board.CE0), # Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4)
            dc=digitalio.DigitalInOut(board.D25),
            rst=None,
            baudrate=64000000, # Config for display baudrate (default max is 24mhz)
            width=135,
            height=240,
            x_offset=53,
            y_offset=40,
        )
        
        # Create blank image for drawing.
        # Make sure to create image with mode 'RGB' for full color.
        self.height = self.disp.width  # we swap height/width to rotate it to landscape!
        self.width = self.disp.height
        self.image = Image.new("RGB", (self.width, self.height))
        self.rotation = 90
        
        # Text helping things
        self.padding = -2
        self.top = self.padding
        self.bottom = self.height - self.padding
        # Move left to right keeping track of the current x position for drawing shapes.
        self.x = 0
        self.y = self.top
        # Alternatively load a TTF font.  Make sure the .ttf font file is in the
        # same directory as the python script!
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    
        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)
        
        self.blank()
        self.commit()
        
        self.backlight = Backlight()
        self.backlight.on()

    def printLn(self, string, color="#FFFFFF", selected=False):
        messageSize = self.font.getsize(string)
        newY = self.y + messageSize[1]
        textColor = "#000000" if selected else color
        if selected:
            self.draw.rectangle([0, self.y, self.disp.width, newY], fill=color)
        self.draw.text((self.x, self.y), string, font=self.font, fill=textColor)
        self.y = newY + 1 # one extra pixel for inter-line spacing

class Backlight:
    def __init__(self):
        self.pin = digitalio.DigitalInOut(board.D22)
        self.pin.switch_to_output()
    def on(self):
        self.pin.value = True
    def off(self):
        self.pin.value = False


