import time
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7735
from serial import Serial
from micropyGPS import MicropyGPS
import threading
import smbus
from decimal import Decimal, ROUND_HALF_UP

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the display:
disp = st7735.ST7735R(
    spi,
    rotation=270,
    x_offset=2,
    y_offset=1,
    bgr=True,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)

# First define some constants to allow easy positioning of text.
padding = 0
x = 0

# Load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", 18)

TIME_ZONE = 9  # タイムゾーン(UTF+TIME_ZOME)

gps = MicropyGPS(TIME_ZONE, "dd")  # MicroGPSオブジェクトを生成する。(引数はタイムゾーンの時差と出力フォーマット)

gps_serial = Serial("/dev/serial0", 9600, timeout=10)

bus_number = 1
i2c_address = 0x76

bus = smbus.SMBus(bus_number)

digT = []
digP = []
digH = []

t_fine = 0.0


def run_gps():  # GPSモジュールを読み、GPSオブジェクトを更新する
    while True:
        try:
            sentence = gps_serial.readline().decode("utf-8")  # GPSデーターを読み、文字列に変換する
        except UnicodeDecodeError:
            print("Decode Error")
            continue
        if sentence[0] != "$":  # 先頭が'$'でなければ捨てる
            print("Not Matched $")
            continue
        for x in sentence:  # 読んだ文字列を解析してGPSオブジェクトにデーターを追加、更新する
            gps.update(x)


def writeReg(reg_address, data):
    bus.write_byte_data(i2c_address, reg_address, data)


def get_calib_param():
    calib = []

    for i in range(0x88, 0x88 + 24):
        calib.append(bus.read_byte_data(i2c_address, i))
    calib.append(bus.read_byte_data(i2c_address, 0xA1))
    for i in range(0xE1, 0xE1 + 7):
        calib.append(bus.read_byte_data(i2c_address, i))

    digT.append((calib[1] << 8) | calib[0])
    digT.append((calib[3] << 8) | calib[2])
    digT.append((calib[5] << 8) | calib[4])
    digP.append((calib[7] << 8) | calib[6])
    digP.append((calib[9] << 8) | calib[8])
    digP.append((calib[11] << 8) | calib[10])
    digP.append((calib[13] << 8) | calib[12])
    digP.append((calib[15] << 8) | calib[14])
    digP.append((calib[17] << 8) | calib[16])
    digP.append((calib[19] << 8) | calib[18])
    digP.append((calib[21] << 8) | calib[20])
    digP.append((calib[23] << 8) | calib[22])
    digH.append(calib[24])
    digH.append((calib[26] << 8) | calib[25])
    digH.append(calib[27])
    digH.append((calib[28] << 4) | (0x0F & calib[29]))
    digH.append((calib[30] << 4) | ((calib[29] >> 4) & 0x0F))
    digH.append(calib[31])

    for i in range(1, 2):
        if digT[i] & 0x8000:
            digT[i] = (-digT[i] ^ 0xFFFF) + 1

    for i in range(1, 8):
        if digP[i] & 0x8000:
            digP[i] = (-digP[i] ^ 0xFFFF) + 1

    for i in range(0, 6):
        if digH[i] & 0x8000:
            digH[i] = (-digH[i] ^ 0xFFFF) + 1


def getData():
    data = []
    for i in range(0xF7, 0xF7 + 8):
        data.append(bus.read_byte_data(i2c_address, i))
    pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
    hum_raw = (data[6] << 8) | data[7]

    return pres_raw, temp_raw, hum_raw


def compensate_P(adc_P):
    global t_fine
    pressure = 0.0

    v1 = (t_fine / 2.0) - 64000.0
    v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * digP[5]
    v2 = v2 + ((v1 * digP[4]) * 2.0)
    v2 = (v2 / 4.0) + (digP[3] * 65536.0)
    v1 = (
        ((digP[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8) + ((digP[1] * v1) / 2.0)
    ) / 262144
    v1 = ((32768 + v1) * digP[0]) / 32768

    if v1 == 0:
        return 0
    pressure = ((1048576 - adc_P) - (v2 / 4096)) * 3125
    if pressure < 0x80000000:
        pressure = (pressure * 2.0) / v1
    else:
        pressure = (pressure / v1) * 2
    v1 = (digP[8] * (((pressure / 8.0) * (pressure / 8.0)) / 8192.0)) / 4096
    v2 = ((pressure / 4.0) * digP[7]) / 8192.0
    pressure = pressure + ((v1 + v2 + digP[6]) / 16.0)

    return pressure


def compensate_T(adc_T):
    global t_fine
    v1 = (adc_T / 16384.0 - digT[0] / 1024.0) * digT[1]
    v2 = (
        (adc_T / 131072.0 - digT[0] / 8192.0)
        * (adc_T / 131072.0 - digT[0] / 8192.0)
        * digT[2]
    )
    t_fine = v1 + v2
    temperature = t_fine / 5120.0

    return temperature


def compensate_H(adc_H):
    global t_fine
    var_h = t_fine - 76800.0
    if var_h != 0:
        var_h = (adc_H - (digH[3] * 64.0 + digH[4] / 16384.0 * var_h)) * (
            digH[1]
            / 65536.0
            * (
                1.0
                + digH[5] / 67108864.0 * var_h * (1.0 + digH[2] / 67108864.0 * var_h)
            )
        )
    else:
        return 0
    var_h = var_h * (1.0 - digH[0] * var_h / 524288.0)
    if var_h > 100.0:
        var_h = 100.0
    elif var_h < 0.0:
        var_h = 0.0

    return var_h


def setup():
    osrs_t = 1  # Temperature oversampling x 1
    osrs_p = 1  # Pressure oversampling x 1
    osrs_h = 1  # Humidity oversampling x 1
    mode = 3  # Normal mode
    t_sb = 5  # Tstandby 1000ms
    filter = 0  # Filter off
    spi3w_en = 0  # 3-wire SPI Disable

    ctrl_meas_reg = (osrs_t << 5) | (osrs_p << 2) | mode
    config_reg = (t_sb << 5) | (filter << 2) | spi3w_en
    ctrl_hum_reg = osrs_h

    writeReg(0xF2, ctrl_hum_reg)
    writeReg(0xF4, ctrl_meas_reg)
    writeReg(0xF5, config_reg)


gps_thread = threading.Thread(target=run_gps, args=())  # 上の関数を実行するスレッドを生成
gps_thread.daemon = True
gps_thread.start()  # スレッドを起動

setup()
get_calib_param()

try:
    while True:
        h = gps.timestamp[0] if gps.timestamp[0] < 24 else gps.timestamp[0] - 24
        print(
            "%2d年 %2d月 %2d日 %2d時 %02d分 %02d秒"
            % (
                gps.date[2],
                gps.date[1],
                gps.date[0],
                h,
                gps.timestamp[1],
                gps.timestamp[2],
            )
        )
        print("緯度経度: %2.8f, %2.8f" % (gps.latitude[0], gps.longitude[0]))
        print("海抜: %f [m]" % gps.altitude)
        print("速度: %f [km/h]" % gps.speed[2])
        print("=" * 40)

        show_date = "%2d年%2d月%2d日" % (gps.date[2], gps.date[1], gps.date[0])
        show_time = "%2d時%02d分%02d秒" % (h, gps.timestamp[1], gps.timestamp[2])
        show_speed = "速度:%6.1f km/h" % float(
            Decimal(str(gps.speed[2])).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        )
        show_above_sea_level = "海抜:%6.1f m" % float(
            Decimal(str(gps.altitude)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        )

        pres_raw, temp_raw, hum_raw = getData()
        show_temp = "気温:%6.1f ℃" % float(
            Decimal(str(compensate_T(temp_raw))).quantize(
                Decimal("0.1"), rounding=ROUND_HALF_UP
            )
        )
        show_hum = "湿度:%6.1f ％" % float(
            Decimal(str(compensate_H(hum_raw))).quantize(
                Decimal("0.1"), rounding=ROUND_HALF_UP
            )
        )
        show_pressure = "気圧:%6.2fhPa" % float(
            Decimal(str(compensate_P(pres_raw) / 100)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        )

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Write four lines of text
        y = padding
        draw.text((x, y), show_date, font=font, fill="#FFFFFF")
        y += font.getsize(show_date)[1]
        draw.text((x, y), show_time, font=font, fill="#FFFFFF")
        y += font.getsize(show_time)[1]
        draw.text((x, y), show_speed, font=font, fill="#FF8800")
        y += font.getsize(show_speed)[1]
        draw.text((x, y), show_above_sea_level, font=font, fill="#FFFF00")
        y += font.getsize(show_above_sea_level)[1]
        draw.text((x, y), show_temp, font=font, fill="#00FF00")
        y += font.getsize(show_temp)[1]
        draw.text((x, y), show_hum, font=font, fill="#00FFFF")
        y += font.getsize(show_hum)[1]
        draw.text((x, y), show_pressure, font=font, fill="#0088FF")

        # Display image.
        disp.image(image)
        time.sleep(1)
except KeyboardInterrupt:
    pass
