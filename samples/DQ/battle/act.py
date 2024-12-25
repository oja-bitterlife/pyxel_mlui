import random

from xmlui.core import XMLUI,XUWinBase,XUTextUtil
from xmlui.ext.scene import XUXAct,XUXActItem,XUXActWait
from msg_dq import MsgDQ
from db import user_data, enemy_data


# バトル用シーン遷移ベース
# #############################################################################
class BattleAct(XUXAct):
    def __init__(self, xmlui:XMLUI):
        super().__init__()
        self.xmlui = xmlui

        # データ受け渡しをここでやってみる
        self.sway_x = 0
        self.sway_y = 0
        self.blink = False

        self.is_dead = False


class BattleActItem(XUXActItem[BattleAct]):
    @property
    def xmlui(self):
        return self.act.xmlui

    @property
    def msg_dq(self):
        return MsgDQ(self.act.xmlui.find_by_id("msg_text"))

class BattleActWait(XUXActWait[BattleAct]):
    @property
    def xmlui(self):
        return self.act.xmlui

    @property
    def msg_dq(self):
        return MsgDQ(self.act.xmlui.find_by_id("msg_text"))


# 個々のAct
# #############################################################################
# メッセージ
# *****************************************************************************
# 設定済みメッセージ表示完了待機
class _MsgBase(BattleActWait):
    def __init__(self, text:str, params:dict):
        super().__init__()
        self.text = text
        self.params = params

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
        self.msg_dq.append_msg("コマンド？")
        self.act.add(CmdCheck())

# コマンド選択待ち
class CmdCheck(BattleActWait):
    def waiting(self):
        if "attack" in self.xmlui.event.trg:
            # 選択されたらメニューは閉じる
            XUWinBase(self.xmlui.find_by_id("menu")).start_close()

            # ダメージ計算
            enemy_data.data["hit"] = XUTextUtil.format_zenkaku(random.randint(1, 100))

            self.act.add(
                PlayerMsg("{name}の　こうげき！", user_data.data),
                BlinkEffect(),
                PlayerMsg("{name}に　{hit}ポイントの\nダメージを　あたえた！", enemy_data.data),
                EnemyStart())
            return True

        if "run" in self.xmlui.event.trg:
            # 選択されたらメニューは閉じる
            XUWinBase(self.xmlui.find_by_id("menu")).start_close()

            # 逃げる
            self.act.add(
                PlayerMsg("{name}は　にげだした", user_data.data),
                RunWait(),
                PlayerMsg("しかし　まわりこまれて\nしまった!", {}),
                EnemyStart())
            return True

        if "spel" in self.xmlui.event.trg:
            # 選択されたらメニューは閉じる
            XUWinBase(self.xmlui.find_by_id("menu")).start_close()

            self.act.add(
                PlayerMsg("じゅもんを　おぼえていない", {}),
                CmdStart())  # コマンド選択に戻る
            return True

        if "tools" in self.xmlui.event.trg:
            self.xmlui.popup("under_construct")

        return False

# 敵の行動
# *****************************************************************************
class EnemyStart(BattleActItem):
    def init(self):
        self.set_wait(10)  # コマンド？を出すのにちょっと溜める

    def action(self):
        # ダメージ計算
        damage = random.randint(5, 10)
        user_data.data["damage"] = XUTextUtil.format_zenkaku(damage)

        self.act.add(
            EnemyMsg("{name}の　こうげき！", enemy_data.data),
            DamageEffect(damage),
            EnemyMsg("{name}は　{damage}ポイントの\nだめーじを　うけた", user_data.data))
        
        if user_data.hp > damage:
            self.act.add(CmdStart())
        else:
            self.act.add(
                DeadWait(),
                PlayerMsg("{name}は　しんでしまった", user_data.data),
                ReturnKing())

# ウェイト系
# *****************************************************************************
class DamageEffect(BattleActWait):
    def __init__(self, damage:int):
        super().__init__()
        self.damage = damage
        self.set_wait(15)  # 適当時間

    def waiting(self):
        # とりあえず画面揺らし
        self.act.sway_x = random.randint(-3, 3)
        self.act.sway_y = random.randint(-3, 3)
        return False

    def action(self):
        self.act.sway_x = 0
        self.act.sway_y = 0
        user_data.hp = max(0, user_data.hp - self.damage)

class BlinkEffect(BattleActWait):
    def init(self):
        self.set_wait(10)  # エフェクトはないので適当待ち

    def waiting(self):
        self.act.blink = self.count % 2 < 1
        return False

    def action(self):
        self.blink = False

class RunWait(BattleActWait):
    def init(self):
        self.set_wait(15)  # SE待ち

class DeadWait(BattleActWait):
    def init(self):
        self.set_wait(15)  # SE待ち

# 死に戻り
# *****************************************************************************
class ReturnKing(BattleActItem):
    def init(self):
        self.set_wait(45)  # ちょっと待機
    def action(self):
        self.act.is_dead = True
