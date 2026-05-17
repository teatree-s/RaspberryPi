import spidev
from PIL import Image, ImageDraw

class MAX7219:
    def __init__(self, bus=0, device=0, num=1):
        self.num = num
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 10000000

        self.image = Image.new("1", (8 * num, 8))
        self.draw = ImageDraw.Draw(self.image)
        self.init()

    def _write(self, command, data):
        payload = []
        for _ in range(self.num):
            payload.extend([command, data])
        self.spi.xfer2(payload)

    def init(self):
        for command, data in ((12, 0), (15, 0), (11, 7), (9, 0), (12, 1)):
            self._write(command, data)

    def brightness(self, value):
        if not 0 <= value <= 15:
            raise ValueError("Brightness must be 0-15")
        self._write(10, value)

    def fill(self, color):
        fill_color = 255 if color else 0
        self.draw.rectangle((0, 0, 8 * self.num, 8), fill=fill_color)

    def clear(self):
        self.fill(0)

    def text(self, string, x, y, color=1):
        self.draw.text((x, y), string, fill=255 if color else 0)

    def dot(self, x, y, color=1):
        """Draw a single dot (pixel) at coordinates (x, y)"""
        fill_color = 255 if color else 0
        self.draw.point((x, y), fill=fill_color)

    def line(self, x1, y1, x2, y2, color=1):
        """Draw a line from (x1, y1) to (x2, y2)"""
        fill_color = 255 if color else 0
        self.draw.line((x1, y1, x2, y2), fill=fill_color)

    def show(self):
        img_data = self.image.load()
        for y in range(8):
            payload = []
            for m in range(self.num):
                byte = 0
                for x in range(8):
                    if img_data[x + (m * 8), y]:
                        byte |= 1 << (7 - x)
                payload.extend([y + 1, byte])
            self._write(payload[0], payload[1])  # 単体(num=1)用に最適化

    def close(self):
        self.spi.close()
