import pyxel
from xmlui.core import XURect
from xmlui.ext.timer import XUEInterval

# 車輪の再発明、するぞー
class XUETilemap(XUEInterval):
    # 定数
    DEFAULT_TILE_AREA = XURect(0, 0, 256, 256)  # イメージバンク全体を基本にすると横の数を気にしなくていい
    DEFAULT_TILE_SIZE = 16
    DEFAULT_ANIM_SPEED = 15  # 30FPSで15カウント=0.5秒

    def __init__(self, image_bank:int, tile_size=DEFAULT_TILE_SIZE, anim_speed=DEFAULT_ANIM_SPEED, tile_area:XURect=DEFAULT_TILE_AREA) -> None:
        super().__init__(anim_speed)
        self.anim_no = 0

        self.image_bank = image_bank
        self.tile_size = tile_size
        self.tile_area = tile_area

        # 画像の左上の色をカラーキーとする
        self.color_key:int|None = pyxel.images[image_bank].pget(tile_area.x, tile_area.y)

    # 表示No更新
    def action(self):
        self.anim_no += 1

    # tile描画
    def draw(self, x:int, y:int, tiles:int|list[int], *, rotate:float|None=None, scale:float|None=None):
        # tilesがリストならアニメーション表示
        if isinstance(tiles, list):
            tile_no = tiles[self.anim_no % len(tiles)]
        else:
            tile_no = tiles

        # イメージバンク上の座標を取得
        tile_w_num = self.tile_area.w // self.tile_size
        u = self.tile_size * (tile_no % tile_w_num)
        v = self.tile_size * (tile_no // tile_w_num)

        # タイル描画
        pyxel.blt(x, y, self.image_bank, u, v, self.tile_size, self.tile_size, self.color_key, rotate=rotate, scale=scale)

