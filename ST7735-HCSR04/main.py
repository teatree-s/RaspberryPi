import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735

import sys
import RPi.GPIO as GPIO
from time import sleep
import glob

import sensor
import servo
import math

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
    spi, rotation=90, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE, bgr=True
)
string_image = Image.new("RGB", (48, 12))
string_draw = ImageDraw.Draw(string_image)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 12)

print("Display width :", disp.width)
print("Display height:", disp.height)

# for Files.
files = glob.glob("./image/*")
print(files)

file_count = len(files)
file_index = 0

# for HC-SR04.
trig_pin = 15
echo_pin = 14
sensor = sensor.HCSR04(trig_pin, echo_pin)

# for SG90.
servo_pin = 12
servo = servo.SG90(servo_pin)
servo.set_angle(90)

# for Buttons.
buttonA_pin = 5
buttonC_pin = 6
GPIO.setup(buttonA_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buttonC_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
search = False


def buttonA_callback(channel):
    print("A button was pressed.")
    global search
    search = not search


def buttonC_callback(channel):
    print("C button was pressed.")
    disp.fill(0x0000)
    disp_background()


GPIO.add_event_detect(
    buttonA_pin, GPIO.FALLING, callback=buttonA_callback, bouncetime=300
)
GPIO.add_event_detect(
    buttonC_pin, GPIO.FALLING, callback=buttonC_callback, bouncetime=300
)

print("Initialize done.")

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


def disp_background():
    for angle in range(30, 151):
        x, y = conv_lengh_to_xy(40, angle)
        disp.pixel(x, y, 0x03E0)
        x, y = conv_lengh_to_xy(80, angle)
        disp.pixel(x, y, 0x03E0)
        x, y = conv_lengh_to_xy(120, angle)
        disp.pixel(x, y, 0x03E0)
        if angle % 30 == 0:
            line(128, 80, x, y, 0x03E0)


def line(x0, y0, x1, y1, color):
    if abs(y1 - y0) > abs(x1 - x0):
        steep = True
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    else:
        steep = False

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = abs(y1 - y0)

    err = dx // 2
    if y0 < y1:
        ystep = 1
    else:
        ystep = -1

    while x0 <= x1:
        if steep:
            disp.pixel(y0, x0, color)
        else:
            disp.pixel(x0, y0, color)
        err -= dy
        if err < 0:
            y0 += ystep
            err += dx
        x0 += 1


def conv_lengh_to_xy(lengh, angle):
    x = round(lengh * math.cos(math.radians(angle)))
    y = round(lengh * math.sin(math.radians(angle)))
    x, y = -y + 128, -x + 80
    return x, y


# if file_count:
#     image = Image.open(files[file_index])
#     disp_image(image)

servo_angle = 90
inc_angle = 1
x, y, x0, y0 = 0, 0, 0, 0

disp.fill(0x0000)
disp_background()

try:
    while True:
        if search:
            # servo.
            servo.set_angle(servo_angle)
            servo_angle += inc_angle
            # 30 - 150
            if 149 < servo_angle:
                inc_angle = -1
            elif 29 > servo_angle:
                inc_angle = 1

            # sensor.
            distance = sensor.get_distance()
            print("distance : ", distance)

            # display.
            # draw distance line.
            x, y = conv_lengh_to_xy(distance, servo_angle)
            print("x, y : ", x, y)
            if x0 != 0 and y0 != 0:
                line(x0, y0, x, y, 0xEEEE)
            x0, y0 = x, y
            # disp distance value.
            str_distance = "{:.1f}cm".format(distance)
            string_draw.rectangle((0, 0, 48, 12), outline=0, fill=(0, 0, 0))
            string_draw.text((0, 0), str_distance, font=font, fill="#FFFF00")
            disp.image(string_image, x=116, y=112)
        else:
            sleep(1)

except KeyboardInterrupt:
    pass

finally:
    servo.end()
    # GPIO.cleanup()
    sys.exit()
