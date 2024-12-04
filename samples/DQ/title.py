import pyxel

# タイトル画面
from xmlui_core import XMLUI,XUState,XUEvent
from ui_common import xmlui,draw_menu_cursor
from xmlui_pyxel import select,text,win,input

UI_TEMPLATE_TITLE = "ui_title"

class Title:
    def __init__(self):
        xmlui.template_fromfile("assets/ui/dq.xml", UI_TEMPLATE_TITLE)
        xmlui.open(UI_TEMPLATE_TITLE, "game_title")

    def __del__(self):
        xmlui.remove_template(UI_TEMPLATE_TITLE)

    def update(self):
        if "game_start" in xmlui.event.trg:
            return "next_scene"
        return None

    def draw(self):
        xmlui.check_input_on(pyxel.btn)
        xmlui.draw()


# タイトル画面UI
# ---------------------------------------------------------
@select.list(xmlui, "game_start", "menu_item", "item_w", "item_h")
def game_start(game_start:select.List, event:XUEvent):
    # メニュー選択
    game_start.select_by_event(event.trg, *input.UP_DOWN)
    # カーソル追加
    draw_menu_cursor(game_start.selected_item, 0, 1)

    if input.BTN_A in event.trg:
        game_start.close_on("game_start")

@select.list(xmlui, "game_speed", "menu_item", "item_w", "item_h")
def game_speed(game_speed:select.List, event:XUEvent):
    # メニュー選択
    is_change = game_speed.select_by_event(event.trg, *input.LEFT_RIGHT)

    # カーソル追加
    draw_menu_cursor(game_speed.selected_item, 0, 1)

    # メッセージスピードを切り替える
    if is_change:
        match game_speed:
            case "slow":
                print("msg is slow")
            case "normal":
                print("msg is normal")
            case "fast":
                print("msg is fast")

# メニューアイテム
# ---------------------------------------------------------
@select.item(xmlui, "menu_item")
def start_item(menu_item:select.Item, event:XUEvent):
    pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, 7, text.default.font)

