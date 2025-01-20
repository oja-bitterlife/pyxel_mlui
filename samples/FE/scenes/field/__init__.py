import pyxel

from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUEFadeScene

from scenes.unit import UNITS

class Field(XUEFadeScene):
    def __init__(self):
        super().__init__(DebugXMLUI(pyxel.width, pyxel.height))

        self.stage = 1
        self.units = UNITS(self.stage)

        print(self.units)
        # UIの読み込み
        # self.xmlui.load_template("assets/ui/field.xml")
        # self.xmlui.load_template("assets/ui/common.xml")

        # ui_common.ui_init(self.xmlui)
        # msg_win.ui_init(self.xmlui)
        # menu.ui_init(self.xmlui)
        # talk_dir.ui_init(self.xmlui)
        # tools.ui_init(self.xmlui)

        # ゲーム本体(仮)
        # self.player = Player(self.xmlui, 10, 10)
        # self.bg = BG()
        # self.npc = NPCManager()
        # self.field_obj = FieldObj()

        # 画像読み込み
        # pyxel.images[1].load(0, 0, "assets/images/field_tile.png" )

    def closed(self):
        self.xmlui.close()  # 読みこんだUIの削除
