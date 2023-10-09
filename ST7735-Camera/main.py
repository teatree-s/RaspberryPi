import digitalio
import board
from PIL import Image, ImageDraw
import adafruit_rgb_display.st7735 as st7735

import RPi.GPIO as GPIO
from time import sleep, time
import glob

import cv2
from PIL import Image
import numpy as np

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
print("Display width :", disp.width)
print("Display height:", disp.height)

# for Camera
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
capture = True
fase_capture = False

# for Files.
files = glob.glob("./image/*")
print(files)

file_count = len(files)
file_index = 0

# for Buttons.
buttonA_pin = 5
buttonC_pin = 6
GPIO.setup(buttonA_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buttonC_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def buttonA_callback(channel):
    print("A button was pressed.")
    global capture
    capture = not capture


def buttonC_callback(channel):
    print("C button was pressed.")
    global fase_capture
    fase_capture = not fase_capture


GPIO.add_event_detect(
    buttonA_pin, GPIO.FALLING, callback=buttonA_callback, bouncetime=300
)
GPIO.add_event_detect(
    buttonC_pin, GPIO.FALLING, callback=buttonC_callback, bouncetime=300
)

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


# if file_count:
#     image = Image.open(files[file_index])
#     disp_image(image)

sleep(3)

try:
    while True:
        if capture:
            start_time = time()
            ret, frame = cap.read()
            if ret:
                if fase_capture:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(
                        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                    )
                    for x, y, w, h in faces:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # cv2.imwrite("capture.jpg", frame)
                # print("save picture")
                image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                disp_image(image)
            print(f"capture time :{time() - start_time:.3f}")
        else:
            sleep(1)

except KeyboardInterrupt:
    pass

finally:
    # GPIO.cleanup()
    cap.release()
    print("Done.")
