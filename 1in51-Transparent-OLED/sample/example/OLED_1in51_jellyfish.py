#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import random
from datetime import datetime

picdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "pic"
)
libdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "lib"
)
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import time
from waveshare_OLED import OLED_1in51
from PIL import Image, ImageDraw, ImageFont
import json
from jellyfish import Jellyfish

logging.basicConfig(level=logging.DEBUG)


class Bubble:
    def __init__(self):
        self._x = 0
        self._y = 0
        self._sleep = 0
        self.reset()

    def reset(self):
        self._x = random.randint(0, 127)
        self._y = 64
        self._sleep = random.randint(1, 10)

    def update(self):
        if self._y == 0:
            self.reset()
        elif self._sleep > 0:
            self._sleep -= 1
        else:
            self._y -= 4

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y


def load_bmp_images(folderpath):
    images = []
    if os.path.isdir(folderpath):
        for file in sorted(os.listdir(folderpath)):
            if file.lower().endswith(".bmp"):
                img_path = os.path.join(folderpath, file)
                try:
                    images.append(Image.open(img_path))
                except Exception as e:
                    print(f"Image loading error: {file}, {e}")
    return images


try:
    disp = OLED_1in51.OLED_1in51()

    logging.info("\r1.51inch OLED ")
    # Initialize library.
    disp.Init()
    # Clear display.
    logging.info("clear display")
    disp.clear()

    picjdir = os.path.join(picdir, "jellyfish")
    jellyfish_images = load_bmp_images(picjdir)
    jellyfish_images_order = []
    with open(os.path.join(picjdir, "jellyfish.json"), "r") as f:
        jellyfish_images_order = json.load(f)
    jellyfish1 = Jellyfish(jellyfish_images, jellyfish_images_order)
    jellyfish2 = Jellyfish(jellyfish_images, jellyfish_images_order, 3)
    bubble1 = Bubble()
    bubble2 = Bubble()
    font1 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 12)

    image = Image.new("1", (disp.width, disp.height), 255)  # 255: clear the frame

    while True:
        image.paste(255, [0, 0, image.width, image.height])
        # Draw jellyfish
        jellyfish1.update()
        image.paste(jellyfish1.get_image(), jellyfish1.get_position())
        jellyfish2.update()
        image.paste(jellyfish2.get_image(), jellyfish2.get_position())
        # Draw bubble
        draw = ImageDraw.Draw(image)
        bubble1.update()
        draw.point((bubble1.x, bubble1.y))
        bubble2.update()
        draw.point((bubble2.x, bubble2.y))
        # Draw time
        time_str = datetime.now().strftime("%H:%M").replace("8", "8")
        draw.text((2, 2), time_str, font=font1)
        # Show time
        image = image.rotate(180)
        disp.ShowImage(disp.getbuffer(image))
        time.sleep(0.2)

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    disp.module_exit()
    exit()
