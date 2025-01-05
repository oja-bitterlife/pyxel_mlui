from xmlui.core import XUElem
from xmlui.ext.scene import XUEActItem,XUEFadeScene

class BattleData:
    def __init__(self, scene:XUEFadeScene):
        self.scene = scene

# バトル開始時スライド＆フェード
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

# コマンド待ち
class BattleCmdOpen(XUEActItem):
    def __init__(self, data:BattleData):
        super().__init__(16)
        self.data = data
        self.enemy_win = data.scene.xmlui.find_by_id("enemy_win")

    def action(self):
        self.cmd = self.enemy_win.open("menu")
