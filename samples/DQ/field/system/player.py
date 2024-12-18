import pyxel
from xmlui.lib.pyxel_util import PyxelInputInfo
from ui_common import xmlui

import field.system.npc as npc
import field.system.bg as bg

class Player:
    def __init__(self, x, y):
        self.x = x*16
        self.y = y*16
        self.move_x = 0
        self.move_y = 0

    def update(self, blocks:list[list[int]], npcs:list[npc.NPC_Data]):
        def _hitcheck(x, y):
            block_x = x // 16
            block_y = y // 16
            match blocks[block_y][block_x]:
                case bg.BG.FLOOR | bg.BG.STAIRS:
                    pass
                case _:
                    return False
            for npc in npcs:
                if npc.x == block_x and npc.y == block_y:
                    return False
            return True

        # キー入力チェック
        if not self.is_moving:
            input_info = PyxelInputInfo(xmlui)
            if input_info.input(pyxel.KEY_UP):
                if _hitcheck(self.x, self.y-16):
                    self.move_y = -16
            if input_info.input(pyxel.KEY_DOWN):
                if _hitcheck(self.x, self.y+16):
                    self.move_y = 16
            if input_info.input(pyxel.KEY_LEFT):
                if _hitcheck(self.x-16, self.y):
                    self.move_x = -16
            if input_info.input(pyxel.KEY_RIGHT):
                if _hitcheck(self.x+16, self.y):
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
        pyxel.circ(128+8, 127, 7, 12)

