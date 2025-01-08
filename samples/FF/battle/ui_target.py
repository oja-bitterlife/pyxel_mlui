import pyxel

from xmlui.core import XUEvent
from xmlui.lib import select,debug

from system import system_font,hand_cursor
from battle.data import BattleData

from db import enemy_data

def ui_init(xmlui:debug.DebugXMLUI[BattleData]):
    target_select = select.Decorator(xmlui)

    @target_select.grid("enemy_sel", "select_item")
    def enemy_sel(enemy_sel:select.Grid, event:XUEvent):
        battle_data = xmlui.data_ref
        target_idx = battle_data.target[battle_data.player_idx]

        # 敵のエリアでの選択じゃなかった
        if target_idx < 0:
            return

        # カーソル移動
        input = ""
        if XUEvent.Key.LEFT in event._repeat:
            input = "next_l"
        elif XUEvent.Key.RIGHT in event._repeat:
            input = "next_r"
        elif XUEvent.Key.UP in event._repeat:
            input = "next_u"
        elif XUEvent.Key.DOWN in event._repeat:
            input = "next_d"

        if input:
            battle_data.target[battle_data.player_idx] = enemy_data.data[target_idx][input]

        # カーソル表示
        area = enemy_sel.items[target_idx].area
        hand_cursor.draw(area.x, area.y + 8)
    
    @target_select.list("player_sel", "select_item")
    def player_sel(player_sel:select.List, event:XUEvent):
        battle_data = xmlui.data_ref
        target_idx = battle_data.target[battle_data.player_idx]

        # プレイヤーエリアでの選択中ではない
        if target_idx >= 0:
            return
    
        target_idx = -target_idx - 1

        # カーソル移動
        if XUEvent.Key.LEFT in event._repeat:
            battle_data.target[battle_data.player_idx] = 1
        elif player_sel.select_by_event(event._repeat, *XUEvent.Key.UP_DOWN()):
            battle_data.target[battle_data.player_idx] = -player_sel.selected_no - 1

        # カーソル表示
        area = player_sel.selected_item.area
        hand_cursor.draw(area.x + battle_data.player_offset[player_sel.selected_no], area.y+8)
