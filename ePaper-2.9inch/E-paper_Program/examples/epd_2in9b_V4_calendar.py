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
from waveshare_epd import epd2in9b_V4
import time
from PIL import Image, ImageDraw, ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd2in9b V4 Demo")

    epd = epd2in9b_V4.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    time.sleep(1)

    logging.info("1.read bmp file")
    Blimage = Image.open(os.path.join(picdir, "ohinasama-bl.bmp"))
    Rimage = Image.open(os.path.join(picdir, "ohinasama-red.bmp"))

    # Drawing on the image
    logging.info("2.Drawing calendar")
    font24 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 24)
    font14 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 14)

    HBlimage = Image.new("1", (epd.height, epd.width), 255)  # 250*122
    HRimage = Image.new("1", (epd.height, epd.width), 255)  # 250*122
    drawbl = ImageDraw.Draw(HBlimage)
    drawr = ImageDraw.Draw(HRimage)

    drawbl.bitmap((24, 0), Blimage)
    drawr.bitmap((24, 0), Rimage)

    CalX = 124
    CalY = 12
    drawbl.text((CalX + 24, CalY - 8), "2026 Mar.", font=font24, fill=0)
    drawr.line((CalX, CalY + 20, CalX + 148, CalY + 20), fill=0)
    drawbl.text((CalX + 8, CalY + 24), "     Mo Tu We Th Fr Sa", font=font14, fill=0)
    drawbl.text(
        (CalX + 8, CalY + 36), "        2   3    4   5   6   7", font=font14, fill=0
    )
    drawbl.text((CalX + 8, CalY + 48), "        9 10  11 12 13 14", font=font14, fill=0)
    drawbl.text(
        (CalX + 8, CalY + 60), "      16 17  18 19      21", font=font14, fill=0
    )
    drawbl.text((CalX + 8, CalY + 72), "      23 24  25 26 27 28", font=font14, fill=0)
    drawbl.text((CalX + 8, CalY + 84), "      30 31", font=font14, fill=0)
    drawr.text((CalX + 8, CalY + 24), "Su", font=font14, fill=0)
    drawr.text((CalX + 8, CalY + 36), "  1", font=font14, fill=0)
    drawr.text((CalX + 8, CalY + 48), "  8", font=font14, fill=0)
    drawr.text(
        (CalX + 8, CalY + 60), "15                        20", font=font14, fill=0
    )
    drawr.text((CalX + 8, CalY + 72), "22", font=font14, fill=0)
    drawr.text((CalX + 8, CalY + 84), "29", font=font14, fill=0)
    # drawr.text((CalX + 8, CalY + 96), "31", font=font14, fill=0)
    epd.display(epd.getbuffer(HBlimage), epd.getbuffer(HRimage))

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in9b_V4.epdconfig.module_exit(cleanup=True)
    exit()
