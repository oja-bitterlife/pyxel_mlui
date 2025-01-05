from xmlui.core import XUElem,XUSelectItem
from xmlui.ext.scene import XUEActItem,XUEFadeScene

class BattleData:
    JOBS = ["heishi", "basaka", "yousei", "majyo"]

    def __init__(self, scene:XUEFadeScene):
        self.scene = scene
        self.player_idx = -1

    @property
    def player_job(self):
        return self.JOBS[self.player_idx]

# BattleDataを扱えるAct
class BattleDataAct(XUEActItem):
    def __init__(self, data:BattleData):
        super().__init__()
        self.data = data
        self.scene = data.scene

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
class BattleCmdStart(BattleDataAct):
    def init(self):
        self.set_wait(16)

    def action(self):
        self.data.player_idx = 0
        self.act.add_act(BattleCmd(self.data, self.scene.xmlui.find_by_id("enemy_win").open("menu")))

class BattleCmd(BattleDataAct):
    def __init__(self, data:BattleData, menu_win:XUElem):
        super().__init__(data)
        self.menu_win = menu_win
        self.command = menu_win.find_by_id("command")

        # 職業によってメニューを変える。とりあえずサンプルなので適当に
        job = {
            "heishi":["たたかう", "ぼうぎょ", "にげる", "アイテム"],
            "basaka":["たたかう", "まもらぬ", "にげぬ", "アイテム"],
            "yousei":["たたかう", "ぬすむ", "とんずら", "アイテム"],
            "majyo":["たたかう", "ぼうぎょ", "まほう", "アイテム"],
        }

        for action in job[self.data.player_job]:
            item = XUSelectItem(XUElem.new(self.scene.xmlui, "battle_action").set_text(action).set_attr("action", action))
            self.command.add_child(item)

    def waiting(self):
        pass
