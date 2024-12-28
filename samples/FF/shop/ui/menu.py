import pyxel

from xmlui.core import XUTemplate,XUEvent,XUSelectItem,XUWinBase
from xmlui.lib import select
from system import system_font, hand_cursor

def ui_init(template:XUTemplate):
    shop = select.Decorator(template)

    def shop_sel_item(shop_act_item:XUSelectItem):
        area = shop_act_item.area
        pyxel.text(area.x, area.y, shop_act_item.text, 7, system_font.font)

        if shop_act_item.selected:
            hand_cursor.draw(area.x, area.y+4)

    @shop.list("shop_act_list", "shop_sel_item")
    def shop_act_list(shop_act_lst:select.List, event:XUEvent):
        for item in shop_act_lst.items:
            shop_sel_item(item)

        shop_act_lst.select_by_event(event.trg, *XUEvent.Key.LEFT_RIGHT())
        if XUEvent.Key.BTN_A in event.trg:
            match shop_act_lst.action:
                case "buy":
                    win = XUWinBase.find_parent_win(shop_act_lst)
                    shop_act_lst.remove()
                    win.open("buy_list")
                case "sell":
                    pass
                case "exit":
                    # バトルへ
                    pass

    @shop.list("buy_num", "shop_sel_item")
    def buy_num(buy_num:select.List, event:XUEvent):
        for item in buy_num.items:
            shop_sel_item(item)

        buy_num.select_by_event(event.trg, *XUEvent.Key.LEFT_RIGHT())
        # if XUEvent.Key.BTN_A in event.trg:
        #     match shop_act_lst.action:
        #         case "buy":
        #             win = XUWinBase.find_parent_win(shop_act_lst)
        #             shop_act_lst.remove()
        #             win.open("buy_list")
        #         case "sell":
        #             pass
        #         case "exit":
        #             # バトルへ
        #             pass
