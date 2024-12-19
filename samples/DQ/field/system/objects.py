import pyxel
from xmlui.core import XURect
from xmlui.ext.tilemap import XUXTilemap

class Treasure:
    treasure = [
        # typ,        x, y, color, detai
        ["tresure1", 9, 9, (4,0), "やくそう"],
        ["tresure2", 10, 9, (4,0), "100G"],
        ["tresure3", 11, 6, (4,0), "10G"],
        ["door", 9, 12, (4,2), "10G"],
    ]
    def draw(self, scroll_x, scroll_y):
        tile = XUXTilemap(1, 16, XURect(0, 0, 128, 128))

        for treasure in self.treasure:
            tile_x,tile_y = treasure[3]
            tile.draw_tile(treasure[1]*16+scroll_x, treasure[2]*16+scroll_y, tile_x, tile_y)

            # pyxel.rect(treasure[1]*16+scroll_x+1, treasure[2]*16+scroll_y+2, 14, 12, treasure[3])
