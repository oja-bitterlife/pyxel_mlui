import pyxel

from xmlui.core import XUElem,XUEvent,XUTextUtil,XURect,XUWinInfo
from xmlui.lib import text,debug
from system import system_font

from ui_common import get_world_clip
from db import user_data,enemy_data
from battle.data import BattleData

def ui_init(xmlui:debug.DebugXMLUI[BattleData]):
    result_text = text.Decorator(xmlui)

    @result_text.label("result_who")
    def result_who(result_who:text.XULabel, event:XUEvent):
        text = user_data.player_data[xmlui.data_ref.player_idx]["name"]
        pyxel.text(result_who.area.x, result_who.area.y, text, 7, system_font.font)

    @result_text.label("result_target")
    def result_target(result_target:text.XULabel, event:XUEvent):
        target_idx = xmlui.data_ref.target[xmlui.data_ref.player_idx]

        if target_idx < 0:
            # パーティーアタック
            target_idx = abs(target_idx)-1
            target_name = user_data.player_data[target_idx]["name"]
        else:
            target_name = enemy_data.data[target_idx]["name"]

        pyxel.text(result_target.area.x, result_target.area.y, target_name, 7, system_font.font)


    @result_text.label("result_action")
    def result_action(result_action:text.XULabel, event:XUEvent):
        text = "　２かいヒット"
        pyxel.text(result_action.area.x, result_action.area.y, text, 7, system_font.font)
