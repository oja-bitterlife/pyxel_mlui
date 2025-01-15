import pyxel

# ショップ画面
from xmlui.core import XUEventItem
from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUEFadeScene

import ui_common
from shop import ui_shop,ui_buy,ui_sell

class Shop(XUEFadeScene):
    def __init__(self):
        xmlui = DebugXMLUI(pyxel.width, pyxel.height)
        super().__init__(xmlui)

        # XMLの読み込み
        self.xmlui.load_template("assets/ui/common.xml")
        self.xmlui.load_template("assets/ui/shop.xml")
        self.xmlui.open("ui_shop")

        ui_common.ui_init(xmlui)
        ui_shop.ui_init(xmlui)
        ui_buy.ui_init(xmlui)
        ui_sell.ui_init(xmlui)

        # プレイヤの画像
        self.player_imgs = [
            pyxel.Image.from_image(filename="assets/images/heishi.png"),
            pyxel.Image.from_image(filename="assets/images/basaka.png"),
            pyxel.Image.from_image(filename="assets/images/yousei.png"),
            pyxel.Image.from_image(filename="assets/images/majyo.png"),
        ]

    def closed(self):
        from battle import Battle
        self.set_next_scene(Battle())
        self.xmlui.close()

    def event(self, event:XUEventItem):
        match event.name:
            case "start_buy":
                ui_buy.init_buy_list(self.xmlui)
            case "start_sell":
                ui_sell.init_sell_list(self.xmlui)
            case "shop_exit":
                self.close()

    def draw(self):
        # プレイヤの表示
        if self.xmlui.exists_id("buy_menu"):
            for i,img in enumerate(self.player_imgs):
                pyxel.blt(204, 80+i*38, img, 0, 0, img.width, img.height, 0)

        # UIの表示
        self.xmlui.draw()
