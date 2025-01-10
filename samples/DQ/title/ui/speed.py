from enum import StrEnum

from xmlui.core import XMLUI,XUEvent,XUSelectItem
from xmlui.lib import select

from title.ui.item import menu_item
from db import user_config

class MSG_SPEED(StrEnum):
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"

from ui_common import draw_menu_cursor
def ui_init(xmlui:XMLUI):
    title_select = select.Decorator(xmlui)

    # メッセージスピード選択
    @title_select.row_list("game_speed", "menu_item")
    def game_speed(game_speed:select.XURowList, event:XUEvent):
        for item in game_speed.items:
            menu_item(item)

        # メニュー選択。カーソルが動いたらTrueが返る
        if game_speed.select_by_event(event.trg, *XUEvent.Key.LEFT_RIGHT()):
            # メッセージスピードをその場で切り替える
            match game_speed.action:
                case MSG_SPEED.SLOW:
                    user_config.msg_spd = user_config.MsgSpd.SLOW
                case MSG_SPEED.NORMAL:
                    user_config.msg_spd = user_config.MsgSpd.NORMAL
                case MSG_SPEED.FAST:
                    user_config.msg_spd = user_config.MsgSpd.FAST
