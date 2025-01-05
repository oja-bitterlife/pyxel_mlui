from xmlui.core import XUElem
from xmlui.ext.scene import XUEActItem

class BattleStart(XUEActItem):
    def __init__(self, elem:XUElem):
        super().__init__(8)
        self.elem = elem

    def waiting(self):
        self.elem.set_pos(256-self.count*32, 0)

    def action(self):
        self.elem.set_pos(0, 0)

