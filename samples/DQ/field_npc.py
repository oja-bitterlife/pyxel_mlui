import pyxel

from xmlui.lib import text
import field

class NPC:
    npc = [
        # typ,   x, y, color, talk
        ["king", 8, 8, 2, "おうさままままままままままままままままままままままままままままままままままままままままままままままままままままままままままままま"],
        ["knight1", 8, 11, 3, "とびらのまえで　とびら　をせんたくしてね"],
        ["knight2", 10, 11, 3, "へいし　だよ\nげんじ　じゃないよ"],
        ["knighg3", 12, 9, 3, "たからばこ？\nみじっそ…とっちゃだめだからね？"],
    ]
    def draw(self, scroll_x, scroll_y):
        for npc in self.npc:
            pyxel.circ(npc[1]*16+scroll_x+7, npc[2]*16+scroll_y+7, 6, npc[3])

    # 会話チェック
    def _check(self, block_x, block_y) -> str:
        for npc in self.npc:
            if npc[1] == block_x and npc[2] == block_y:
                return npc[4]
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
            msg_win = xmlui.find_by_id("menu").open(field.Field.UI_TEMPLATE_FIELD, "message")
            msg_text = msg_win.find_by_tag("msg_text")
            if talk:
                text.MsgDQ.start_talk(msg_text, talk)  # talkでテキスト開始
            else:
                text.MsgDQ.start_system(msg_text, "だれもいません")  # systemメッセージ
