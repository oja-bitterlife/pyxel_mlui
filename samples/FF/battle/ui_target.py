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
        if target_idx >= 0:
            input = ""
            if XUEvent.Key.LEFT in event.trg:
                input = "next_l"
            elif XUEvent.Key.RIGHT in event.trg:
                input = "next_r"
            elif XUEvent.Key.UP in event.trg:
                input = "next_u"
            elif XUEvent.Key.DOWN in event.trg:
                input = "next_d"

            if input:
                battle_data.target[battle_data.player_idx] = enemy_data.data[target_idx][input]

            # カーソル表示
            area = enemy_sel.items[target_idx].area
            hand_cursor.draw(area.x, area.y)
    
    @target_select.list("player_sel", "select_item")
    def player_sel(player_sel:select.List, event:XUEvent):
        battle_data = xmlui.data_ref
        target_idx = battle_data.target[battle_data.player_idx]
        if target_idx < 0:
            for i,item in enumerate(player_sel.items):
                area = item.area
                pyxel.text(area.x + battle_data.player_offset[i], area.y, str(i), 7, system_font.font)
    
