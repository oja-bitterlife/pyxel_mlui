import pyxel
from xmlui.core import XURect

# 車輪の再発明、するぞー
class XUXTilemap:
    DEFAULT_TILE_AREA = XURect(0, 0, 256, 256)

    def __init__(self, image_bank:int, tile_size=16, tile_area:XURect=DEFAULT_TILE_AREA) -> None:
        self.image_bank = image_bank
        self.tile_size = tile_size
        self.tile_area = tile_area

        # 画像の左上の色をカラーキーとする
        self.color_key:int|None = pyxel.images[image_bank].pget(tile_area.x, tile_area.y)

    def draw_tile(self, x:int, y:int, tile_no:int, *, rotate:float|None=None, scale:float|None=None):
        tile_num = self.tile_area.w // self.tile_size
        u = self.tile_size * (tile_no % tile_num)
        v = self.tile_size * (tile_no // tile_num)
        pyxel.blt(x, y, self.image_bank, u, v, self.tile_size, self.tile_size, self.color_key, rotate=rotate, scale=scale)
