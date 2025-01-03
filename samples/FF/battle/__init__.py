import pyxel

# バトル画面
from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUXFadeScene

import ui_common
from FF.battle import ui_status

class Battle(XUXFadeScene):
    def __init__(self):
        super().__init__(DebugXMLUI(pyxel.width, pyxel.height))

        # XMLの読み込み
        self.xmlui.load_template("assets/ui/common.xml")
        self.xmlui.load_template("assets/ui/battle.xml")
        self.xmlui.open("ui_battle")

        ui_common.ui_init(self.xmlui)
        ui_status.ui_init(self.xmlui)

    def closed(self):
        self.xmlui.close()

    def update(self):
        pass
        # if "start_buy" in self.xmlui.event.trg:
        #     ui_buy.init_buy_list(self.xmlui)

        # if "start_sell" in self.xmlui.event.trg:
        #     ui_sell.init_sell_list(self.xmlui)

    def draw(self):
        if self.xmlui.update_count < 16:
            self.xmlui.root.set_pos(256-self.xmlui.update_count*16, 0)
        else:
            self.xmlui.root.set_pos(0, 0)

        # UIの表示
        self.xmlui.draw()
