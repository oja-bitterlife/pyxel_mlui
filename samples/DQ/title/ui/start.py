from xmlui.core import XUTemplate,XUEvent
from xmlui.lib import select
from title.ui.item import menu_item
import title

# タイトル画面UI
# ---------------------------------------------------------
from ui_common import draw_menu_cursor
def ui_init(template:XUTemplate):
    title_select = select.Decorator(template)

    # START/CONTINUE選択
    @title_select.list("game_start", "menu_item")
    def game_start(game_start:select.List, event:XUEvent):
        # 選択肢描画
        for item in game_start.items:
            menu_item(item)

        # メニュー選択
        game_start.select_by_event(event.trg, *XUEvent.Key.UP_DOWN())

        # メニュー決定
        if XUEvent.Key.BTN_A in event.trg:
            match game_start.action:
                case "start" as action:
                    return action
                case _:
                    game_start.xmlui.popup("under_construct")
