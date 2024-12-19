import dataclasses
import pyxel

from xmlui.core import XUElem,XURect
from xmlui.ext.tilemap import XUXTilemap
from xmlui_modules import dq
import db

@dataclasses.dataclass
class NPC_Data:
    name: str
    x: int
    y: int
    anim_pat: list[tuple[int,int]]
    talk: str

    SPEED = 15

    def setup(self):
        self.tile = XUXTilemap(1, 16, XURect(0, 0, 128, 128))
        self.draw_count = 0

    def draw(self, offset_x:int, offset_y:int):
        self.draw_count += 1
        tile_x,tile_y = self.anim_pat[self.draw_count//self.SPEED % len(self.anim_pat)]
        self.tile.draw_tile(self.x*16 + offset_x, self.y*16 + offset_y, tile_x, tile_y)

class NPC:
    npc_data = [
        # typ,   x, y, color, talk
        NPC_Data("king", 8, 8, [(0,1), (1,1)], "{name}が　つぎのれべるになるには\nあと　{rem_exp}ポイントの\nけいけんが　ひつようじゃ\\pでは　また　あおう！\nゆうしゃ　{name}よ！"),
        NPC_Data("knight1", 8, 11, [(0,0), (1, 0)], "とびらのまえで　とびら　をせんたくしてね"),
        NPC_Data("knight2", 10, 11, [(0,0), (1, 0)], "とびらのさきに　かいだんがある"),
        NPC_Data("knighg3", 12, 9, [(0,0), (1, 0)], "たからばこ？\nとっちゃだめだだよ？"),
    ]
    def __init__(self):
        for npc in self.npc_data:
            npc.setup()

    def draw(self, scroll_x, scroll_y):
        for npc in self.npc_data:
            npc.draw(scroll_x-1, scroll_y-1)

    # 会話チェック
    def _check(self, block_x, block_y) -> str:
        for data in self.npc_data:
            if data.x == block_x and data.y == block_y:
                return data.talk
        return ""

    # 会話イベントチェック
    def check_talk(self, menu:XUElem, player):
        talk = None
        if "start_talk_east" in menu.xmlui.event.trg:
            talk = self._check(player.block_x+1, player.block_y)
        if "start_talk_west" in menu.xmlui.event.trg:
            talk = self._check(player.block_x-1, player.block_y)
        if "start_talk_south" in menu.xmlui.event.trg:
            talk = self._check(player.block_x, player.block_y+1)
        if "start_talk_north" in menu.xmlui.event.trg:
            talk = self._check(player.block_x, player.block_y-1)

        # 会話が発生した
        if talk is not None:
            # メッセージウインドウを開く
            msg_text = dq.MsgDQ(menu.open("message").find_by_id("msg_text"))
            if talk:
                msg_text.append_talk(talk, vars(db.user_data))  # talkでテキスト開始
            else:
                msg_text.append_msg("だれもいません")  # systemメッセージ
