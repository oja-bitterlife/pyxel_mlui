import random
import pyxel

# タイトル画面
from xmlui.core import XMLUI,XUEvent,XUWinBase,XUSelectItem,XUTextUtil
from xmlui.lib import select,text
from xmlui.ext.scene import XUXScene,XUXAct,XUXActItem,XUXActWait
from ui_common import system_font
from msg_dq import MsgDQ
from msg_dq import Decorator as DQDecorator
from db import user_data, enemy_data

# バトル用シーン遷移ベース
class BattleActItem(XUXActItem):
    def __init__(self, battle:"Battle"):
        super().__init__()
        self.battle = battle
        self.xmlui = battle.xmlui

class BattleActWait(XUXActWait):
    def __init__(self, battle:"Battle"):
        super().__init__()
        self.battle = battle
        self.xmlui = battle.xmlui

sway_x = 0
sway_y = 0

# バトルシーン
# *****************************************************************************
class Battle(XUXScene):
    UI_TEMPLATE_BATTLE = "ui_battle"

    # 個々のAct
    class _MsgBase(BattleActWait):
        def __init__(self, battle:"Battle", text:str, params:dict):
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

    class PlayerMsg(_MsgBase):
        def init(self):
            self.msg_dq.append_msg(self.text, self.params)

    class EnemyMsg(_MsgBase):
        def init(self):
            self.msg_dq.append_enemy(self.text, self.params)

    class CmdStart(BattleActItem):
        def init(self):
            self.set_wait(10)  # コマンド？を出すのにちょっと溜める

        def action(self):
            self.xmlui.open("menu")
            self.msg_dq = MsgDQ(self.xmlui.find_by_id("msg_text"))
            self.msg_dq.append_msg("コマンド？")
            self.battle.act.add(Battle.CmdCheck(self.battle))

    class CmdCheck(BattleActWait):
        # メニュー選択待ち
        def waiting(self):
            if "attack" in self.xmlui.event.trg:
                # 選択されたらメニューは閉じる
                menu = MsgDQ(self.xmlui.find_by_id("menu"))
                XUWinBase(menu).start_close()

                # ダメージ計算
                enemy_data.data["hit"] = XUTextUtil.format_zenkaku(random.randint(1, 100))

                self.battle.act.add(
                    Battle.PlayerMsg(self.battle, "{name}の　こうげき！", user_data.data),
                    Battle.EffectWait(self.battle),
                    Battle.PlayerMsg(self.battle, "{name}に　{hit}ポイントの\nダメージを　あたえた！", enemy_data.data),
                    Battle.EnemyStart(self.battle))
                return True

            if "run" in self.xmlui.event.trg:
                # 逃げる
                self.battle.act.add(
                    Battle.PlayerMsg(self.battle, "{name}は　にげだした", user_data.data),
                    Battle.RunWait(self.battle),
                    Battle.PlayerMsg(self.battle, "しかし まわりこまれて\nしまった!", {}),
                    Battle.EnemyStart(self.battle))
                return True

            if "spel" in self.xmlui.event.trg:
                self.battle.act.add(
                    Battle.PlayerMsg(self.battle, "じゅもんを　おぼえていない", {}),
                    Battle.CmdStart(self.battle))
                return True

            return False

    class EffectWait(BattleActWait):
        def init(self):
            self.set_wait(20)  # エフェクトはないので適当待ち
        def waiting(self):
            global sway_x, sway_y
            sway_x = random.randint(-3, 3)
            sway_y = random.randint(-3, 3)
            return False

    class RunWait(BattleActWait):
        def init(self):
            self.set_wait(20)  # SE待ち

    class EnemyStart(BattleActItem):
        def init(self):
            self.set_wait(10)  # コマンド？を出すのにちょっと溜める

        def action(self):
            # ダメージ計算
            user_data.data["damage"] = XUTextUtil.format_zenkaku(random.randint(1, 10))

            self.battle.act.add(
                Battle.EnemyMsg(self.battle, "{name}の　こうげき！", enemy_data.data),
                Battle.EffectWait(self.battle),
                Battle.EnemyMsg(self.battle, "{name}は　{damage}ポイントの\nだめーじを　うけた", user_data.data),
                Battle.CmdStart(self.battle))


    def __init__(self, xmlui:XMLUI):
        super().__init__(xmlui)
        self.act = XUXAct()

        # UIの読み込み
        self.template = self.xmlui.load_template("assets/ui/battle.xml")
        ui_init(self.template)

        # バトル開始UI初期化
        self.battle = self.xmlui.open("battle")

        # 最初のAct
        self.act.add(
            Battle.PlayerMsg(self, "{name}が　あらわれた！", enemy_data.data),
            Battle.CmdStart(self))

    def closed(self):
        # 読みこんだUIの削除
        self.template.remove()

    def update(self):
        self.act.update()

    def draw(self):
        # UIの描画(fieldとdefaultグループ)
        self.xmlui.draw()

# バトルUI
# *****************************************************************************
from ui_common import common_msg_text, get_world_clip, draw_menu_cursor

def ui_init(template):
    # fieldグループ用デコレータを作る
    battle_select = select.Decorator(template)
    battle_text = text.Decorator(template)
    battle_dq = DQDecorator(template)

    # コマンドメニューのタイトル
    @battle_text.label("title")
    def title(title:text.Label, event:XUEvent):
        clip = get_world_clip(XUWinBase.find_parent_win(title)).intersect(title.area)
        pyxel.rect(title.area.x, title.area.y, title.area.w, clip.h, 0)  # タイトルの下地

        # テキストはセンタリング
        if title.area.y < clip.bottom():  # world座標で比較
            x, y = title.aligned_pos(system_font)
            pyxel.text(x, y-1, title.text, 7, system_font.font)

    # メニューアイテム
    # ---------------------------------------------------------
    def menu_item(menu_item:XUSelectItem):
        # ウインドウのクリップ状態に合わせて表示する
        if menu_item.area.y < get_world_clip(XUWinBase.find_parent_win(menu_item)).bottom():
            pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, 7, system_font.font)

            # カーソル表示
            if menu_item.selected and menu_item.enable:
                draw_menu_cursor(menu_item, 0, 0)

    # コマンドメニュー
    # ---------------------------------------------------------
    @battle_select.grid("menu_grid", "menu_item")
    def menu_grid(menu_grid:select.Grid, event:XUEvent):
        # 各アイテムの描画
        for item in menu_grid.items:
            menu_item(item)

        # メニュー選択
        menu_grid.select_by_event(event.trg, *XUEvent.Key.CURSOR())

        # 選択アイテムの表示
        if XUEvent.Key.BTN_A in event.trg:
            return menu_grid.action


    @battle_dq.msg_dq("msg_text")
    def msg_text(msg_text:MsgDQ, event:XUEvent):
        # メッセージ共通処理
        common_msg_text(msg_text, event, False)


        # 自動テキスト送り
        if msg_text.is_next_wait:
            msg_text.next()

        if msg_text.is_all_finish:
            return "finish_msg"
