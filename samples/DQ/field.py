import pyxel

# タイトル画面
from xmlui_core import XUState,XUEvent
from ui_common import xmlui,draw_menu_cursor
from xmlui_pyxel import select,text,input

class Field:
    UI_TEMPLATE_FIELD = "ui_field"

    def __init__(self):
        xmlui.template_fromfile("assets/ui/field.xml", self.UI_TEMPLATE_FIELD)

    def __del__(self):
        xmlui.remove_template(self.UI_TEMPLATE_FIELD)

    def update(self):
        print("field")
        return None

    def draw(self):
        xmlui.check_input_on(pyxel.btn)
        xmlui.draw()


# 町の中
# ---------------------------------------------------------
