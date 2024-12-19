import pyxel
from xmlui.core import XURect
from xmlui.ext.timer import XUXTimer

# 車輪の再発明、するぞー
class XUXTilemap:
    DEFAULT_TILE_AREA = XURect(0, 0, 256, 256)

    def __init__(self, image_bank:int, tile_size=16, tile_area:XURect=DEFAULT_TILE_AREA) -> None:
        self.image_bank = image_bank
        self.tile_size = tile_size
        self.tile_area = tile_area

        # アニメーション用
        self.timer = None
        self.anim_no = 0  # アニメ時tile_no

        # 画像の左上の色をカラーキーとする
        self.color_key:int|None = pyxel.images[image_bank].pget(tile_area.x, tile_area.y)

    # anim_noをintervalごとに更新
    def _anim_time_func(self):
        self.anim_no += 1

    # アニメーション開始
    def start_anim(self, speed):
        self.anim_no = 0
        self.timer = XUXTimer(XUXTimer.Mode.INTERVAL, self._anim_time_func, speed)

    # アニメーション更新
    def update(self):
        if self.timer is not None:
            self.timer.update()

    # tile描画
    def draw_tile(self, x:int, y:int, tile_no:int, *, rotate:float|None=None, scale:float|None=None):
        tile_num = self.tile_area.w // self.tile_size
        u = self.tile_size * (tile_no % tile_num)
        v = self.tile_size * (tile_no // tile_num)
        pyxel.blt(x, y, self.image_bank, u, v, self.tile_size, self.tile_size, self.color_key, rotate=rotate, scale=scale)

    # tileアニメーション描画
    def draw_anim(self, x:int, y:int, anim:list[int], *, rotate:float|None=None, scale:float|None=None):
        tile_no = anim[self.anim_no % len(anim)]
        self.draw_tile(x, y, tile_no, rotate=rotate, scale=scale)
