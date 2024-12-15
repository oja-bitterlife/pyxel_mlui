import dataclasses
import pyxel

from xmlui.core import XUTextUtil
from xmlui.lib import text
import field

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
        NPC_Data("king", 8, 8, 2, "{name}が　つぎのれべるになるには\nあと　{rem_exp}ポイントの\nけいけんが　ひつようじゃ\\pそれでは　ゆくがよい"),
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
    def check_talk(self, xmlui, player):
        talk = None
        if "start_talk_east" in xmlui.event.trg:
            talk = self._check(player.block_x+1, player.block_y)
        if "start_talk_west" in xmlui.event.trg:
            talk = self._check(player.block_x-1, player.block_y)
        if "start_talk_south" in xmlui.event.trg:
            talk = self._check(player.block_x, player.block_y+1)
        if "start_talk_north" in xmlui.event.trg:
            talk = self._check(player.block_x, player.block_y-1)

        # 会話が発生した
        if talk is not None:
            # メッセージウインドウを開く
            msg_win = xmlui.find_by_id("menu").open("message")
            msg_text = msg_win.find_by_tag("msg_text")
            if talk:
                text.MsgDQ.start_talk(msg_text, talk, field.param_db)  # talkでテキスト開始
            else:
                text.MsgDQ.start_system(msg_text, "だれもいません")  # systemメッセージ
