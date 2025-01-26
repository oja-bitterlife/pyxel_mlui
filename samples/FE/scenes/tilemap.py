from typing import cast,Any
import json
import pyxel

from xmlui.core import XURect
from xmlui.ext.db import XUECSVArray
from xmlui.ext.timer import XUEInterval

# マップセット管理
class XUETileSet:
    def __init__(self, img:pyxel.Image|int, tiles:list[XURect]):
        self.img = img
        self.tiles = tiles
        self.size = tiles[0].to_offset()

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

# ユニットやマップブロック1つに対応
class XUETileAnim(XUEInterval):
    DEFAULT_ANIM_SPEED = 15  # 30FPSで15カウント=0.5秒

    def __init__(self, tileset:XUETileSet, tile_no:int, speed:int=DEFAULT_ANIM_SPEED):
        super().__init__(speed)
        self.tileset = tileset

        # 初期値(変更しないもの)
        self._tileset = tileset
        self.init_tile_no = tile_no

        # 変更して使うもの
        self.anim_no = tile_no

    # 表示
    def draw(self, x:int, y:int, *, rotate:float|None=None, scale:float|None=None):
        uv_rect = self.tileset.tiles[self.anim_no]
        pyxel.blt(x, y, self.tileset.img, uv_rect.x, uv_rect.y, uv_rect.w, uv_rect.h, 0, rotate=rotate, scale=scale)

    # アニメーションするときはここでanim_noを切り替えるように
    # def action(self):

    # アニメーションするときはupdate(XUEIntervalで定義)を呼ぶように
    # def update(self):

# 並べて表示するもの。主にマップ用
class XUETileMap[T:XUETileAnim]:
    # ステージごとに初期化する
    def __init__(self, tileset:XUETileSet, tilemap_csv:str, speed:int=XUETileAnim.DEFAULT_ANIM_SPEED):
        super().__init__()
        self.tileset = tileset
        self.tilemap = XUECSVArray(tilemap_csv)

        # アニメするタイルオブジェクトを用意
        self.tile_anims:dict[int, XUETileAnim] = {}
        for tile_no in set([tile for row in self.tilemap.rows for tile in row]):
            # 0は非表示
            if tile_no > 0:
                self.tile_anims[tile_no] = XUETileAnim(tileset, tile_no, speed)

                # Type指定があればcastしておく
                if T is not Any:
                    self.tile_anims[tile_no] = cast(T, self.tile_anims[tile_no])

    def update(self):
        # 全部更新
        for anim in self.tile_anims.values():
            anim.update()

    def draw(self, screen_x:int, screen_y:int, *, rotate:float|None=None, scale:float|None=None):
        for y,row in enumerate(self.tilemap.rows):
            for x,tile_no in enumerate(row):
                # 0は非表示
                if tile_no > 0:
                    anim = self.tile_anims[tile_no]
                    draw_x = screen_x + x * self.tileset.size.w
                    draw_y = screen_y + y * self.tileset.size.h
                    anim.draw(draw_x, draw_y, rotate=rotate, scale=scale)

class TileMap(XUETileMap):
    # ステージごとに初期化する
    def __init__(self, stage_no:int):
        super().__init__(
            XUETileSet.from_aseprite(f"assets/stage/tileset-{stage_no}.png", f"assets/stage/tileset-{stage_no}.json"),
            f"assets/stage/tilemap-{stage_no}.csv")
