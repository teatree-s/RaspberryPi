"""
This program is based on the sample program at Adafruit-Python-Usage.
(https://learn.adafruit.com/1-8-tft-display/python-usage)

2021/09/06 var1.0
"""

import digitalio
import board
from PIL import Image, ImageDraw
import adafruit_rgb_display.st7735 as st7735

import RPi.GPIO as GPIO
from time import sleep
import glob

print("Start...")

# Configuration for CS and DC pins
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# for Display.
disp = st7735.ST7735R(
    spi,
    rotation=90,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    bgr=True
)
print("Display width :", disp.width)
print("Display height:", disp.height)

# for Files.
files = glob.glob("./image/*")
print(files)

file_count = len(files)
file_index = 0

# for Buttons.
button_pinA = 5
button_pinC = 6
GPIO.setup(button_pinA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_pinC, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def buttonA_callback(channel):
    print("A button was pressed.")
    global file_index,file_count
    file_index = file_index+1
    if file_count == file_index:
      file_index = 0
    image = Image.open(files[file_index])
    disp_image(image)

def buttonC_callback(channel):
    print("C button was pressed.")
    global file_index,file_count
    if file_index == 0:
      file_index = file_count-1
    else:
      file_index = file_index-1
    image = Image.open(files[file_index])
    disp_image(image)

GPIO.add_event_detect(button_pinA, GPIO.FALLING, callback=buttonA_callback, bouncetime=300)
GPIO.add_event_detect(button_pinC, GPIO.FALLING, callback=buttonC_callback, bouncetime=300)

print("Initialize done.")

disp.fill(0x0000)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

def disp_image(image):

  # Scale the image to the smaller screen dimension
  image_ratio = image.width / image.height
  screen_ratio = width / height
  if screen_ratio < image_ratio:
      scaled_width = image.width * height // image.height
      scaled_height = height
  else:
      scaled_width = width
      scaled_height = image.height * width // image.width
  image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

  # Crop and center the image
  x = scaled_width // 2 - width // 2
  y = scaled_height // 2 - height // 2
  image = image.crop((x, y, x + width, y + height))

  # Display image.
  disp.image(image)

if file_count:
    image = Image.open(files[file_index])
    disp_image(image)

try:
    while True:
      sleep(1)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
