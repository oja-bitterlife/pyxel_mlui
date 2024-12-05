import pyxel

# タイトル画面
from xmlui_core import XUState,XUEvent
from ui_common import xmlui,draw_menu_cursor
from xmlui_pyxel import select,text,input

UI_TEMPLATE_FIELD = "ui_field"

class Field:
    def __init__(self):
        xmlui.template_fromfile("assets/ui/dq.xml", UI_TEMPLATE_FIELD)
        xmlui.open(UI_TEMPLATE_FIELD, "game_title")

    def __del__(self):
        xmlui.remove_template(UI_TEMPLATE_FIELD)

    def update(self):
        return None

    def draw(self):
        xmlui.check_input_on(pyxel.btn)
        xmlui.draw()


# 町の中
# ---------------------------------------------------------
