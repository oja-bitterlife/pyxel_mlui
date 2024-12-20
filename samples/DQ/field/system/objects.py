import pyxel
from xmlui.core import XURect
from xmlui.ext.tilemap import XUXTilemap

class Treasure:
    treasure = [
        # typ,        x, y, color, detai
        ["tresure1", 9, 9, 4, "やくそう"],
        ["tresure2", 10, 9, 4, "100G"],
        ["tresure3", 11, 6, 4, "10G"],
        ["door", 9, 12, 20, "10G"],
    ]
    def __init__(self):
        self.tile_anim = XUXTilemap(1)

    def draw(self, scroll_x, scroll_y):
        self.tile_anim.update()

        for treasure in self.treasure:
            self.tile_anim.draw(treasure[1]*16+scroll_x, treasure[2]*16+scroll_y, treasure[3])
