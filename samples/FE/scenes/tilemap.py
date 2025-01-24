import json
import pyxel

from xmlui.core import XURect
from xmlui.ext.db import XUECSVArray
from xmlui.ext.timer import XUEInterval

class XUETileSet:
    def __init__(self, img:pyxel.Image|int, tiles:list[XURect]):
        self.img = img
        self.tiles = tiles

    @classmethod
    def from_aseprite(cls, img_path:str, json_path:str) -> "XUETileSet":
        # imageをload
        img = pyxel.Image(256, 256)
        img.load(0, 0, img_path)

        # tileset情報を取得
        tiles = []
        with open(json_path) as f:
            tileset = json.load(f)
            for tile in tileset["frames"]:
                frame = tile["frame"]
                tiles.append(XURect(frame["x"], frame["y"], frame["w"], frame["h"]))

        # tilesetを作成
        return XUETileSet(img, tiles)

class XUETileMap(XUEInterval):
    DEFAULT_ANIM_SPEED = 15  # 30FPSで15カウント=0.5秒
    DEFAULT_BLOCK_SIZE = 16
    DEFAULT_COLOR_KEY = 0

    # ステージごとに初期化する
    def __init__(self, tileset:XUETileSet, tilemap_csv:str, speed:int=DEFAULT_ANIM_SPEED, block_size:int=DEFAULT_BLOCK_SIZE, color_key=DEFAULT_COLOR_KEY):
        super().__init__(speed)
        self.tilemap = XUECSVArray(tilemap_csv)
        self.tileset = tileset

        self.block_size = block_size
        self.color_key = color_key

        self.anim_no = 0

        self.tile_offset_u = 0
        self.tile_offset_v = 0

    def draw(self, screen_x:int, screen_y:int, *, rotate:float|None=None, scale:float|None=None):
        for y,row in enumerate(self.tilemap.rows):
            for x,tile_no in enumerate(row):
                # 0は非表示
                if tile_no > 0:
                    tile_rect = self.tileset.tiles[tile_no]
                    tile_rect.x += self.tile_offset_u
                    tile_rect.y += self.tile_offset_v
                    draw_x = x*self.block_size - screen_x
                    draw_y = y*self.block_size - screen_y
                    pyxel.blt(draw_x, draw_y, self.tileset.img, tile_rect.x, tile_rect.y, tile_rect.w, tile_rect.h, self.color_key, rotate=rotate, scale=scale)


    # override: 一定時間ごとにanimを切り替え
    def action(self):
        self.change_anim(self.anim_no + 1)

    def change_anim(self, anim_no:int):
        self.anim_no = anim_no
        self.anim_changed()

    # アクションが切り替わったときに呼ばれる
    # 継承側で表示uv切り替えを行う
    def anim_changed(self):
        pass


class TileMap(XUETileMap):
    # ステージごとに初期化する
    def __init__(self, stage_no:int):
        super().__init__(
            XUETileSet.from_aseprite(f"assets/stage/tileset-{stage_no}.png", f"assets/stage/tileset-{stage_no}.json"),
            f"assets/stage/tilemap-{stage_no}.csv")
