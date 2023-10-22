import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735
from adafruit_bme280 import basic as adafruit_bme280

import RPi.GPIO as GPIO
from time import sleep, time
import glob

import datetime
import subprocess

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

# for BME280.
# Create sensor object, using the board's default I2C bus.
i2c = board.I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

# change this to match the location's pressure (hPa) at sea level
bme280.sea_level_pressure = 1013.25

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


def buttonC_callback(channel):
    print("C button was pressed.")


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

# First define some constants to allow easy resizing of shapes.
image_font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTSIZE = 24
COLOR_TURQUOISE_BLUE = (28, 236, 254)

# Get drawing object to draw on image.
image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)


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


def get_system_info():
    system_info = {}

    # CPUの型番を取得
    cpuinfo = subprocess.check_output(
        "cat /proc/cpuinfo | grep 'Hardware'", shell=True
    ).decode()
    val = cpuinfo.split(":")[1].strip()
    system_info["hardware"] = f"{val}"

    # CPU温度を取得
    temp = subprocess.check_output("vcgencmd measure_temp", shell=True).decode()
    val = temp.replace("temp=", "").replace("'C\n", "°C")
    system_info["cpu temp"] = f"{val}"

    # メモリのサイズを取得
    meminfo = subprocess.check_output(
        "cat /proc/meminfo | grep 'MemTotal'", shell=True
    ).decode()
    val = int(int(meminfo.split()[1]) / 1024)
    system_info["ram size"] = f"{val} M"

    # microSDカードの情報を取得
    df_output = subprocess.check_output("df -h /media", shell=True).decode()
    df_lines = df_output.split("\n")[1]  # 2行目の情報を取得
    df_info = df_lines.split()
    val = df_info[1]
    system_info["sd size"] = f"{val}"
    val = df_info[3]
    system_info["sd free space"] = f"{val}"

    return system_info


def draw_background():
    disp.fill(0x0000)

    draw.rectangle((0, 0, width, 20), fill=(0, 32, 32))
    draw.rectangle((0, 118, width, 120), fill=(0, 32, 32))

    # date
    FONTSIZE = 8
    font = ImageFont.truetype(image_font, FONTSIZE)

    current_date = datetime.date.today()
    text = current_date.strftime("%Y/%m/%d")
    draw.text((2, 2), text, font=font, fill=COLOR_TURQUOISE_BLUE)

    text = datetime.datetime.now().strftime("%A")
    draw.text((2, 12), text, font=font, fill=COLOR_TURQUOISE_BLUE)

    FONTSIZE = 18
    font = ImageFont.truetype(image_font, FONTSIZE)

    current_time = datetime.datetime.now().time()
    text = current_time.strftime("%H:%M:%S")
    draw.text((54, 2), text, font=font, fill=COLOR_TURQUOISE_BLUE)

    draw.line([(140, 2), (140, 18)], fill="gray")
    draw.line([(144, 4), (156, 4)], fill="gray")
    draw.line([(144, 10), (156, 10)], fill="gray")
    draw.line([(144, 16), (156, 16)], fill="gray")

    # System infomation
    FONTSIZE = 14
    font = ImageFont.truetype(image_font, FONTSIZE)

    text = "Infomation"
    draw.text((0, 22), text, font=font, fill="darkorange")

    FONTSIZE = 8
    font = ImageFont.truetype(image_font, FONTSIZE)

    text = "CPU:"
    draw.text((0, 44), text, font=font, fill="gray")
    text = " Temp:"
    draw.text((0, 60), text, font=font, fill="gray")
    text = "RAM:"
    draw.text((0, 74), text, font=font, fill="gray")
    text = "SD:"
    draw.text((0, 88), text, font=font, fill="gray")
    text = " Free:"
    draw.text((0, 102), text, font=font, fill="gray")

    system_info = get_system_info()
    text = system_info["hardware"]
    draw.text((34, 44), text, font=font, fill="lightgray")
    text = system_info["cpu temp"]
    draw.text((34, 60), text, font=font, fill="lightgray")
    text = system_info["ram size"]
    draw.text((34, 74), text, font=font, fill="lightgray")
    text = system_info["sd size"]
    draw.text((34, 88), text, font=font, fill="lightgray")
    text = system_info["sd free space"]
    draw.text((34, 102), text, font=font, fill="lightgray")

    # temperature, humidity, atmospheric pressure
    FONTSIZE = 12
    font = ImageFont.truetype(image_font, FONTSIZE)

    text = "Temp"
    draw.text((98, 22), text, font=font, fill=COLOR_TURQUOISE_BLUE)
    text = "Humidity"
    draw.text((98, 52), text, font=font, fill=COLOR_TURQUOISE_BLUE)
    text = "Pressure"
    draw.text((78, 82), text, font=font, fill=COLOR_TURQUOISE_BLUE)

    FONTSIZE = 16
    font = ImageFont.truetype(image_font, FONTSIZE)

    temp = ""
    draw.text((100, 36), temp, font=font, fill="lightgray")
    hum = ""
    draw.text((100, 66), hum, font=font, fill="lightgray")
    pres = ""
    draw.text((80, 96), pres, font=font, fill="lightgray")

    # Display image.
    disp.image(image)


def draw_parameter():
    # date
    FONTSIZE = 18
    font = ImageFont.truetype(image_font, FONTSIZE)

    current_time = datetime.datetime.now().time()
    text = current_time.strftime("%H:%M:%S")
    draw.rectangle((54, 0, 138, 20), fill=(0, 32, 32))
    draw.text((54, 2), text, font=font, fill=COLOR_TURQUOISE_BLUE)

    # temperature, humidity, atmospheric pressure
    FONTSIZE = 12
    font = ImageFont.truetype(image_font, FONTSIZE)

    text = "Temp"
    draw.text((98, 22), text, font=font, fill=COLOR_TURQUOISE_BLUE)
    text = "Humidity"
    draw.text((98, 52), text, font=font, fill=COLOR_TURQUOISE_BLUE)
    text = "Pressure"
    draw.text((78, 82), text, font=font, fill=COLOR_TURQUOISE_BLUE)

    FONTSIZE = 16
    font = ImageFont.truetype(image_font, FONTSIZE)

    temp = "%0.1f C" % bme280.temperature
    draw.rectangle((100, 36, 159, 52), fill="black")
    draw.text((100, 36), temp, font=font, fill="lightgray")
    hum = "%0.1f %%" % bme280.relative_humidity
    draw.rectangle((100, 66, 159, 82), fill="black")
    draw.text((100, 66), hum, font=font, fill="lightgray")
    pres = "%0.0f hPa" % bme280.pressure
    draw.rectangle((80, 96, 159, 112), fill="black")
    draw.text((80, 96), pres, font=font, fill="lightgray")

    # Display image.
    disp.image(image)


def draw_footer():
    block = 16
    for i in range((block - 1), 160, block):
        disp.fill_rectangle(117, 0, 2, width, 0x1C3)
        disp.fill_rectangle(117, 160 - i, 2, block, 0xCD19)
        sleep((1 * block / 160) * 0.6)


draw_background()

if __name__ == "__main__":
    try:
        while True:
            start_time = time()
            draw_parameter()
            draw_footer()
            wait_time = 1 - (time() - start_time)
            sleep(wait_time)

    except KeyboardInterrupt:
        pass

    finally:
        # GPIO.cleanup()
        print("Done.")
