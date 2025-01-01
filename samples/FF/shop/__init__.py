import pyxel

# ショップ画面
from xmlui.core import XMLUI,XUDebug
from xmlui.ext.scene import XUXFadeScene

import ui_common
from FF.shop import ui_shop,ui_buy,ui_sell

class Shop(XUXFadeScene):
    def __init__(self):
        super().__init__(XMLUI(pyxel.width, pyxel.height, XUDebug.DEBUGLEVEL_LIB))

        # XMLの読み込み
        common_template = self.xmlui.load_template("assets/ui/common.xml")
        self.template = self.xmlui.load_template("assets/ui/shop.xml")
        self.xmlui.open("ui_shop")

        ui_common.ui_init(common_template)
        ui_shop.ui_init(self.template)
        ui_buy.ui_init(self.template)
        ui_sell.ui_init(self.template)

    def closed(self):
        from FF.battle import Battle
        self.set_next_scene(Battle())
        self.xmlui.close()

    def update(self):
        if "start_buy" in self.xmlui.event.trg:
            ui_buy.init_buy_list(self.xmlui)

        if "start_sell" in self.xmlui.event.trg:
            ui_sell.init_sell_list(self.xmlui)

        if "exit" in self.xmlui.event.trg:
            self.close()

    def draw(self):
        # UIの表示
        self.xmlui.draw()
