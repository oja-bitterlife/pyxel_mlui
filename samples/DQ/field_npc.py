import pyxel

class NPC:
    npc = [
        # typ,   x, y, color, talk
        ["king", 8, 8, 2, "おうさままままままままままままままままままままままままままままままままままままままままままままままままままままままままままままま"],
        ["knight1", 8, 11, 3, "とびらのまえで　ひらく　をせんたく"],
        ["knight2", 10, 11, 3, "さきにおうさまのはなしをきくのだ"],
        ["knighg3", 12, 9, 3, "へいし　だよ\nげんじ　じゃないよ"],
    ]
    def draw(self, scroll_x, scroll_y):
        for npc in self.npc:
            pyxel.circ(npc[1]*16+scroll_x+7, npc[2]*16+scroll_y+7, 6, npc[3])

    # 会話チェック
    def check(self, block_x, block_y) -> str:
        for npc in self.npc:
            if npc[1] == block_x and npc[2] == block_y:
                return npc[4]
        return ""
