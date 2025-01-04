import pyxel

# ショップ画面
from xmlui.core import XUEventItem
from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUEFadeScene

import ui_common
from FF.shop import ui_shop,ui_buy,ui_sell

class Shop(XUEFadeScene):
    def __init__(self):
        super().__init__(DebugXMLUI(pyxel.width, pyxel.height))

        # XMLの読み込み
        self.xmlui.load_template("assets/ui/common.xml")
        self.xmlui.load_template("assets/ui/shop.xml")
        self.xmlui.open("ui_shop")

        ui_common.ui_init(self.xmlui)
        ui_shop.ui_init(self.xmlui)
        ui_buy.ui_init(self.xmlui)
        ui_sell.ui_init(self.xmlui)

    def closed(self):
        from FF.battle import Battle
        self.set_next_scene(Battle())
        self.xmlui.close()

    def event(self, event:XUEventItem):
        match event:
            case "start_buy":
                ui_buy.init_buy_list(self.xmlui)
            case "start_sell":
                ui_sell.init_sell_list(self.xmlui)
            case "exit":
                self.fade_close()

    def draw(self):
        # UIの表示
        self.xmlui.draw()
