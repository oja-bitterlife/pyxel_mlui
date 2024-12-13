import pyxel

# タイトル画面
from xmlui.core import XMLUI,XUEvent,XUWinBase,XUTextBase,XURect
from xmlui.lib import select,text
from ui_common import ui_theme
from params import param_db

class Battle:
    UI_TEMPLATE_BATTLE = "ui_battle"

    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui

        # UIの読み込み
        self.xmlui.template_fromfile("assets/ui/battle.xml", self.UI_TEMPLATE_BATTLE)
        ui_init(self.xmlui, self.UI_TEMPLATE_BATTLE)

        self.xmlui.open(self.UI_TEMPLATE_BATTLE, "battle")

    def __del__(self):
        # 読みこんだUIの削除
        self.xmlui.remove_template(self.UI_TEMPLATE_BATTLE)
        self.xmlui.remove_drawfunc(self.UI_TEMPLATE_BATTLE)

    def update(self):
        pass
            
    def draw(self):
        # UIの描画(fieldとdefaultグループ)
        self.xmlui.draw([self.UI_TEMPLATE_BATTLE])


# バトルUI
# *****************************************************************************
from ui_common import draw_menu_cursor, draw_msg_cursor

def ui_init(xmlui, group):
    # fieldグループ用デコレータを作る
    field_select = select.Decorator(xmlui, group)
    field_text = text.Decorator(xmlui, group)


    # バトルステータスタイトル
    @field_text.label("status_title", "align", "valign")
    def status_title(status_title:text.Label, event:XUEvent):
        pyxel.rect(status_title.area.x, status_title.area.y, status_title.area.w, status_title.area.w, 0)  # タイトルの下地

        # テキストは左寄せ
        x, y = status_title.aligned_pos(ui_theme.font.system)
        pyxel.text(x+1, y-1, param_db["name"], 7, ui_theme.font.system.font)


    # ステータス各種アイテム
    # ---------------------------------------------------------
    @field_text.label("status_item")
    def status_item(status_item:text.Label, event:XUEvent):
        system_font = ui_theme.font.system

        # 値の取得
        text = XUTextBase.dict_new(status_item.text, param_db)

        # テキストは右寄せ
        area = status_item.area
        x, y = XURect.align_offset(area.w, area.h, system_font.text_width(text) + 5, 0, status_item.align, status_item.valign)
        pyxel.text(area.x + x, area.y + y, text, 7, system_font.font)
