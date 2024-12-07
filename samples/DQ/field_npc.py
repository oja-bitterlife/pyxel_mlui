import pyxel

# タイトル画面
from xmlui.xmlui_core import XUState,XUEvent
from ui_common import xmlui,draw_menu_cursor
from xmlui_pyxel import select,text,input,win


class NPC:
    npc = [
        ["king", 8, 8, 2, "おうさま"],
        ["knight1", 8, 11, 3, "兵士1"],
        ["knight2", 10, 11, 3, "兵士2"],
        ["knighg3", 12, 9, 3, "兵士3"],
    ]
    def draw(self, scroll_x, scroll_y):
        for npc in self.npc:
            pyxel.circ(npc[1]*16+scroll_x+7, npc[2]*16+scroll_y+7, 6, npc[3])
