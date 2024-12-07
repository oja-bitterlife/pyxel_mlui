import pyxel

class Player:
    def __init__(self, x, y):
        self.x = x*16
        self.y = y*16
        self.move_x = 0
        self.move_y = 0

    def update(self, blocks, npcs):
        def _hitcheck(x, y):
            block_x = x // 16
            block_y = y // 16
            if blocks[block_y][block_x] != 2:
                return False
            for npc in npcs:
                if npc[1] == block_x and npc[2] == block_y:
                    return False
            return True

        # キー入力チェック
        if self.move_x == 0 and self.move_y == 0:
            if pyxel.btn(pyxel.KEY_UP):
                if _hitcheck(self.x, self.y-16):
                    self.move_y = -16
            if pyxel.btn(pyxel.KEY_DOWN):
                if _hitcheck(self.x, self.y+16):
                    self.move_y = 16
            if pyxel.btn(pyxel.KEY_LEFT):
                if _hitcheck(self.x-16, self.y):
                    self.move_x = -16
            if pyxel.btn(pyxel.KEY_RIGHT):
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

    def draw(self):
        pyxel.circ(128+8, 127, 7, 12)

