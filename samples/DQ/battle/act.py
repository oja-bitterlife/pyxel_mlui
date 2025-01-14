import random

from xmlui.core import XMLUI,XUWinInfo,XUTextUtil
from xmlui.ext.scene import XUEDebugActItem

from msg_dq import MsgDQ
from db import user_data, enemy_data

from battle.data import BattleData


# バトル用シーン遷移ベース
# #############################################################################
class BattleActItem(XUEDebugActItem):
    def __init__(self, xmlui:XMLUI[BattleData]):
        super().__init__()
        self.xmlui = xmlui

        self.msg_dq = MsgDQ(xmlui.find_by_id("msg_text"))

    @property
    def data(self) -> BattleData:
        return self.xmlui.data_ref


# 個々のAct
# #############################################################################
# メッセージ
# *****************************************************************************
# 設定済みメッセージ表示完了待機
class _MsgBase(BattleActItem):
    def __init__(self, xmlui:XMLUI[BattleData], text:str, params:dict):
        super().__init__(xmlui)
        self.text = text
        self.params = params

    # メッセージ表示完了待ち
    def waiting(self):
        if self.msg_dq.is_all_finish:
            self.finish()

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
        self.set_timeout(10)  # コマンド？を出すのにちょっと溜める

    def action(self):
        self.xmlui.open("menu")
        self.msg_dq.append_msg("コマンド？")
        self.act.add_act(CmdCheck(self.xmlui))

# コマンド選択待ち
class CmdCheck(BattleActItem):
    def waiting(self):
        if "attack" in self.xmlui.event.trg:
            # 選択されたらメニューは閉じる
            XUWinInfo(self.xmlui.find_by_id("menu")).setter.start_close()

            # ダメージ計算
            enemy_data.data["hit"] = XUTextUtil.format_zenkaku(random.randint(1, 100))

            self.act.add_act(
                PlayerMsg(self.xmlui, "{name}の　こうげき！", user_data.data),
                BlinkEffect(self.xmlui),
                PlayerMsg(self.xmlui, "{name}に　{hit}ポイントの\nダメージを　あたえた！", enemy_data.data),
                EnemyStart(self.xmlui))

            self.finish()

        if "run" in self.xmlui.event.trg:
            # 選択されたらメニューは閉じる
            XUWinInfo(self.xmlui.find_by_id("menu")).setter.start_close()

            # 逃げる
            self.act.add_act(
                PlayerMsg(self.xmlui, "{name}は　にげだした", user_data.data),
                RunWait(self.xmlui),
                PlayerMsg(self.xmlui, "しかし　まわりこまれて\nしまった!", {}),
                EnemyStart(self.xmlui))

            self.finish()

        if "spel" in self.xmlui.event.trg:
            # 選択されたらメニューは閉じる
            XUWinInfo(self.xmlui.find_by_id("menu")).setter.start_close()

            self.act.add_act(
                PlayerMsg(self.xmlui, "じゅもんを　おぼえていない", {}),
                CmdStart(self.xmlui))  # コマンド選択に戻る

            self.finish()

        if "tools" in self.xmlui.event.trg:
            self.xmlui.popup("under_construct")

# 敵の行動
# *****************************************************************************
class EnemyStart(BattleActItem):
    def init(self):
        self.set_timeout(10)  # コマンド？を出すのにちょっと溜める

    def action(self):
        # ダメージ計算
        damage = random.randint(5, 10)
        user_data.data["damage"] = XUTextUtil.format_zenkaku(damage)

        self.act.add_act(
            EnemyMsg(self.xmlui, "{name}の　こうげき！", enemy_data.data),
            DamageEffect(self.xmlui, damage),
            EnemyMsg(self.xmlui, "{name}は　{damage}ポイントの\nだめーじを　うけた", user_data.data))
        
        if user_data.hp > damage:
            self.act.add_act(CmdStart(self.xmlui))
        else:
            self.act.add_act(
                DeadWait(self.xmlui),
                PlayerMsg(self.xmlui, "{name}は　しんでしまった", user_data.data),
                ReturnKing(self.xmlui))

# ウェイト系
# *****************************************************************************
class DamageEffect(BattleActItem):
    def __init__(self, xmlui:XMLUI[BattleData], damage:int):
        super().__init__(xmlui)
        self.damage = damage
        self.set_timeout(15)  # 適当時間

    def waiting(self):
        # とりあえず画面揺らし
        self.data.sway_x = random.randint(-3, 3)
        self.data.sway_y = random.randint(-3, 3)

    def action(self):
        self.data.sway_x = 0
        self.data.sway_y = 0
        user_data.hp = max(0, user_data.hp - self.damage)

class BlinkEffect(BattleActItem):
    def init(self):
        self.set_timeout(10)  # エフェクトはないので適当待ち

    def waiting(self):
        self.data.blink = self.count % 2 < 1

    def action(self):
        self.blink = False

class RunWait(BattleActItem):
    def init(self):
        self.set_timeout(15)  # SE待ち

class DeadWait(BattleActItem):
    def init(self):
        self.set_timeout(15)  # SE待ち

# 死に戻り
# *****************************************************************************
class ReturnKing(BattleActItem):
    def init(self):
        self.set_timeout(45)  # ちょっと待機
    def action(self):
        self.xmlui.send_event("dead")
