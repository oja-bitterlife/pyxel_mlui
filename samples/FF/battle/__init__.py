import pyxel

# バトル画面
from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUXFadeScene

import ui_common
from FF.shop import ui_buy,ui_sell

class Battle(XUXFadeScene):
    def __init__(self):
        super().__init__(DebugXMLUI(pyxel.width, pyxel.height))

        # XMLの読み込み
        self.xmlui.load_template("assets/ui/common.xml")
        self.xmlui.load_template("assets/ui/battle.xml")
        self.xmlui.open("status_win")

        ui_common.ui_init(self.xmlui)
        # ui_shop.ui_init(self.template)
        # ui_buy.ui_init(self.template)
        # ui_sell.ui_init(self.template)

    def closed(self):
        self.xmlui.close()

    def update(self):
        if "start_buy" in self.xmlui.event.trg:
            ui_buy.init_buy_list(self.xmlui)

        if "start_sell" in self.xmlui.event.trg:
            ui_sell.init_sell_list(self.xmlui)

    def draw(self):
        # UIの表示
        self.xmlui.draw()
