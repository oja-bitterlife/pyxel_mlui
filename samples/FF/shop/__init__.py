import pyxel

# タイトル画面
from xmlui.core import XMLUI,XUDebug
from xmlui.ext.scene import XUXFadeScene

from ui_common import ui_common_init
from FF.shop import ui_shop,ui_buy,ui_sell

class Shop(XUXFadeScene):
    def __init__(self):
        super().__init__(XMLUI(pyxel.width, pyxel.height, XUDebug.DEBUGLEVEL_LIB))

        # XMLの読み込み
        self.template = self.xmlui.load_template("assets/ui/shop.xml")
        self.xmlui.open("ui_shop")

        ui_common_init(self.xmlui)
        ui_shop.ui_init(self.template)
        ui_buy.ui_init(self.template)
        ui_sell.ui_init(self.template)

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
