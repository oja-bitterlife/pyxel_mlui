import pyxel

from xmlui.core import XUWinBase,XUElem
from xmlui_modules import dq

class BG:
    FLOOR = 2
    DOOR = 5
    STAIRS = 6

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

    def _draw_triangle(self, x, y, color):
        pyxel.tri(x, y+14, x+7, y+1, x+14, y+14, color)

    def draw(self, scroll_x, scroll_y):
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

    # とびらチェック
    def check_door(self, menu:XUElem, player):
        if "open_door" in menu.xmlui.event.trg:
            block_x, block_y = player.x//16, player.y//16
            door_x, door_y = -1, -1
            if self.blocks[block_y-1][block_x] == self.DOOR:
                door_x, door_y = block_x, block_y-1
            if self.blocks[block_y+1][block_x] == self.DOOR:
                door_x, door_y = block_x, block_y+1
            if self.blocks[block_y][block_x-1] == self.DOOR:
                door_x, door_y = block_x-1, block_y
            if self.blocks[block_y][block_x+1] == self.DOOR:
                door_x, door_y = block_x+1, block_y
            
            if door_x != -1:
                self.blocks[door_y][door_x] = 2
                XUWinBase(menu).start_close()
            else:
                msg_text = dq.MsgDQ(menu.open("message").find_by_id("msg_text"))
                msg_text.append_msg("とびらがない")  # systemメッセージ

    # 階段チェック
    def check_stairs(self, menu:XUElem, player):
        if "down_stairs" in menu.xmlui.event.trg:
            block_x, block_y = player.x//16, player.y//16
            if self.blocks[block_y][block_x] == self.STAIRS:
                XUWinBase(menu).start_close()
                menu.xmlui.on("start_battle")
            else:
                msg_text = dq.MsgDQ(menu.open("message").find_by_id("msg_text"))
                msg_text.append_msg("かいだんがない")  # systemメッセージ
