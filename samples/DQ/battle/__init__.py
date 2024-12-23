import random
from enum import StrEnum
from typing import Callable

import pyxel

# タイトル画面
from xmlui.core import XMLUI,XUEvent,XUWinBase,XUSelectItem,XUTextUtil
from xmlui.lib import select,text
from xmlui.ext.scene import XUXScene
from xmlui.ext.timer import XUXTimeout
from ui_common import system_font,WIN_OPEN_SPEED
from msg_dq import MsgDQ
from msg_dq import Decorator as DQDecorator
from db import user_data, enemy_data


class XUXActItem(XUXTimeout):
    # デフォルトはすぐ実行
    def __init__(self, xmlui:XMLUI):
        super().__init__(0)
        self.xmlui = xmlui
        self._init_func:Callable|None = self.init

    # コンストラクタではなくinit()の中で時間を設定する。
    def set_wait(self, wait:int):
        self._count_max = wait

    # オーバーライドして使う物
    def init(self):
        pass

class XUXActWait(XUXActItem):
    WAIT_FOREVER = 2**31-1

    # デフォルトは無限待機
    def __init__(self, xmlui:XMLUI):
        super().__init__(xmlui)
        self.set_wait(self.WAIT_FOREVER)

    # override
    @property
    def alpha(self):
        if self._count_max == self.WAIT_FOREVER:
            return 1
        else:
            return self.alpha

    # override
    def update(self) -> bool:
        update_result = super().update()
        if not self.is_finish:
            if self.waiting():
                self.finish()
        return update_result

    # オーバーライドして使う物
    def waiting(self) -> bool:
        return False

class XUXAct:
    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui
        self.queue:list[XUXActItem] = []

    def add(self, item:XUXActItem):
        self.queue.append(item)

    def next(self):
        self.queue.pop(0)

    def update(self):
        if self.queue:
            act = self.queue[0]
            if act._init_func:
                act._init_func()  # 初回はinitも実行
                act._init_func = None
            act.update()

            # 完了したら次のAct
            if act.is_finish:
                self.next()

class Battle(XUXScene):
    UI_TEMPLATE_BATTLE = "ui_battle"

    # # バトルの状態遷移
    # class TurnState(StrEnum):
    #     MSG_DRAWING = "msg_drawing"
    #     CMD_WAIT = "command_wait"

    #     ATK_START = "attack_start"
    #     ATK_WAIT = "attack_wait"
    #     ATK_RESULT = "attack_result"
    #     ATK_END = "attack_end"

    #     ENEMY_START = "enemy_start"
    #     ENEMY_WAIT = "enemy_wait"
    #     ENEMY_RESULT = "enemy_result"
    #     ENEMY_END = "enemy_end"

    # turn_state = TurnState.MSG_DRAWING

    # # 一定時間後にステートを変更する
    # class StateTimer(XUXTimeout):
    #     def __init__(self, battle:"Battle", timeout, next_state:"Battle.TurnState"):
    #         super().__init__(timeout)
    #         self.battle = battle
    #         self.next_state = next_state

    #         self.battle.turn_state = self.next_state
    #         print("action")


    # バトル用Actベース
    class BattleActItem(XUXActItem):
        def __init__(self, battle:"Battle"):
            super().__init__(battle.xmlui)
            self.battle = battle
    class BattleActWait(XUXActWait):
        def __init__(self, battle:"Battle"):
            super().__init__(battle.xmlui)
            self.battle = battle

    # 個々のAct
    class BattleStart(BattleActWait):
        def init(self):
            self.msg_dq = MsgDQ(self.xmlui.find_by_id("msg_text"))
            self.msg_dq.append_msg("{name}が　あらわれた！", enemy_data.data)

        def waiting(self):
            if self.msg_dq.is_all_finish:
                self.battle.act.add(Battle.CmdStart(self.battle))
                return True
            return False

    class CmdStart(BattleActItem):
        def init(self):
            self.xmlui.open("menu")
            self.set_wait(WIN_OPEN_SPEED)

        def action(self):
            self.msg_dq = MsgDQ(self.xmlui.find_by_id("msg_text"))
            self.msg_dq.append_msg("コマンド？")
            self.battle.act.add(Battle.CmdWait(self.battle))

    class CmdWait(BattleActWait):
        def waiting(self):
            if "attack" in self.xmlui.event.trg:
                menu = MsgDQ(self.xmlui.find_by_id("menu"))
                XUWinBase(menu).start_close()
                self.battle.act.add(Battle.AtkStart(self.battle))
                return True
            return False

    class AtkStart(BattleActWait):
        def init(self):
            enemy_data.data["hit"] = XUTextUtil.format_zenkaku(random.randint(1, 100))

            self.msg_dq = MsgDQ(self.xmlui.find_by_id("msg_text"))
            self.msg_dq.append_msg("{name}の　こうげき！", user_data.data)

        def waiting(self):
            if self.msg_dq.is_all_finish:
                self.battle.act.add(Battle.EffectWait(self.battle))
                self.battle.act.add(Battle.AtkEnd(self.battle))
                return True
            return False

    class EffectWait(BattleActItem):
        def init(self):
            self.set_wait(30)  # エフェクトはないので適当待ち

    class AtkEnd(BattleActItem):
        def init(self):
            msg_dq = MsgDQ(self.xmlui.find_by_id("msg_text"))
            msg_dq.append_msg("{name}に　{hit}ポイントの\nダメージを　あたえた！", enemy_data.data)
            self.battle.act.add(Battle.CmdStart(self.battle))
            self.set_wait(15)


    def __init__(self, xmlui:XMLUI):
        super().__init__(xmlui)
        self.act = XUXAct(xmlui)

        # UIの読み込み
        self.template = self.xmlui.load_template("assets/ui/battle.xml")
        ui_init(self.template)

        # バトル開始UI初期化
        self.battle = self.xmlui.open("battle")

        # 最初のAct
        self.act.add(Battle.BattleStart(self))

    def closed(self):
        # 読みこんだUIの削除
        self.template.remove()

    def update(self):
        pass
        # self.act.update()

            # case Battle.TurnState.ATK_RESULT:
            #     self.turn_state = Battle.TurnState.ATK_END
            #     self.timer = None
            # case Battle.TurnState.ATK_END:
            #     if msg_dq.is_all_finish and self.timer is None:
            #         self.timer = Battle.StateTimer(self, 15, Battle.TurnState.ENEMY_START)

            # # 敵の攻撃
            # case Battle.TurnState.ENEMY_START:
            #     user_data.data["damage"] = XUTextUtil.format_zenkaku(random.randint(1, 10))
            #     msg_dq.append_enemy("{name}の　こうげき！", enemy_data.data)
            #     self.turn_state = Battle.TurnState.ENEMY_WAIT
            #     self.timer = None
            # case Battle.TurnState.ENEMY_WAIT:
            #     if msg_dq.is_all_finish and self.timer is None:
            #         self.timer = Battle.StateTimer(self, 30, Battle.TurnState.ENEMY_RESULT)
            # case Battle.TurnState.ENEMY_RESULT:
            #     msg_dq.append_enemy("{name}は　{damage}ポイントの\nだめーじを　うけた", user_data.data)
            #     self.turn_state = Battle.TurnState.ENEMY_END
            #     self.timer = None
            # case Battle.TurnState.ENEMY_END:
            #     if msg_dq.is_all_finish and self.timer is None:
            #         self.timer = Battle.StateTimer(self, 15, Battle.TurnState.MSG_DRAWING)

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

        # # メッセージウインドウがアクティブの時は自動テキスト送り
        if event.is_active and msg_text.is_next_wait:
            msg_text.next()

        if msg_text.is_all_finish:
            return "finish_msg"
