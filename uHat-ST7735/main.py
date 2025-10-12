import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735

import RPi.GPIO as GPIO
from time import sleep
import glob

print("Start...")

# Configuration for CS and DC pins
cs_pin = digitalio.DigitalInOut(board.D23)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# for Display.
disp = st7735.ST7735R(
    spi, rotation=90, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE, bgr=True
)
print("Display width :", disp.width)
print("Display height:", disp.height)

# for Files.
files = glob.glob("./image/*")
print(files)

file_count = len(files)
file_index = 0

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


# Display text.
img = Image.new("RGB", (width, height), (0, 0, 0))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
text = "Hello World"
draw.text((40, 50), text, font=font, fill=(255, 255, 255))
disp.image(img)
sleep(3)

try:
    while True:
        file_index = file_index + 1
        if file_count == file_index:
            file_index = 0
        image = Image.open(files[file_index])
        disp_image(image)
        print("Draw Image.")
        sleep(3)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
