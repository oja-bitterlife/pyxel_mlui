from xmlui.core import XUElem,XUEvent,XUSelectItem
from xmlui.ext.scene import XUEActItem,XUEFadeScene

class BattleData:
    JOBS = ["heishi", "basaka", "yousei", "majyo"]

    def __init__(self, scene:XUEFadeScene):
        self.scene = scene
        self.player_idx = -1
        self.player_move_dir = [0, 0, 0, 0]
        self.player_offset = [0, 0, 0, 0]

        self.enemy_selecting = False

# BattleDataを扱えるAct
class BattleDataAct(XUEActItem):
    def __init__(self, data:BattleData):
        super().__init__()
        self.data = data
        self.scene = data.scene

# バトル開始時スライド＆フェード
class BattleStart(XUEActItem):
    def __init__(self, data:BattleData):
        super().__init__(8)
        self.scene = data.scene
        self.elem = data.scene.xmlui.find_by_id("ui_battle")

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
        self.act.add_act(BattleCmdSetup(self.data, self.scene.xmlui.find_by_id("enemy_win").open("menu")))

# メニューの設定とキャラ進め
class BattleCmdSetup(BattleDataAct):
    def __init__(self, data:BattleData, menu_win:XUElem):
        super().__init__(data)
        self.menu_win = menu_win

        # 次のキャラへ
        self.data.player_idx += 1

        # 職業によってメニューを変える。とりあえずサンプルなので適当に
        command = menu_win.find_by_id("command")
        job = {
            "heishi":["たたかう", "ぼうぎょ", "にげる", "アイテム"],
            "basaka":["たたかう", "まもらぬ", "にげぬ", "アイテム"],
            "yousei":["たたかう", "ぬすむ", "とんずら", "アイテム"],
            "majyo":["たたかう", "ぼうぎょ", "まほう", "アイテム"],
        }
        for action in job[self.data.JOBS[self.data.player_idx]]:
            item = XUSelectItem(XUElem.new(self.scene.xmlui, "battle_action").set_text(action).set_attr("action", action))
            command.add_child(item)

        # キャラ移動開始(移動が終わったらあmove_dirを0にする)
        self.data.player_move_dir[self.data.player_idx] = -1
        self.data.player_offset[self.data.player_idx] = 0

    # キャラ移動待ち
    def waiting(self):
        if self.data.player_move_dir[self.data.player_idx] == 0:
            self.finish()

    def action(self):
        self.act.add_act(BattleCmdSel(self.data, self.menu_win))

# class BattleCharaMove(BattleDataAct):
#     def init(self):
#         # 現在のキャラを引っ込める
#         if self.data.player_idx >= 0:
#             self.data.player_move_dir[self.data.player_idx] = 1
#             self.data.player_offset[self.data.player_idx] = 0

# コマンド選択
class BattleCmdSel(BattleDataAct):
    def __init__(self, data:BattleData, menu_win:XUElem):
        super().__init__(data)
        self.menu_win = menu_win

    def waiting(self):
        if XUEvent.Key.BTN_A in self.scene.xmlui.event.trg:
            self.act.add_act(BattleCmdEnemySel(self.data, self.menu_win))
            self.finish()

# 敵の選択
class BattleCmdEnemySel(BattleDataAct):
    def __init__(self, data:BattleData, menu_win:XUElem):
        super().__init__(data)
        self.menu_win = menu_win
        self.enemy_selecting = True

    def waiting(self):
        self.finish()
