import pyxel

from xmlui.core import XURect
from xmlui.ext.db import XUECSVArray
from orm.user_unit_state import UserUnitState

class Map:
    IMAGE_BANK = 2

    # ステージごとに初期化する
    def __init__(self, stage_no:int):
        self.tiles = XUECSVArray[int](f"assets/stage/stage{stage_no}_tile.csv")

    def load_image(self):
        pass

    def draw(self, screen_x:int, screen_y:int):
        for y,row in enumerate(self.tiles.rows):
            for x,tile_no in enumerate(row):
                rect = XURect(x*16 - screen_x, y*16 - screen_y, 16, 16)
                pyxel.blt(rect.x, rect.y, self.IMAGE_BANK, tile_no%16*16, tile_no//16*16, 16, 16, 0)
