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
        if not self.xmlui.exists_id("menu"):
            msg_text = self.xmlui.find_by_tag("msg_text")
            text.MsgDQ.start_system(msg_text, msg_text.text + "\n" + "コマンド？")

            # コマンド待ち開始
            self.xmlui.open("menu")
            
    def draw(self):
        # UIの描画(fieldとdefaultグループ)
        self.xmlui.draw()

# バトルUI
# *****************************************************************************
from ui_common import common_msg_text

def ui_init(template):
    # fieldグループ用デコレータを作る
    battle_select = select.Decorator(template)
    battle_text = text.Decorator(template)

    # バトルステータスタイトル
    # @field_text.label("status_title", "align", "valign")
    # def status_title(status_title:text.Label, event:XUEvent):
    #     pyxel.rect(status_title.area.x, status_title.area.y, status_title.area.w, status_title.area.w, 0)  # タイトルの下地

    #     # テキストは左寄せ
    #     x, y = status_title.aligned_pos(ui_theme.font.system)
    #     pyxel.text(x+1, y-1, param_db["name"], 7, ui_theme.font.system.font)

    @battle_text.msg_dq("msg_text")
    def msg_text(msg_text:text.MsgDQ, event:XUEvent):
        # メッセージ共通処理
        common_msg_text(msg_text, event)

        if msg_text.is_finish:
            return "finish_msg"
