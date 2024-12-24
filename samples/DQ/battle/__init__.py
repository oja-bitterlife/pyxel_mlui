import pyxel

# タイトル画面
from xmlui.core import XMLUI
from xmlui.ext.scene import XUXFadeScene,XUXAct
from db import enemy_data

from battle.ui.menu import ui_init
from battle.act import *


# バトルシーン
# #############################################################################
class Battle(XUXFadeScene):
    UI_TEMPLATE_BATTLE = "ui_battle"

    def __init__(self, xmlui:XMLUI):
        super().__init__(xmlui)
        self.act = XUXAct()

        self.sway_x = 0
        self.sway_y = 0
        self.blink = False

        # UIの読み込み
        self.template = self.xmlui.load_template("assets/ui/battle.xml")
        ui_init(self.template)

        # バトル開始UI初期化
        self.battle = self.xmlui.open("battle")

        # 最初のAct
        self.act.add(
            PlayerMsg(self, "{name}が　あらわれた！", enemy_data.data),
            CmdStart(self))

        self.img = pyxel.Image.from_image(filename="assets/images/slime.png")

    def closed(self):
        # 読みこんだUIの削除
        self.template.remove()

    def update(self):
        self.act.update()

    def draw(self):
        # 敵の絵
        if not self.blink:
            pyxel.blt(-64+self.sway_x, -80+self.sway_y, self.img, 0, 0, self.img.width, self.img.height, scale=0.2)

        # UIの描画
        self.xmlui.draw()

