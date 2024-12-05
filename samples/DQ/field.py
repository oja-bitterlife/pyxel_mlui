import pyxel

# タイトル画面
from xmlui_core import XUState,XUEvent
from ui_common import xmlui,draw_menu_cursor
from xmlui_pyxel import select,text,input

class Field:
    UI_TEMPLATE_FIELD = "ui_field"

    def __init__(self):
        xmlui.template_fromfile("assets/ui/field.xml", self.UI_TEMPLATE_FIELD)
        self.player_x = 10*16
        self.player_y = 10*16
        self.move_x = 0
        self.move_y = 0

    def __del__(self):
        xmlui.remove_template(self.UI_TEMPLATE_FIELD)

    def update(self):
        def _hitcheck(x, y):
            block_x = x // 16
            block_y = y // 16
            if self.blocks[block_y][block_x] != 2:
                return False
            for npc in self.npc:
                if npc[1] == block_x and npc[2] == block_y:
                    return False
            return True

        # キー入力チェック
        if self.move_x == 0 and self.move_y == 0:
            if pyxel.btn(pyxel.KEY_UP):
                if _hitcheck(self.player_x, self.player_y-16):
                    self.move_y = -16
            if pyxel.btn(pyxel.KEY_DOWN):
                if _hitcheck(self.player_x, self.player_y+16):
                    self.move_y = 16
            if pyxel.btn(pyxel.KEY_LEFT):
                if _hitcheck(self.player_x-16, self.player_y):
                    self.move_x = -16
            if pyxel.btn(pyxel.KEY_RIGHT):
                if _hitcheck(self.player_x+16, self.player_y):
                    self.move_x = 16

        # プレイヤの移動
        if self.move_x < 0:
            self.player_x -= 1
            self.move_x += 1
        if self.move_x > 0:
            self.player_x += 1
            self.move_x -= 1
        if self.move_y < 0:
            self.player_y -= 1
            self.move_y += 1
        if self.move_y > 0:
            self.player_y += 1
            self.move_y -= 1

        return None

    def draw(self):
        scroll_x = -self.player_x +160-32
        scroll_y = -self.player_y +160-32
        self.draw_bg(scroll_x, scroll_y)
        self.draw_npc(scroll_x, scroll_y)
        self.draw_treasure(scroll_x, scroll_y)
        self.draw_player()

        xmlui.check_input_on(pyxel.btn)
        xmlui.draw()

    def _draw_triangle(self, x, y, color):
        pyxel.tri(x, y+14, x+7, y+1, x+14, y+14, color)

    # 背景
    blocks = [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,2,2,2,2,2,2,2,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,4,4,4,4,4,4,2,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,4,2,4,4,2,4,2,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,2,2,2,2,2,2,2,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,2,2,2,2,2,2,2,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,2,2,2,2,2,2,2,3,1,1,1,1,1],
        [1,1,1,1,1,3,3,3,3,5,3,3,3,3,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,2,2,2,2,2,2,6,3,1,1,1,1,1],
        [1,1,1,1,1,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ]
    def draw_bg(self, scroll_x, scroll_y):
        for y,line in enumerate(self.blocks):
            for x,block in enumerate(line):
                match block:
                    case 1:
                        pyxel.rect(x*16+scroll_x, y*16+scroll_y, 15, 15, 13)
                    case 2:
                        pyxel.rect(x*16+scroll_x, y*16+scroll_y, 15, 15, 4)
                    case 3:
                        pyxel.rect(x*16+scroll_x, y*16+scroll_y, 15, 15, 15)
                    case 4:
                        pyxel.rect(x*16+scroll_x, y*16+scroll_y, 15, 15, 9)
                    case 5:
                        self._draw_triangle(x*16+scroll_x, y*16+scroll_y, 1)
                    case 6:
                        pyxel.rect(x*16+scroll_x, y*16+scroll_y, 15, 15, 1)

    npc = [
        ["king", 8, 8, "おうさま", 2],
        ["knight1", 8, 11, "兵士1", 3],
        ["knight2", 10, 11, "兵士2", 3],
        ["knighg3", 12, 9, "兵士3", 3],
    ]
    def draw_npc(self, scroll_x, scroll_y):
        for npc in self.npc:
            pyxel.circ(npc[1]*16+scroll_x+7, npc[2]*16+scroll_y+7, 6, npc[4])

    treasure = [
        ["tresure1", 9, 9, "やくそう", 10],
        ["tresure2", 10, 9, "100G", 10],
        ["tresure3", 11, 6, "10G", 10],
    ]
    def draw_treasure(self, scroll_x, scroll_y):
        for treasure in self.treasure:
            pyxel.rect(treasure[1]*16+scroll_x+1, treasure[2]*16+scroll_y+2, 14, 12, treasure[4])

    def draw_player(self):
        pyxel.circ(128+7, 128+7, 7, 12)


# 町の中
# ---------------------------------------------------------
