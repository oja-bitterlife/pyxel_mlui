import pyxel

from xmlui.core import XUTemplate,XUEvent,XUSelectItem
from xmlui.lib import select
from system import system_font

def ui_init(template:XUTemplate):
    shop = select.Decorator(template)

    def shop_act_item(shop_act_item:XUSelectItem):
        area = shop_act_item.area
        pyxel.text(area.x, area.y, shop_act_item.text, 7, system_font.font)

    @shop.list("shop_act_lst", "shop_act_item")
    def shop_act_lst(shop_act_lst:select.List, event:XUEvent):
        for item in shop_act_lst.items:
            shop_act_item(item)
