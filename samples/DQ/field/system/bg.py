from xmlui.core import XUElem
from xmlui.ext.tilemap import XUXTilemap

class BG:
    STAIRS = ST = 21
    FLOOR = FL =5

    # 背景
    blocks = [
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7,FL,FL,FL,FL,FL,FL,FL,FL, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7,FL,23,23,23,23,23,23,FL, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7,FL,23,FL,23,23,FL,23,FL, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7,FL,FL,FL,FL,FL,FL,FL,FL, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7,FL,FL,FL,FL,FL,FL,FL,FL, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7,FL,FL,FL,FL,FL,FL,FL,FL, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7, 7, 7, 7,FL, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6],
        [ 6, 6, 6, 6, 6, 7,FL,FL,FL,FL,FL,FL,FL,ST, 7, 6, 6, 6, 6, 6],
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

    def hit_check(self, block_x:int, block_y:int) -> bool:
        return self.blocks[block_y][block_x] != self.FLOOR

    # 階段チェック
    def check_stairs(self, menu:XUElem, block_x:int, block_y:int) -> bool:
        return self.blocks[block_y][block_x] == self.STAIRS
