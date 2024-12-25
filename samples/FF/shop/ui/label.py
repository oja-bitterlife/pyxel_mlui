import pyxel

from xmlui.core import XUTemplate,XUEvent
from xmlui.lib import text
from system import system_font

def ui_init(template:XUTemplate):
    shop = text.Decorator(template)

    @shop.label("label")
    def label(label:text.Label, event:XUEvent):
        x, y = label.aligned_pos(system_font)
        pyxel.text(x, y, label.text, 7, system_font.font)

