import json
import pyxel

from xmlui.core import XURect
from xmlui.ext.db import XUECSVArray
from orm.user_unit_state import UserUnitState


class TileSet:
    def __init__(self, json_path:str, img_path:str):
        self.img = pyxel.Image(256, 256)
        self.img.load(0, 0, img_path)
        with open(json_path) as f:
            self.tileset = json.load(f)
        
    def get_tile_rect(self, tile_no:int) -> XURect:
        tile = self.tileset["frames"][tile_no]["frame"]
        return XURect(tile["x"], tile["y"], tile["w"], tile["h"])

class TileMap:
    IMAGE_BANK = 2

    # ステージごとに初期化する
    def __init__(self, stage_no:int):
        self.tilemap = XUECSVArray(f"assets/stage/tilemap-{stage_no}.csv")
        self.tileset = TileSet(f"assets/stage/tileset-{stage_no}.json", f"assets/stage/tileset-{stage_no}.png")

    def draw(self, screen_x:int, screen_y:int):
        for y,row in enumerate(self.tilemap.rows):
            for x,tile_no in enumerate(row):
                tile_rect = self.tileset.get_tile_rect(tile_no)
                draw_rect = XURect(x*16 - screen_x, y*16 - screen_y, 16, 16)
                pyxel.blt(draw_rect.x, draw_rect.y, self.tileset.img, tile_rect.x, tile_rect.y, tile_rect.w, tile_rect.h, 0)
