import pyxel

# タイトル画面
from xmlui.core import XMLUI,XUDebug
from xmlui.ext.scene import XUXFadeScene

class Shop(XUXFadeScene):
    def __init__(self):
        super().__init__(XMLUI(pyxel.width, pyxel.height, XUDebug.DEBUGLEVEL_LIB))

        # XMLの読み込み
        self.template = self.xmlui.load_template("assets/ui/shop.xml")
        self.xmlui.open("ui_shop")

    def closed(self):
        self.template.remove()

    def update(self):
        pass

    def draw(self):
        # UIの表示
        self.xmlui.draw()
