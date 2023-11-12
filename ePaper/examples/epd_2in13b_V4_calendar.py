#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

picdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "pic"
)
libdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "lib"
)
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in13b_V4
import time
from PIL import Image, ImageDraw, ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd2in13b_V4 Demo")

    epd = epd2in13b_V4.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.clear()
    time.sleep(1)

    logging.info("1.read bmp file")
    Blackimage = Image.open(os.path.join(picdir, "santa-kao-black.bmp"))
    Rimage = Image.open(os.path.join(picdir, "santa-kao-red.bmp"))

    # Drawing on the image
    logging.info("2.Drawing calendar")
    font20 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 24)
    font12 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 14)

    HBlackimage = Image.new("1", (epd.height, epd.width), 255)  # 250*122
    HRimage = Image.new("1", (epd.height, epd.width), 255)  # 250*122
    drawblack = ImageDraw.Draw(HBlackimage)
    drawr = ImageDraw.Draw(HRimage)

    drawblack.bitmap((0, 0), Blackimage)
    drawr.bitmap((0, 0), Rimage)

    CalX = 102
    CalY = 10
    drawblack.text((0, CalY - 8), "2023", font=font20, fill=0)
    drawblack.text((CalX + 60, CalY - 8), "12", font=font20, fill=0)
    drawblack.text((CalX + 8, CalY + 24), "　 Mo Tu We Th Fr Sa", font=font12, fill=0)
    drawblack.text((CalX + 8, CalY + 36), "　　　　　　　　　1", font=font12, fill=0)
    drawblack.text(
        (CalX + 8, CalY + 48), "　   4   5   6   7   8   9", font=font12, fill=0
    )
    drawblack.text((CalX + 8, CalY + 60), "　 11 12 13 14 15 16", font=font12, fill=0)
    drawblack.text((CalX + 8, CalY + 72), "　 18 19 20 21 22 23", font=font12, fill=0)
    drawblack.text((CalX + 8, CalY + 84), "　 25 26 27 28 29 30", font=font12, fill=0)
    drawr.line((CalX + 8, CalY + 20, CalX + 148, CalY + 20), fill=0)
    drawr.text((CalX + 8, CalY + 24), "Su", font=font12, fill=0)
    # drawr.text((CalX + 8, CalY + 36), "", font=font12, fill=0)
    drawr.text((CalX + 8, CalY + 48), "  3", font=font12, fill=0)
    drawr.text((CalX + 8, CalY + 60), "10", font=font12, fill=0)
    drawr.text((CalX + 8, CalY + 72), "17", font=font12, fill=0)
    drawr.text((CalX + 8, CalY + 84), "24", font=font12, fill=0)
    drawr.text((CalX + 8, CalY + 96), "31", font=font12, fill=0)
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRimage))

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in13b_V4.epdconfig.module_exit()
    exit()
