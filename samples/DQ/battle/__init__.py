import pyxel

# タイトル画面
from xmlui.core import XMLUI
from xmlui.ext.scene import XUXFadeScene,XUXAct
from db import enemy_data

from battle.ui.menu import ui_init
from battle.act import *

# 死に戻り先
import scenes

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

        self.enemy_img = pyxel.Image.from_image(filename="assets/images/slime.png")
        self.enemy_bg = pyxel.Image.from_image(filename="assets/images/enemy_bg.png")
        self.field_img = pyxel.Image.from_image(filename="assets/images/field.png")

    def closed(self):
        # 読みこんだUIの削除
        self.template.remove()
        self.set_next_scene(scenes.Field(self.xmlui))

    def update(self):
        self.act.update()

    def draw(self):
        # 背景
        pyxel.blt(-16+self.sway_x, -16+self.sway_y, self.field_img, 0, 0, self.field_img.width, self.field_img.height)
        pyxel.blt(64+self.sway_x, 64+self.sway_y, self.enemy_bg, 0, 0, self.enemy_bg.width, self.enemy_bg.height)

        # 敵の絵
        if not self.blink:
            pyxel.blt(-70+self.sway_x, -70+self.sway_y, self.enemy_img, 0, 0, self.enemy_img.width, self.enemy_img.height, 0, scale=0.2)

        # UIの描画
        self.xmlui.draw()

