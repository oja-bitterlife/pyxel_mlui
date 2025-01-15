from xmlui.core import XUElem,XMLUI,XUEvent,XUWinInfo,XUSelectInfo
from xmlui.ext.scene import XUEDebugActItem

from db import user_data,enemy_data
from battle.data import BattleData,BattleDamage


# BattleDataを扱えるAct
class BattleDataAct(XUEDebugActItem):
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
class BattleMenuAct(XUEDebugActItem):
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

# リザルト系Act
class BattlePlayAct(XUEDebugActItem):
    def __init__(self, xmlui:XMLUI[BattleData], result:XUElem):
        super().__init__()
        self.xmlui = xmlui
        self.result = result

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

    def init(self):
        self.set_timeout(8)

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
        self.battle_data.player_idx = 0
        self.battle_data.target = [0, 0, 0, 0]
        self.act.add_act(BattleCmdStart(self.xmlui))

        # 2週目以降
        elem =self.xmlui.find_by_id("ui_battle")
        if not elem.exists_id("enemy_name_win"):
            # 閉じていたenemy_name_winを復活させる
            self.xmlui.open("enemy_name_win")

        self.finish()

# コマンド
# ---------------------------------------------------------
class BattleCmdStart(BattleDataAct):
    def init(self):
        self.set_timeout(15)

    def action(self):
        self.act.add_act(BattleCmdSetup(self.xmlui, self.xmlui.find_by_id("enemy_name_win").open("menu")))

# メニューの設定とキャラ進め
class BattleCmdSetup(BattleMenuAct):
    def init(self):
        # コマンドのリセット
        command = self.menu_win.find_by_id("command")
        command.remove_children()

        # 職業によってメニューを変える。とりあえずサンプルなので適当に
        job: dict[str, dict[str, bool]] = {
            "heishi":{"たたかう":True, "ぼうぎょ":True, "にげる":False, "アイテム":False},
            "basaka":{"たたかう":True, "まもらぬ":True, "ひかぬ":True, "こびぬ":True},
            "yousei":{"たたかう":True, "ぬすむ":False, "とんずら":False, "アイテム":False},
            "majyo":{"たたかう":True, "ぼうぎょ":True, "まほう":False, "アイテム":False},
        }
        for action,allow in job[self.battle_data.JOBS[self.battle_data.player_idx]].items():
            # コマンド追加
            item = (XUElem.new(self.scene.xmlui, "battle_action")
                .set_text(action)
                .set_attr("action", action)
                .set_attr("value", "" if allow else "工事中"))
            command.add_child(item)

        # キャラ移動開始(移動が終わったらmove_dirが0になってる)
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
        if self.scene.xmlui.event.check_trg(XUEvent.Key.BTN_A):
            menu = XUSelectInfo(self.menu_win.find_by_id("command"))
            if menu.selected_item.value == "工事中":
                self.scene.xmlui.popup("under_construct")
                self.act.add_act(BattleCmdDeny(self.xmlui, self.menu_win))
                self.finish()
                return

            # 選択コマンドを記録
            self.battle_data.command[self.battle_data.player_idx] = menu.selected_item.text
            if menu.selected_item.text == "ぼうぎょ":
                self.act.add_act(BattleCmdCharaBack(self.xmlui, self.menu_win, self.battle_data.player_idx+1))
            else:
                self.act.add_act(BattleCmdTargetSel(self.xmlui, self.menu_win))
            self.finish()

        # 取りやめ
        if self.xmlui.event.check_trg(XUEvent.Key.BTN_B):
            self.act.add_act(BattleCmdCharaBack(self.xmlui, self.menu_win, self.battle_data.player_idx-1))
            self.finish()

# 工事中
class BattleCmdDeny(BattleMenuAct):
    def waiting(self):
        if self.xmlui.event.check_trg(XUEvent.Key.BTN_A, XUEvent.Key.BTN_B):
            self.act.add_act(BattleCmdSel(self.xmlui, self.menu_win))
            self.finish()

# ターゲットの選択
class BattleCmdTargetSel(BattleMenuAct):
    def init(self):
        self.target_select = self.menu_win.open("target_select")
        self.battle_data.target[self.battle_data.player_idx] = 0  # 選択を戻す

        # ターゲット設定
        enemy_sel = self.target_select.find_by_id("enemy_sel")
        for i,enemy in enumerate(enemy_data.data):
            item = XUElem.new(self.scene.xmlui, "select_item")
            item.set_pos(self.battle_data.enemy_rect[i].x, self.battle_data.enemy_rect[i].y)
            enemy_sel.add_child(item)

        player_sel = self.target_select.find_by_id("player_sel")
        for i,player in enumerate(user_data.player_data):
            item = XUElem.new(self.scene.xmlui, "select_item")
            item.set_pos(self.battle_data.player_rect[i].x, self.battle_data.player_rect[i].y)
            player_sel.add_child(item)

    def waiting(self):
        # ターゲット決定
        if self.xmlui.event.check_trg(XUEvent.Key.BTN_A):
            self.target_select.close()
            self.act.add_act(BattleCmdCharaBack(self.xmlui, self.menu_win, self.battle_data.player_idx+1))
            self.finish()

        # 取りやめ
        if self.xmlui.event.check_trg(XUEvent.Key.BTN_B):
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
            self.battle_data.player_idx = self.next_idx  # 操作キャラを更新

            # 全員のターゲットが決まった
            if self.battle_data.player_idx >= len(user_data.player_data):
                self.act.add_act(BattleCmdClose(self.xmlui, self.menu_win))
            # 次のキャラのコマンド入力
            else:
                self.act.add_act(BattleCmdSetup(self.xmlui, self.menu_win))

            self.finish()

class BattleCmdClose(BattleMenuAct):
    def init(self):
        # enemy名(command_menuの上位)ごと閉じる
        self.target_win = XUWinInfo.find_parent_win(self.menu_win)
        self.target_win.setter.start_close()

    def waiting(self):
        if self.target_win.removed:
            self.act.add_act(BattlePlayStart(self.xmlui, self.xmlui.open("result")))
            self.finish()

# アクション
# ---------------------------------------------------------
class BattlePlayStart(BattlePlayAct):
    # プレイヤ側を先に
    def init(self):
        self.battle_data.player_idx = -1
        self.battle_data.enemy_idx = -1
        self.act.add_act(BattlePlayUnitSelect(self.xmlui, self.result))
        self.finish()

# プレイヤ・敵のアクション開始
class BattlePlayUnitSelect(BattlePlayAct):
    def init(self):
        # 次のプレイヤへ
        self.battle_data.player_idx += 1

        # プレイヤが完了していれば敵を進める
        if self.battle_data.player_idx >= len(user_data.player_data):
            self.battle_data.enemy_idx += 1

            # 敵も終了していたら仕切り直し
            if self.battle_data.enemy_idx >= len(enemy_data.data):
                self.result.close()
                self.act.add_act(BattleTurnStart(self.xmlui))
                self.finish()
                return

        self.result.open("result_who")  # キャラ名表示
        self.battle_data.damage.clear()
        self.set_timeout(2)

    def action(self):
        # プレイヤーの行動
        if self.battle_data.is_player_turn:
            self.act.add_act(BattlePlayPlayerAction(self.xmlui, self.result))
        # 敵の行動
        else:
            self.act.add_act(BattlePlayEnemyAction(self.xmlui, self.result))
        self.finish()

# プレイヤ専用アクション
# ---------------------------------------------------------
class BattlePlayPlayerAction(BattlePlayAct):
    def init(self):
        # ぼうぎょ
        if self.battle_data.command[self.battle_data.player_idx] == "ぼうぎょ":
            self.act.add_act(
                BattlePlayFront(self.xmlui, self.result),  # 前に出るのを待って
                BattlePlayDeffence(self.xmlui, self.result),  # ぼうぎょを表示
                BattlePlayBack(self.xmlui, self.result),  # 後ろにさがって
                BattlePlayCloseWin(self.xmlui, self.result),  # ウインドウを閉じて
                BattlePlayUnitSelect(self.xmlui, self.result))  # 次のキャラへ
        # こうげき
        else:
            self.result.open("result_target")  # ターゲット表示
            self.act.add_act(
                BattlePlayFront(self.xmlui, self.result),  # 前に出るのを待って
                BattlePlayPlayerAttack(self.xmlui, self.result),  # 攻撃エフェクト
                BattlePlayBack(self.xmlui, self.result),  # 後ろにさがって
                BattlePlayHit(self.xmlui, self.result),  # ヒット数表示
                BattlePlayDamage(self.xmlui, self.result),  # ダメージ表示
                BattlePlayCloseWin(self.xmlui, self.result),  # ウインドウを閉じて
                BattlePlayUnitSelect(self.xmlui, self.result))  # 次のキャラへ

        self.finish()

class BattlePlayFront(BattlePlayAct):
    def init(self):
        # 移動開始
        self.battle_data.player_move_dir[self.battle_data.player_idx] = -1
        self.battle_data.player_offset[self.battle_data.player_idx] = 0

    # キャラ移動待ち
    def waiting(self):
        if self.battle_data.player_move_dir[self.battle_data.player_idx] == 0:
            self.finish()

class BattlePlayBack(BattlePlayAct):
    def init(self):
        self.battle_data.player_move_dir[self.battle_data.player_idx] = 1  # 後ろにさがる

    # キャラ移動待ち
    def waiting(self):
        if self.battle_data.player_move_dir[self.battle_data.player_idx] == 0:
            self.finish()

class BattlePlayPlayerAttack(BattlePlayAct):
    def init(self):
        # 攻撃エフェクト再生
        self.set_timeout(10)

        # ダメージ設定
        import random
        target = self.battle_data.target[self.battle_data.player_idx]
        self.battle_data.damage.append(BattleDamage(random.randint(0, 9999), random.randint(1, 99), target))

    # 攻撃エフェクト終了待ち

class BattlePlayDeffence(BattlePlayAct):
    def init(self):
        self.result.open("result_action")  # 防御表示
        self.set_timeout(15)

# プレイヤ・敵・共通アクション
# ---------------------------------------------------------
# ヒット数表示開始
class BattlePlayHit(BattlePlayAct):
    def init(self):
        self.result.open("result_action")
        self.set_timeout(2)

# ダメージ表示
class BattlePlayDamage(BattlePlayAct):
    # ダメージ表示完了待ち
    def waiting(self):
        if all([damage.is_finish for damage in self.battle_data.damage]):
            self.finish()

    # ダメージの反映
    def action(self):
        for damage in self.battle_data.damage:
            if damage.target < 0:
                target = abs(damage.target) - 1
                user_data.set_hp(target, user_data.player_data[target]["hp"] - damage.damage)


# サブウインドウを1つずつ閉じる
class BattlePlayCloseWin(BattlePlayAct):
    def waiting(self):
        children = [child for child in self.result.children if XUWinInfo.is_win(child)]
        if not children:
            self.finish()
        else:
            win = XUWinInfo(children[-1])
            if not win.is_closing:
                win.setter.start_close()

# 敵アクション
# ---------------------------------------------------------
class BattlePlayEnemyAction(BattlePlayAct):
    def init(self):
        # こうげき
        self.act.add_act(
            BattlePlayEnemyFlush(self.xmlui, self.result),  # flushさせて
            BattlePlayHit(self.xmlui, self.result),  # ヒット数表示
            BattlePlayDamage(self.xmlui, self.result),  # ダメージ表示
            BattlePlayCloseWin(self.xmlui, self.result),  # ウインドウを閉じて
            BattlePlayUnitSelect(self.xmlui, self.result))  # 次のキャラへ
        self.finish()

class BattlePlayEnemyFlush(BattlePlayAct):
    def init(self):
        self.result.open("result_target")  # ターゲット表示

        # ダメージ設定
        import random
        target = random.randint(0, len(user_data.player_data)-1)
        damage = random.randint(1, 3)
        hit = 1
        if user_data.player_data[target]["hp"] <= damage:
            # 死にそうになってたらミスするように
            damage = 0
            hit = 0
        self.battle_data.damage.append(BattleDamage(damage, hit, -target-1))

        # 攻撃エフェクト再生
        self.set_timeout(10)

