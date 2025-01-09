from xmlui.core import XUElem,XMLUI,XUEvent,XUSelectItem,XUWinBase
from xmlui.ext.scene import XUEActItem
from battle.data import BattleData

from db import user_data,enemy_data

# BattleDataを扱えるAct
class BattleDataAct(XUEActItem):
    def __init__(self, xmlui:XMLUI[BattleData]):
        super().__init__()
        self.xmlui = xmlui

    @property
    def battle_data(self):
        return self.xmlui.data_ref
    @property
    def scene(self):
        return self.xmlui.data_ref.scene

# コマンドメニュー下のAct
class BattleMenuAct(XUEActItem):
    def __init__(self, xmlui:XMLUI[BattleData], menu_win:XUElem):
        super().__init__()
        self.xmlui = xmlui
        self.menu_win = menu_win

    @property
    def battle_data(self):
        return self.xmlui.data_ref
    @property
    def scene(self):
        return self.xmlui.data_ref.scene


# バトルコマンド関係
# *****************************************************************************
# 初期化
# ---------------------------------------------------------
# バトル開始時スライド＆フェード
class BattleStart(BattleDataAct):
    def __init__(self, xmlui:XMLUI[BattleData]):
        super().__init__(xmlui)
        self.elem =self.xmlui.find_by_id("ui_battle")

        # enemy_name_winをownerから切り離す
        self.xmlui.find_by_id("enemy_name_win").set_attr("owner", "")

    def init(self):
        self.set_wait(8)

    def waiting(self):
        self.scene.alpha = 1-self.alpha  # fadeのコントロールをこっちで
        self.elem.set_pos(256-self.count*32, 0)

    def action(self):
        self.scene.alpha = 0
        self.elem.set_pos(0, 0)
        self.act.add_act(BattleTurnStart(self.xmlui))

# ターン開始
class BattleTurnStart(BattleDataAct):
    def init(self):
        self.set_wait(0)

    def action(self):
        self.battle_data.player_idx = 0
        self.battle_data.target = [0, 0, 0, 0]
        self.act.add_act(BattleCmdStart(self.xmlui))

# コマンド
# ---------------------------------------------------------
class BattleCmdStart(BattleDataAct):
    def __init__(self, xmlui:XMLUI[BattleData]):
        super().__init__(xmlui)
        self.set_wait(15)

    def action(self):
        self.act.add_act(BattleCmdSetup(self.xmlui, self.xmlui.find_by_id("enemy_name_win").open("menu")))

# メニューの設定とキャラ進め
class BattleCmdSetup(BattleMenuAct):
    def __init__(self, xmlui:XMLUI[BattleData], menu_win:XUElem):
        super().__init__(xmlui, menu_win)

    def init(self):
        # コマンドのリセット
        command = self.menu_win.find_by_id("command")
        command.remove_children()

        # 職業によってメニューを変える。とりあえずサンプルなので適当に
        job = {
            "heishi":["たたかう", "ぼうぎょ", "にげる", "アイテム"],
            "basaka":["たたかう", "まもらぬ", "ひかぬ", "かえりみぬ"],
            "yousei":["たたかう", "ぬすむ", "とんずら", "アイテム"],
            "majyo":["たたかう", "ぼうぎょ", "まほう", "アイテム"],
        }
        for action in job[self.battle_data.JOBS[self.battle_data.player_idx]]:
            # コマンド追加
            item = XUSelectItem(XUElem.new(self.scene.xmlui, "battle_action").set_text(action).set_attr("action", action))
            command.add_child(item)

        # キャラ移動開始(移動が終わったらあmove_dirを0にする)
        self.battle_data.player_move_dir[self.battle_data.player_idx] = -1
        self.battle_data.player_offset[self.battle_data.player_idx] = 0

    # キャラ移動待ち
    def waiting(self):
        if self.battle_data.player_move_dir[self.battle_data.player_idx] == 0:
            self.finish()

    def action(self):
        self.act.add_act(BattleCmdSel(self.xmlui, self.menu_win))

# コマンド選択
class BattleCmdSel(BattleMenuAct):
    def waiting(self):
        if self.scene.xmlui.event.check(XUEvent.Key.BTN_A):
            self.act.add_act(BattleCmdTargetSel(self.xmlui, self.menu_win))
            self.finish()

        # 取りやめ
        if self.xmlui.event.check(XUEvent.Key.BTN_B):
            self.act.add_act(BattleCmdCharaBack(self.xmlui, self.menu_win, self.battle_data.player_idx-1))
            self.finish()

# ターゲットの選択
class BattleCmdTargetSel(BattleMenuAct):
    def init(self):
        self.target_select = self.menu_win.open("target_select")
        self.battle_data.target[self.battle_data.player_idx] = 0  # 選択を戻す

        # ターゲット設定
        enemy_sel = self.target_select.find_by_id("enemy_sel")
        for i,enemy in enumerate(enemy_data.data):
            item = XUSelectItem(XUElem.new(self.scene.xmlui, "select_item"))
            item.set_pos(self.battle_data.enemy_rect[i].x, self.battle_data.enemy_rect[i].y)
            enemy_sel.add_child(item)

        player_sel = self.target_select.find_by_id("player_sel")
        for i,player in enumerate(user_data.player_data):
            item = XUSelectItem(XUElem.new(self.scene.xmlui, "select_item"))
            item.set_pos(self.battle_data.player_rect[i].x, self.battle_data.player_rect[i].y)
            player_sel.add_child(item)

    def waiting(self):
        # ターゲット決定
        if self.xmlui.event.check(XUEvent.Key.BTN_A):
            self.target_select.close()
            self.act.add_act(BattleCmdCharaBack(self.xmlui, self.menu_win, self.battle_data.player_idx+1))
            self.finish()

        # 取りやめ
        if self.xmlui.event.check(XUEvent.Key.BTN_B):
            self.target_select.close()
            self.act.add_act(BattleCmdSel(self.xmlui, self.menu_win))
            self.finish()


class BattleCmdCharaBack(BattleMenuAct):
    def __init__(self, xmlui: XMLUI[BattleData], menu_win: XUElem, next_idx:int):
        super().__init__(xmlui, menu_win)
        self.next_idx = min(max(next_idx, 0), len(user_data.player_data))

    def init(self):
        # 現在のキャラを引っ込める
        self.battle_data.player_move_dir[self.battle_data.player_idx] = 1

    # キャラ移動待ち
    def waiting(self):
        if self.battle_data.player_move_dir[self.battle_data.player_idx] == 0:
            # 全員のターゲットが決まった
            if self.next_idx >= len(user_data.player_data):
                self.act.add_act(BattleCmdClose(self.xmlui))
            # 残次のキャラのコマンド入力
            else:
                self.battle_data.player_idx = self.next_idx  # 操作キャラを進める
                self.act.add_act(BattleCmdSetup(self.xmlui, self.menu_win))

            self.finish()

class BattleCmdClose(BattleDataAct):
    def init(self):
        self.target_win = XUWinBase(self.xmlui.find_by_id("enemy_name_win"))
        self.target_win.start_close()

    def waiting(self):
        if self.target_win.removed:
            self.act.add_act(BattlePlay(self.xmlui))
            self.finish()

class BattlePlay(BattleDataAct):
    def waiting(self):
        pass
