import pyxel

from xmlui.core import XUElem,XUEvent,XUTextUtil,XURect,XUWinInfo
from xmlui.lib import text,debug
from system import system_font

from ui_common import get_world_clip
from db import user_data
from battle.data import BattleData

def ui_init(xmlui:debug.DebugXMLUI[BattleData]):
    result_text = text.Decorator(xmlui)

    @result_text.label("result_who")
    def result_who(result_who:text.XULabel, event:XUEvent):
        text = user_data.player_data[xmlui.data_ref.player_idx]["name"]
        pyxel.text(result_who.area.x, result_who.area.y, text, 7, system_font.font)


