import dataclasses
import pyxel

from xmlui.core import XUElem
from xmlui_ext import dq
import db

@dataclasses.dataclass
class NPC_Data:
    name: str
    x: int
    y: int
    color: int
    talk: str

class NPC:
    npc_data = [
        # typ,   x, y, color, talk
        NPC_Data("king", 8, 8, 2, "{name}が　つぎのれべるになるには\nあと　{rem_exp:.1f}ポイントの\nけいけんが　ひつようじゃ\\pでは　また　あおう！\nゆうしゃ　{name}よ！"),
        NPC_Data("knight1", 8, 11, 3, "とびらのまえで　とびら　をせんたくしてね"),
        NPC_Data("knight2", 10, 11, 3, "とびらのさきに　かいだんがある"),
        NPC_Data("knighg3", 12, 9, 3, "たからばこ？\nとっちゃだめだだよ？"),
    ]
    def draw(self, scroll_x, scroll_y):
        for data in self.npc_data:
            pyxel.circ(data.x*16+scroll_x+7, data.y*16+scroll_y+7, 6, data.color)

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
