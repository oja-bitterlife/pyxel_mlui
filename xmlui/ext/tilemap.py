from typing import cast,Self
import json

import pyxel

from xmlui.core import XURect
from xmlui.ext.timer import XUEInterval
from xmlui.ext.db import XUECSVArray

# 車輪の再発明、するぞー
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
        self.tile_no = tile_no

        # 変更して使うもの
        self.anim_no = tile_no

    # ジェネリクスだけでは実現不可能だったので、ベースクラスを作ったあとconvertする
    @classmethod
    def from_base(cls, anim:"XUETileAnim") -> Self:
        return cls(anim.tileset, anim.tile_no, anim._count_max)

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
        self.tile_anims:dict[int, T] = {}
        for tile_no in set([tile for row in self.tilemap.rows for tile in row]):
            # 0は非表示
            if tile_no > 0:
                self.tile_anims[tile_no] = self.convert(XUETileAnim(tileset, tile_no, speed))

    # コレをオーバーライドして実際に使うTileAnimに変換する
    def convert(self, anim:XUETileAnim) -> T:
        return cast(T, anim)

    # アニメーション更新
    def update(self):
        # 全部更新
        for anim in self.tile_anims.values():
            anim.update()

    # 全体を描画
    def draw(self, screen_x:int, screen_y:int, *, rotate:float|None=None, scale:float|None=None):
        for y,row in enumerate(self.tilemap.rows):
            for x,tile_no in enumerate(row):
                # 0は非表示
                if tile_no > 0:
                    anim = self.tile_anims[tile_no]
                    draw_x = screen_x + x * self.tileset.size.w
                    draw_y = screen_y + y * self.tileset.size.h
                    anim.draw(draw_x, draw_y, rotate=rotate, scale=scale)
