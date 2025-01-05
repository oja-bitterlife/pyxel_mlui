from xmlui.core import XUElem
from xmlui.ext.scene import XUEActItem,XUEFadeScene

class BattleStart(XUEActItem):
    def __init__(self, scene:XUEFadeScene):
        super().__init__(8)
        self.scene = scene
        self.elem = scene.xmlui.find_by_id("ui_battle")

    def waiting(self):
        self.scene.alpha = 1-self.alpha  # fadeのコントロールをこっちで
        self.elem.set_pos(256-self.count*32, 0)

    def action(self):
        self.scene.alpha = 0
        self.elem.set_pos(0, 0)

