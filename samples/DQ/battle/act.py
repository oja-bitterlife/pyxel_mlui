import random

from xmlui.core import XUWinBase,XUTextUtil
from xmlui.ext.scene import XUESceneBase,XUEActItem,XUEActWait
from msg_dq import MsgDQ
from db import user_data, enemy_data


# バトル用シーン遷移ベース
# #############################################################################
class BattleData:
    def __init__(self, scene:XUESceneBase):
        super().__init__()
        self.scene = scene

        # データ受け渡しをここでやってみる
        self.sway_x = 0
        self.sway_y = 0
        self.blink = False

class BattleActItem(XUEActItem):
    def __init__(self, data:BattleData):
        super().__init__()
        self.data = data

    @property
    def xmlui(self):
        return self.data.scene.xmlui

    @property
    def msg_dq(self):
        return MsgDQ(self.data.scene.xmlui.find_by_id("msg_text"))

class BattleActWait(XUEActWait):
    def __init__(self, data:BattleData):
        super().__init__()
        self.data = data

    @property
    def xmlui(self):
        return self.data.scene.xmlui

    @property
    def msg_dq(self):
        return MsgDQ(self.data.scene.xmlui.find_by_id("msg_text"))


# 個々のAct
# #############################################################################
# メッセージ
# *****************************************************************************
# 設定済みメッセージ表示完了待機
class _MsgBase(BattleActWait):
    def __init__(self, data:BattleData, text:str, params:dict):
        super().__init__(data)
        self.text = text
        self.params = params

    # メッセージ表示完了待ち
    def waiting(self):
        return self.msg_dq.is_all_finish

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
        self.data.scene.add_act(CmdCheck(self.data))

# コマンド選択待ち
class CmdCheck(BattleActWait):
    def waiting(self):
        if "attack" in self.xmlui.event.trg:
            # 選択されたらメニューは閉じる
            XUWinBase(self.xmlui.find_by_id("menu")).start_close()

            # ダメージ計算
            enemy_data.data["hit"] = XUTextUtil.format_zenkaku(random.randint(1, 100))

            self.data.scene.add_act(
                PlayerMsg(self.data, "{name}の　こうげき！", user_data.data),
                BlinkEffect(self.data),
                PlayerMsg(self.data, "{name}に　{hit}ポイントの\nダメージを　あたえた！", enemy_data.data),
                EnemyStart(self.data))
            return True

        if "run" in self.xmlui.event.trg:
            # 選択されたらメニューは閉じる
            XUWinBase(self.xmlui.find_by_id("menu")).start_close()

            # 逃げる
            self.data.scene.add_act(
                PlayerMsg(self.data, "{name}は　にげだした", user_data.data),
                RunWait(self.data),
                PlayerMsg(self.data, "しかし　まわりこまれて\nしまった!", {}),
                EnemyStart(self.data))
            return True

        if "spel" in self.xmlui.event.trg:
            # 選択されたらメニューは閉じる
            XUWinBase(self.xmlui.find_by_id("menu")).start_close()

            self.data.scene.add_act(
                PlayerMsg(self.data, "じゅもんを　おぼえていない", {}),
                CmdStart(self.data))  # コマンド選択に戻る
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

        self.data.scene.add_act(
            EnemyMsg(self.data, "{name}の　こうげき！", enemy_data.data),
            DamageEffect(self.data, damage),
            EnemyMsg(self.data, "{name}は　{damage}ポイントの\nだめーじを　うけた", user_data.data))
        
        if user_data.hp > damage:
            self.data.scene.add_act(CmdStart(self.data))
        else:
            self.data.scene.add_act(
                DeadWait(self.data),
                PlayerMsg(self.data, "{name}は　しんでしまった", user_data.data),
                ReturnKing(self.data))

# ウェイト系
# *****************************************************************************
class DamageEffect(BattleActWait):
    def __init__(self, data:BattleData, damage:int):
        super().__init__(data)
        self.damage = damage
        self.set_wait(15)  # 適当時間

    def waiting(self):
        # とりあえず画面揺らし
        self.data.sway_x = random.randint(-3, 3)
        self.data.sway_y = random.randint(-3, 3)
        return False

    def action(self):
        self.data.sway_x = 0
        self.data.sway_y = 0
        user_data.hp = max(0, user_data.hp - self.damage)

class BlinkEffect(BattleActWait):
    def init(self):
        self.set_wait(10)  # エフェクトはないので適当待ち

    def waiting(self):
        self.data.blink = self.count % 2 < 1
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
        self.data.scene.xmlui.on("dead")
