import pyxel

# タイトル画面
from xmlui.core import XMLUI,XUEvent,XUWinBase,XUTextBase,XURect
from xmlui.lib import select,text,input
from ui_common import ui_theme
from params import param_db

class Battle:
    UI_TEMPLATE_BATTLE = "ui_battle"

    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui

        # UIの読み込み
        self.template = self.xmlui.load_template("assets/ui/battle.xml")
        ui_init(self.template)

        # バトル開始UI初期化
        battle = self.xmlui.open("battle")
        battle.find_by_tag("msg_text").set_text("てきが　あらわれた")

    def __del__(self):
        # 読みこんだUIの削除
        self.template.remove()

    def update(self):
        pass
        # msg_text = self.xmlui.find_by_tag("msg_text")
        # if msg_text.anim.is_finish:
        #     text.MsgDQ.start_system(msg_text, msg_text.text + "\n" + "コマンド？")
            
    def draw(self):
        # UIの描画(fieldとdefaultグループ)
        self.xmlui.draw()

# バトルUI
# *****************************************************************************
from ui_common import draw_menu_cursor, draw_msg_cursor

def ui_init(template):
    # fieldグループ用デコレータを作る
    field_select = select.Decorator(template)
    field_text = text.Decorator(template)
    field_input = input.Decorator(template)


    # バトルステータスタイトル
    # @field_text.label("status_title", "align", "valign")
    # def status_title(status_title:text.Label, event:XUEvent):
    #     pyxel.rect(status_title.area.x, status_title.area.y, status_title.area.w, status_title.area.w, 0)  # タイトルの下地

    #     # テキストは左寄せ
    #     x, y = status_title.aligned_pos(ui_theme.font.system)
    #     pyxel.text(x+1, y-1, param_db["name"], 7, ui_theme.font.system.font)


    @field_input.dial("dial", "dial_item", "item_w")
    def dial(dial:input.Dial, event:XUEvent):
        input_def = ui_theme.input_def
        dial.change_by_event(event.trg, *input_def.CURSOR)

        for item in dial.digits:
            area = item.area
            pyxel.text(area.x, area.y, item.text, 7, ui_theme.font.system.font)

        # 確定
        if input_def.BTN_A in event.trg:
            yesno= dial.open("yes_no", "dial_yes_no")
            yesno.set_attr("value", dial.digits)

        # # 閉じる
        # if input_def.BTN_B in event.trg:
        #     dial.close_on()
