import pyxel

# タイトル画面
from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUXFadeScene

import ui_common
from title.ui import start,speed

class Title(XUXFadeScene):
    NEXT_SCENE_EVENT = "game_start"

    def __init__(self):
        super().__init__(DebugXMLUI(pyxel.width, pyxel.height), 0)

        # XMLの読み込み
        self.xmlui.load_template("assets/ui/title.xml")
        self.xmlui.load_template("assets/ui/common.xml")

        # ui初期化
        ui_common.ui_init(self.xmlui)
        start.ui_init(self.xmlui)
        speed.ui_init(self.xmlui)

        self.img = pyxel.Image.from_image(filename="assets/images/title.png")

        self.xmlui.open("game_title")  # game_title以下表示開始
        self.close()

    def closed(self):
        self.xmlui.close()

        # ゲーム画面へ
        from field import Field
        self.set_next_scene(Field())

    def update(self):
        if "start" in self.xmlui.event.trg:  # startが実行された
            self.close()

    def draw(self):
        # 背景絵
        pyxel.blt(0, 0, self.img, 0, 0, self.img.width, self.img.height)

        # UIの表示
        self.xmlui.draw()
