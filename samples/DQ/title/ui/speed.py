from enum import StrEnum

from xmlui.core import XUTemplate,XUEvent,XUSelectItem
from xmlui.lib import select
from title.ui.item import menu_item
from db import system_info

class MSG_SPEED(StrEnum):
    SLOW = "change_slow"
    NORMAL = "change_slow"
    FAST = "change_slow"

from ui_common import draw_menu_cursor
def ui_init(template:XUTemplate):
    title_select = select.Decorator(template)

    # メッセージスピード選択
    @title_select.list("game_speed", "menu_item")
    def game_speed(game_speed:select.List, event:XUEvent):
        for item in game_speed.items:
            menu_item(item)

        # メニュー選択。カーソルが動いたらTrueが返る
        if game_speed.select_by_event(event.trg, *XUEvent.Key.LEFT_RIGHT()):
            # メッセージスピードをその場で切り替える
            match game_speed.action:
                case MSG_SPEED.SLOW:
                    system_info.msg_spd = 1.0/3
                case MSG_SPEED.NORMAL:
                    system_info.msg_spd = 1
                case MSG_SPEED.FAST:
                    system_info.msg_spd = 65535
