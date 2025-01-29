import pyxel

from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUEFadeScene

from scenes.unit import Units
from scenes.tilemap import TileMap 

class Field(XUEFadeScene):
    def __init__(self):
        super().__init__(DebugXMLUI(pyxel.width, pyxel.height))

        self.stage = 1
        self.units = Units(self.stage)

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

        self.tilemap = TileMap(stage_no=1)

    def closed(self):
        self.xmlui.close()  # 読みこんだUIの削除


    def draw(self):
        self.units.draw(240, 0)
        self.tilemap.draw(240, 0)
