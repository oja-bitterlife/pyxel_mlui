import pyxel

# タイトル画面
from xmlui_core import XMLUI,XUState,XUEvent
from ui_common import xmlui,draw_menu_cursor,draw_msg_cursor
from xmlui_pyxel import select,text,win,input

UI_TEMPLATE_TITLE = "ui_title"
xmlui.template_fromfile("assets/ui/dq.xml", UI_TEMPLATE_TITLE)

class Title:
    def __init__(self):
        xmlui.open(UI_TEMPLATE_TITLE, "game_title")

    def update(self):
        pass

    def draw(self):
        xmlui.check_input_on(pyxel.btn)
        xmlui.draw()



# メニューアイテム
# ---------------------------------------------------------
@select.list(xmlui, "menu_list", "menu_item", "item_w", "item_h")
def start_menu(list_win:select.List, event:XUEvent):
    # メニュー選択
    list_win.select_by_event(event.trg, *input.UP_DOWN)
    # カーソル追加
    draw_menu_cursor(list_win.selected_item, 0, 1)

@select.list(xmlui, "menu_list", "menu_item", "item_w", "item_h")
def speed_menu(list_win:select.List, event:XUEvent):
    # メニュー選択
    list_win.select_by_event(event.trg, *input.LEFT_RIGHT)
    # カーソル追加
    draw_menu_cursor(list_win.selected_item, 0, 1)

# メニューアイテム
# ---------------------------------------------------------
@select.item(xmlui, "menu_item")
def start_item(menu_item:select.Item, event:XUEvent):
    pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, 7, text.default.font)

@select.item(xmlui, "menu_item")
def speed_item(menu_item:select.Item, event:XUEvent):
    pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, 7, text.default.font)

