import random

from xmlui.core import XUWinBase,XUTextUtil
from xmlui.ext.scene import XUXActItem,XUXActWait
from msg_dq import MsgDQ
from db import user_data, enemy_data

from DQ.battle import Battle

# バトル用シーン遷移ベース
# #############################################################################
class BattleActItem(XUXActItem):
    def __init__(self, battle:Battle):
        super().__init__()
        self.battle = battle
        self.xmlui = battle.xmlui

class BattleActWait(XUXActWait):
    def __init__(self, battle:Battle):
        super().__init__()
        self.battle = battle
        self.xmlui = battle.xmlui


# 個々のAct
# #############################################################################
# メッセージ
# *****************************************************************************
# 設定済みメッセージ表示完了待機
class _MsgBase(BattleActWait):
    def __init__(self, battle:Battle, text:str, params:dict):
        super().__init__(battle)
        self.text = text
        self.params = params

        # メッセージウインドウアクセス
        self.msg_dq = MsgDQ(self.xmlui.find_by_id("msg_text"))

    # メッセージ表示完了待ち
    def waiting(self):
        if self.msg_dq.is_all_finish:
            return True
        return False

# プレイヤメッセージ設定
class PlayerMsg(_MsgBase):
    def init(self):
        self.msg_dq.append_msg(self.text, self.params)

# 敵メッセージ設定
class EnemyMsg(_MsgBase):
    def init(self):
        self.msg_dq.append_enemy(self.text, self.params)  # enemey(インデントが違う)


# プレイヤの行動
# *****************************************************************************
# コマンド選択開始
class CmdStart(BattleActItem):
    def init(self):
        self.set_wait(10)  # コマンド？を出すのにちょっと溜める

    def action(self):
        self.xmlui.open("menu")
        self.msg_dq = MsgDQ(self.xmlui.find_by_id("msg_text"))
        self.msg_dq.append_msg("コマンド？")
        self.battle.act.add(CmdCheck(self.battle))

# コマンド選択待ち
class CmdCheck(BattleActWait):
    def waiting(self):
        if "attack" in self.xmlui.event.trg:
            # 選択されたらメニューは閉じる
            menu = MsgDQ(self.xmlui.find_by_id("menu"))
            XUWinBase(menu).start_close()

            # ダメージ計算
            enemy_data.data["hit"] = XUTextUtil.format_zenkaku(random.randint(1, 100))

            self.battle.act.add(
                PlayerMsg(self.battle, "{name}の　こうげき！", user_data.data),
                EffectWait(self.battle),
                PlayerMsg(self.battle, "{name}に　{hit}ポイントの\nダメージを　あたえた！", enemy_data.data),
                EnemyStart(self.battle))
            return True

        if "run" in self.xmlui.event.trg:
            # 逃げる
            self.battle.act.add(
                PlayerMsg(self.battle, "{name}は　にげだした", user_data.data),
                RunWait(self.battle),
                PlayerMsg(self.battle, "しかし まわりこまれて\nしまった!", {}),
                EnemyStart(self.battle))
            return True

        if "spel" in self.xmlui.event.trg:
            self.battle.act.add(
                PlayerMsg(self.battle, "じゅもんを　おぼえていない", {}),
                CmdStart(self.battle))  # コマンド選択に戻る
            return True

        if "tools" in self.xmlui.event.trg:
            self.battle.xmlui.popup("under_construct")

        return False

# 敵の行動
# *****************************************************************************
class EnemyStart(BattleActItem):
    def init(self):
        self.set_wait(10)  # コマンド？を出すのにちょっと溜める

    def action(self):
        # ダメージ計算
        user_data.data["damage"] = XUTextUtil.format_zenkaku(random.randint(1, 10))

        self.battle.act.add(
            EnemyMsg(self.battle, "{name}の　こうげき！", enemy_data.data),
            EffectWait(self.battle),
            EnemyMsg(self.battle, "{name}は　{damage}ポイントの\nだめーじを　うけた", user_data.data),
            CmdStart(self.battle))

# ウェイト系
# *****************************************************************************
class EffectWait(BattleActWait):
    def init(self):
        self.set_wait(20)  # エフェクトはないので適当待ち
    def waiting(self):
        # とりあえず画面揺らし
        global sway_x, sway_y
        sway_x = random.randint(-3, 3)
        sway_y = random.randint(-3, 3)
        return False

class RunWait(BattleActWait):
    def init(self):
        self.set_wait(20)  # SE待ち
