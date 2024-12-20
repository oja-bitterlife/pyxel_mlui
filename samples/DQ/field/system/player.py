import pyxel
from typing import Callable,Any

from xmlui.core import XURect
from xmlui.ext.input import XUEInputInfo
from xmlui.ext.tilemap import XUXTilemap
from ui_common import xmlui

class Player:
    def __init__(self, x, y):
        self.x = x*16
        self.y = y*16
        self.move_x = 0
        self.move_y = 0

        self.tile = XUXTilemap(1)

    def update(self, hitcheck_funcs:list[Callable[[int,int],bool]]):
        # キー入力チェック
        if not self.is_moving:
            input_info = XUEInputInfo(xmlui)
            if input_info.input(pyxel.KEY_UP) and all([not hit(self.block_x, self.block_y-1) for hit in hitcheck_funcs]):
                self.move_y = -16
            if input_info.input(pyxel.KEY_DOWN) and all([not hit(self.block_x, self.block_y+1) for hit in hitcheck_funcs]):
                self.move_y = 16
            if input_info.input(pyxel.KEY_LEFT) and all([not hit(self.block_x-1, self.block_y) for hit in hitcheck_funcs]):
                self.move_x = -16
            if input_info.input(pyxel.KEY_RIGHT) and all([not hit(self.block_x+1, self.block_y) for hit in hitcheck_funcs]):
                self.move_x = 16

        # プレイヤの移動
        if self.move_x < 0:
            self.x -= 1
            self.move_x += 1
        if self.move_x > 0:
            self.x += 1
            self.move_x -= 1
        if self.move_y < 0:
            self.y -= 1
            self.move_y += 1
        if self.move_y > 0:
            self.y += 1
            self.move_y -= 1

    @property
    def is_moving(self) -> bool:
        return self.move_x != 0 or self.move_y != 0

    @property
    def block_x(self) -> int:
        return self.x // 16

    @property
    def block_y(self) -> int:
        return self.y // 16

    def draw(self):
        self.tile.update()
        self.tile.draw(127, 127-8, [16, 17])
