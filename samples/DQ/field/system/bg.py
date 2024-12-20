import pyxel

from xmlui.core import XUWinBase,XUElem
from xmlui.ext.tilemap import XUXTilemap
from xmlui_modules import dq

class BG:
    FLOOR = 6
    STAIRS = 13
    DOOR = 1

    # 背景
    blocks = [
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7, 5, 5, 5, 5, 5, 5, 5, 5, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7, 5,15,15,15,15,15,15, 5, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7, 5,15, 5,15,15, 5,15, 5, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7, 5, 5, 5, 5, 5, 5, 5, 5, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7, 5, 5, 5, 5, 5, 5, 5, 5, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7, 5, 5, 5, 5, 5, 5, 5, 5, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7, 7, 7, 7, 5, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7, 5, 5, 5, 5, 5, 5, 5,13, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
    ]

    def __init__(self) -> None:
        self.tile_anim = XUXTilemap(1)

    def draw(self, scroll_x, scroll_y):
        # アニメ付き背景であれば更新
        self.tile_anim.update()

        # 地形描画
        for y,line in enumerate(self.blocks):
            for x,block in enumerate(line):
                self.tile_anim.draw(x*16+scroll_x, y*16+scroll_y, block)

    # とびらチェック
    # def check_door(self, menu:XUElem, player):
    #     if "open_door" in menu.xmlui.event.trg:
    #         block_x, block_y = player.x//16, player.y//16
    #         door_x, door_y = -1, -1
    #         if self.blocks[block_y-1][block_x] == self.DOOR:
    #             door_x, door_y = block_x, block_y-1
    #         if self.blocks[block_y+1][block_x] == self.DOOR:
    #             door_x, door_y = block_x, block_y+1
    #         if self.blocks[block_y][block_x-1] == self.DOOR:
    #             door_x, door_y = block_x-1, block_y
    #         if self.blocks[block_y][block_x+1] == self.DOOR:
    #             door_x, door_y = block_x+1, block_y
            
    #         if door_x != -1:
    #             self.blocks[door_y][door_x] = 2
    #             XUWinBase(menu).start_close()
    #         else:
    #             msg_text = dq.MsgDQ(menu.open("message").find_by_id("msg_text"))
    #             msg_text.append_msg("とびらがない")  # systemメッセージ

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
