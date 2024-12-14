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
        self.template = self.xmlui.load_template("assets/ui/battle.xml")
        ui_init(self.xmlui, self.UI_TEMPLATE_BATTLE)

        # バトル開始UI初期化
        battle = self.xmlui.open("battle")
        battle.find_by_tag("msg_text").set_text("てきが　あらわれた")

    def __del__(self):
        # 読みこんだUIの削除
        self.template.remove()
        self.xmlui.remove_drawfunc(self.UI_TEMPLATE_BATTLE)

    def update(self):
        msg_dq = text.MsgDQ(self.xmlui.find_by_tag("msg_text"), "page_line_num", "wrap")
        if msg_dq.anim.is_finish:
            msg_dq.start_system(msg_dq.text + "\n" + "コマンド？")
            
    def draw(self):
        # UIの描画(fieldとdefaultグループ)
        self.xmlui.draw([])
#        self.xmlui.draw([self.UI_TEMPLATE_BATTLE])

# バトルUI
# *****************************************************************************
from ui_common import draw_menu_cursor, draw_msg_cursor

def ui_init(xmlui, group):
    # fieldグループ用デコレータを作る
    field_select = select.Decorator(xmlui, group)
    field_text = text.Decorator(xmlui, group)


    # バトルステータスタイトル
    # @field_text.label("status_title", "align", "valign")
    # def status_title(status_title:text.Label, event:XUEvent):
    #     pyxel.rect(status_title.area.x, status_title.area.y, status_title.area.w, status_title.area.w, 0)  # タイトルの下地

    #     # テキストは左寄せ
    #     x, y = status_title.aligned_pos(ui_theme.font.system)
    #     pyxel.text(x+1, y-1, param_db["name"], 7, ui_theme.font.system.font)

