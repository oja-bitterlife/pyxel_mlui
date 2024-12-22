import random
from enum import StrEnum

import pyxel

# タイトル画面
from xmlui.core import XMLUI,XUEvent,XUWinBase,XUSelectItem,XUTextUtil
from xmlui.lib import select,text
from xmlui.ext.scene import XUXScene
from xmlui.ext.timer import XUXTimeout
from ui_common import system_font
from xmlui_modules import dq
from db import user_data, enemy_data

class Battle(XUXScene):
    UI_TEMPLATE_BATTLE = "ui_battle"

    # バトルの状態遷移
    class TurnState(StrEnum):
        MSG_DRAWING = "msg_drawing"
        CMD_WAIT = "command_wait"

        ATK_START = "attack_start"
        ATK_WAIT = "attack_wait"
        ATK_RESULT = "attack_result"
        ATK_END = "attack_end"

        ENEMY_START = "enemy_start"
        ENEMY_WAIT = "enemy_wait"
        ENEMY_RESULT = "enemy_result"
        ENEMY_END = "enemy_end"

    turn_state = TurnState.MSG_DRAWING

    # 一定時間後にステートを変更する
    class StateTimer(XUXTimeout):
        def __init__(self, battle:"Battle", timeout, next_state:"Battle.TurnState"):
            super().__init__(timeout)
            self.battle = battle
            self.next_state = next_state

        def action(self):
            self.battle.turn_state = self.next_state
            print("action")

    def __init__(self, xmlui:XMLUI):
        super().__init__(xmlui)

        # なにかと使うタイマー
        self.timer = None

        # UIの読み込み
        self.template = self.xmlui.load_template("assets/ui/battle.xml")
        ui_init(self.template)

        # バトル開始UI初期化
        print(enemy_data.data)
        self.battle = self.xmlui.open("battle")
        msg_dq = dq.MsgDQ(self.battle.find_by_id("msg_text"))
        msg_dq.append_msg("{name}が　あらわれた！", enemy_data.data)

    def closed(self):
        # 読みこんだUIの削除
        self.template.remove()

    def update(self):
        if self.timer is not None:
            self.timer.update()

        msg_dq = dq.MsgDQ(self.battle.find_by_id("msg_text"))
        match self.turn_state:
            case Battle.TurnState.MSG_DRAWING:
                # メッセージ表示完了
                if msg_dq.is_all_finish:
                    # コマンド入力開始
                    msg_dq.append_msg("コマンド？")
                    self.battle.open("menu")
                    self.turn_state = Battle.TurnState.CMD_WAIT

            case Battle.TurnState.CMD_WAIT:
                menu = dq.MsgDQ(self.battle.find_by_id("menu"))
                if "attack" in self.xmlui.event.trg:
                    XUWinBase(menu).start_close()
                    self.turn_state = Battle.TurnState.ATK_START

            # 自分の攻撃
            case Battle.TurnState.ATK_START:
                enemy_data.data["hit"] = XUTextUtil.format_zenkaku(random.randint(1, 100))
                msg_dq.append_msg("{name}の　こうげき！", user_data.data)

                self.turn_state = Battle.TurnState.ATK_WAIT
                self.timer = Battle.StateTimer(self, 30, Battle.TurnState.ATK_RESULT)
            case Battle.TurnState.ATK_WAIT:
                    pass
            case Battle.TurnState.ATK_RESULT:
                msg_dq.append_msg("{name}に　{hit}ポイントの\nダメージを　あたえた！", enemy_data.data)

                self.turn_state = Battle.TurnState.ATK_END
                self.timer = Battle.StateTimer(self, 15, Battle.TurnState.ENEMY_START)
            case Battle.TurnState.ATK_END:
                    pass

            # 敵の攻撃
            case Battle.TurnState.ENEMY_START:
                user_data.data["damage"] = XUTextUtil.format_zenkaku(random.randint(1, 10))
                msg_dq.append_enemy("{name}の　こうげき！", enemy_data.data)

                self.turn_state = Battle.TurnState.ENEMY_WAIT
                self.timer = Battle.StateTimer(self, 30, Battle.TurnState.ENEMY_RESULT)

            case Battle.TurnState.ENEMY_WAIT:
                    pass
            case Battle.TurnState.ENEMY_RESULT:
                msg_dq.append_enemy("{name}は　{damage}ポイントの\nだめーじを　うけた", user_data.data)
                self.turn_state = Battle.TurnState.ENEMY_END
                self.timer = Battle.StateTimer(self, 15, Battle.TurnState.MSG_DRAWING)
            case Battle.TurnState.ENEMY_END:
                    pass


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
    battle_dq = dq.Decorator(template)

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
    def msg_text(msg_text:dq.MsgDQ, event:XUEvent):
        # メッセージ共通処理
        common_msg_text(msg_text, event, False)

        # メッセージウインドウの無効化(カーソル用)
        # msg_text.enable = False

        # メッセージウインドウがアクティブの時は自動テキスト送り
        if event.is_active and msg_text.is_next_wait:
            msg_text.next()

        if msg_text.is_all_finish:
            return "finish_msg"
