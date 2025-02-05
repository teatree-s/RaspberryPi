import itertools


class Jellyfish:
    def __init__(self, images=[], images_order=[], position=0):
        self.images = images
        self.data = images_order
        self.current_index = 0
        self.x = 0
        self.y = 0
        self.x_values = self.oscillate(0, 110, 2, position)
        self.y_values = self.oscillate(0, 46, 2, position)

    def oscillate(self, start, stop, step, position):
        seq = list(range(start, stop + 1, step)) + list(
            range(stop - step, start - 1, -step)
        )
        if position:
            half_index = len(seq) // position
            return itertools.cycle(seq[half_index:] + seq[:half_index])
        return itertools.cycle(seq)

    def get_position(self):
        return self.x, self.y

    def get_image(self):
        return self.image

    def get_next_image(self):
        if not self.images:
            return None
        image = self.images[self.data["images"][self.current_index]]
        self.current_index = (self.current_index + 1) % len(self.data["images"])
        return image

    def update(self):
        self.x = next(self.x_values)
        self.y = next(self.y_values)
        self.image = self.get_next_image()
