import pyxel

# タイトル画面
from xmlui.core import XUEventItem
from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUEFadeScene
from db import enemy_data

import ui_common
from battle.ui import menu
from battle.act import BattleData,PlayerMsg,CmdStart


# バトルシーン
# #############################################################################
class Battle(XUEFadeScene):
    UI_TEMPLATE_BATTLE = "ui_battle"

    def __init__(self):
        super().__init__(DebugXMLUI(pyxel.width, pyxel.height))
        self.data = BattleData(self.xmlui)
        self.is_close = False

        # UIの読み込み
        self.template = self.xmlui.load_template("assets/ui/battle.xml")
        self.xmlui.load_template("assets/ui/common.xml")
        ui_common.ui_init(self.xmlui)
        menu.ui_init(self.xmlui)

        # バトル開始UI初期化
        self.battle = self.xmlui.open("battle")

        # 最初のAct
        self.add_act(
            PlayerMsg(self.data, "{name}が　あらわれた！", enemy_data.data),
            CmdStart(self.data))

        self.enemy_img = pyxel.Image.from_image(filename="assets/images/slime.png")
        self.enemy_bg = pyxel.Image.from_image(filename="assets/images/enemy_bg.png")
        self.field_img = pyxel.Image.from_image(filename="assets/images/field.png")


    def event(self, event:XUEventItem):
        match event:
            case "dead":
                self.fade_close()

    def closed(self):
        # 読みこんだUIの削除
        self.xmlui.close()

        # 王様の前に戻る
        from field import Field
        self.set_next_scene(Field())

    def draw(self):
        # 背景
        pyxel.blt(-16+self.data.sway_x, -16+self.data.sway_y, self.field_img, 0, 0, self.field_img.width, self.field_img.height)
        pyxel.blt(64+self.data.sway_x, 64+self.data.sway_y, self.enemy_bg, 0, 0, self.enemy_bg.width, self.enemy_bg.height)

        # 敵の絵
        if not self.data.blink:
            pyxel.blt(-70+self.data.sway_x, -70+self.data.sway_y, self.enemy_img, 0, 0, self.enemy_img.width, self.enemy_img.height, 0, scale=0.2)

        # UIの描画
        self.xmlui.draw()

