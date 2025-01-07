import pyxel

from xmlui.core import XMLUI,XUElem,XUEvent,XUSelectItem,XUWinBase,XUTextUtil,XURect
from xmlui.lib import select,text
from system import system_font

from db import user_data,enemy_data
from battle.data import BattleData

def ui_init(xmlui:XMLUI[BattleData]):
    target_select = select.Decorator(xmlui)

    @target_select.grid("enemy_sel", "select_item")
    def enemy_sel(enemy_sel:select.Grid, event:XUEvent):
        for i,item in enumerate(enemy_sel.items):
            area = item.area
            pyxel.text(area.x, area.y, str(i), 7, system_font.font)
    
    @target_select.list("player_sel", "select_item")
    def player_sel(player_sel:select.List, event:XUEvent):
        for i,item in enumerate(player_sel.items):
            area = item.area
            pyxel.text(area.x, area.y, str(i), 7, system_font.font)
    
