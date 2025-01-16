import pyxel

from xmlui.core import XUElem,XUEvent
from xmlui.lib import select,debug

from system import system_font,hand_cursor
from battle.data import BattleData

from db import enemy_data

def ui_init(xmlui:debug.DebugXMLUI[BattleData]):
    target_select = select.Decorator(xmlui)

    @target_select.grid("enemy_sel", "select_item")
    def enemy_sel(enemy_sel:select.XUGrid, event:XUEvent):
        battle_data = xmlui.data_ref
        target_idx = battle_data.target[battle_data.player_idx]

        # 敵のエリアでの選択じゃなかった
        if target_idx < 0:
            return

        # カーソル移動
        input = ""
        if event.check_repeat(XUEvent.Key.LEFT):
            input = "next_l"
        elif event.check_repeat(XUEvent.Key.RIGHT):
            input = "next_r"
        elif event.check_repeat(XUEvent.Key.UP):
            input = "next_u"
        elif event.check_repeat(XUEvent.Key.DOWN):
            input = "next_d"

        if input:
            battle_data.target[battle_data.player_idx] = enemy_data.data[target_idx][input]

        # カーソル表示
        area = enemy_sel.items[target_idx].area
        hand_cursor.draw(area.x, area.y + 8)
    
    @target_select.list("player_sel", "select_item")
    def player_sel(player_sel:select.XUList, event:XUEvent):
        battle_data = xmlui.data_ref
        target_idx = battle_data.target[battle_data.player_idx]

        # プレイヤーエリアでの選択中ではない
        if target_idx >= 0:
            return
    
        target_idx = -target_idx - 1

        # カーソル移動
        if event.check_repeat(XUEvent.Key.LEFT):
            battle_data.target[battle_data.player_idx] = 1
        elif player_sel.select_by_event(event.repeat, *XUEvent.Key.UP_DOWN()):
            battle_data.target[battle_data.player_idx] = -player_sel.selected_no - 1

        # カーソル表示
        area = player_sel.selected_item.area
        hand_cursor.draw(area.x + battle_data.player_offset[player_sel.selected_no], area.y+8)

    @xmlui.tag_draw("target_result")
    def target_result(target_result:XUElem, event:XUEvent):
        # コマンド選択中のみ表示
        if xmlui.data_ref.is_cmd_selecting:
            for i in range(xmlui.data_ref.player_idx):
                target = xmlui.data_ref.target[i]
                if target < 0:
                    target = -target - 1
                    x = xmlui.data_ref.player_rect[target].x + (i+1)*system_font.size
                    y = xmlui.data_ref.player_rect[target].y - system_font.size
                else:
                    x = xmlui.data_ref.enemy_rect[target].x + (i+1)*system_font.size
                    y = xmlui.data_ref.enemy_rect[target].y - system_font.size

                pyxel.text(x, y, f"{i+1}", 7, system_font.font)
