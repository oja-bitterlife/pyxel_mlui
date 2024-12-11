import pyxel

# タイトル画面
from xmlui.core import XMLUI,XUEvent,XUWinBase
from xmlui.lib import select,text
from ui_common import ui_theme
from field_player import Player
from field_bg import BG
from field_npc import NPC
from field_treasure import Treasure

class Battle:
    UI_TEMPLATE_BATTLE = "ui_battle"

    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui

        # UIの読み込み
        self.xmlui.template_fromfile("assets/ui/field.xml", self.UI_TEMPLATE_BATTLE)
        ui_init(self.xmlui, self.UI_TEMPLATE_BATTLE)

    def __del__(self):
        # 読みこんだUIの削除
        self.xmlui.remove_template(self.UI_TEMPLATE_BATTLE)
        self.xmlui.remove_drawfunc(self.UI_TEMPLATE_BATTLE)

    def update(self):
        pass
            
    def draw(self):
        # UIの描画(fieldとdefaultグループ)
        self.xmlui.draw([])


# バトルUI
# *****************************************************************************
from ui_common import draw_menu_cursor, draw_msg_cursor, get_world_clip

def ui_init(xmlui, group):
    # fieldグループ用デコレータを作る
    field_select = select.Decorator(xmlui, group)
    field_text = text.Decorator(xmlui, group)
