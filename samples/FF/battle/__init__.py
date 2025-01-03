import pyxel

# バトル画面
from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUXFadeScene

import ui_common
from FF.battle import ui_status
from db import enemy_data,user_data

class Battle(XUXFadeScene):
    def __init__(self):
        super().__init__(DebugXMLUI(pyxel.width, pyxel.height))

        # XMLの読み込み
        self.xmlui.load_template("assets/ui/common.xml")
        self.xmlui.load_template("assets/ui/battle.xml")
        self.xmlui.open("ui_battle")

        ui_common.ui_init(self.xmlui)
        ui_status.ui_init(self.xmlui)

        self.enemy_img = pyxel.Image.from_image(filename="assets/images/fantasy_goblin.png")
        self.bg_img = pyxel.Image.from_image(filename="assets/images/bg.png")
        self.player_imgs = [
            pyxel.Image.from_image(filename="assets/images/heishi.png"),
            pyxel.Image.from_image(filename="assets/images/basaka.png"),
            pyxel.Image.from_image(filename="assets/images/yousei.png"),
            pyxel.Image.from_image(filename="assets/images/majyo.png"),
        ]

    def closed(self):
        self.xmlui.close()

    def update(self):
        pass
        # if "start_buy" in self.xmlui.event.trg:
        #     ui_buy.init_buy_list(self.xmlui)

        # if "start_sell" in self.xmlui.event.trg:
        #     ui_sell.init_sell_list(self.xmlui)

    def draw(self):
        # 背景の表示
        pyxel.blt(0, 0, self.bg_img, 0, 0, 256, 40, 0)

        # 敵の表示
        for data in enemy_data.data:
            x = 24+data["x"]*48
            y = 56+data["y"]*56
            pyxel.blt(x, y, self.enemy_img, 0, 0, 64, 64, 0)

        # プレイヤの表示
        for i,data in enumerate(user_data.player_data):
            img = self.player_imgs[i]
            x = 256-48 - (1-data["fb"])*16
            pyxel.blt(x, 40+i*32, img, 0, 0, 64, 64, 0)

        # UIの表示
        if self.xmlui.update_count < 16:
            self.xmlui.root.set_pos(256-self.xmlui.update_count*16, 0)
        else:
            self.xmlui.root.set_pos(0, 0)
        self.xmlui.draw()
