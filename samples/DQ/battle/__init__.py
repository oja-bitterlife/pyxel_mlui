
# タイトル画面
from xmlui.core import XMLUI,XUWinBase,XUTextUtil
from xmlui.ext.scene import XUXScene,XUXAct,XUXActItem,XUXActWait
from msg_dq import MsgDQ
from db import user_data, enemy_data

from battle.ui.menu import ui_init
from battle.act import *


sway_x = 0
sway_y = 0

# バトルシーン
# #############################################################################
class Battle(XUXScene):
    UI_TEMPLATE_BATTLE = "ui_battle"

    def __init__(self, xmlui:XMLUI):
        super().__init__(xmlui)
        self.act = XUXAct()

        # UIの読み込み
        self.template = self.xmlui.load_template("assets/ui/battle.xml")
        ui_init(self.template)

        # バトル開始UI初期化
        self.battle = self.xmlui.open("battle")

        # 最初のAct
        self.act.add(
            PlayerMsg(self, "{name}が　あらわれた！", enemy_data.data),
            CmdStart(self))

    def closed(self):
        # 読みこんだUIの削除
        self.template.remove()

    def update(self):
        self.act.update()

    def draw(self):
        # UIの描画(fieldとdefaultグループ)
        self.xmlui.draw()

