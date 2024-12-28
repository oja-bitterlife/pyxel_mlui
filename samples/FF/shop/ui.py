import pyxel

from xmlui.core import XUElem,XUTemplate,XUEvent,XUSelectItem,XUWinBase,XUSelectInfo,XUTextUtil,XURect
from xmlui.lib import select,text
from system import system_font, hand_cursor

from shop.buy_list import BuyList

def ui_init(template:XUTemplate):
    shop_select = select.Decorator(template)
    shot_text = text.Decorator(template)

    @shot_text.label("label")
    def label(label:text.Label, event:XUEvent):
        text = XUTextUtil.format_zenkaku(label.text, {"gil":123456})
        x, y = label.aligned_pos(system_font, text)
        pyxel.text(x, y, text, 7, system_font.font)


    # ショップ選択
    # *************************************************************************
    def shop_ui_item(shop_ui_item:XUSelectItem):
        area = shop_ui_item.area
        pyxel.text(area.x, area.y, shop_ui_item.text, 7, system_font.font)

        if shop_ui_item.selected:
            hand_cursor.draw(area.x, area.y+4)

    def shop_buy_item(shop_buy_item:XUSelectItem, parent_enable:bool):
        buy_menu = shop_buy_item.find_parent_by_id("buy_menu")
        buy_num = XUSelectInfo(buy_menu.find_by_id("buy_num"))

        # 商品名
        area = shop_buy_item.area
        pyxel.text(area.x, area.y, shop_buy_item.text, 7, system_font.font)

        # お値段
        price = int(shop_buy_item.value) * int(buy_num.action)
        match buy_num.action:  # 割引
            case "4":
                price -= price * 26 // 256
            case "10":
                price -= price * 51 // 256
        price_text = XUTextUtil.format_zenkaku(price)
        x,y = area.aligned_pos(system_font.text_width(price_text)+8, 0, XURect.Align.RIGHT)
        pyxel.text(x, area.y, price_text, 7, system_font.font)

        if shop_buy_item.selected and parent_enable:
            hand_cursor.draw(area.x, area.y+4)


    # かう・うる・でるの選択
    # -----------------------------------------------------
    @shop_select.list("shop_act_list", "shop_ui_item")
    def shop_act_list(shop_act_list:select.List, event:XUEvent):
        # 一時的にdisableになることがある
        if shop_act_list.enable == False:
            return

        # メニューアイテム表示
        for item in shop_act_list.items:
            shop_ui_item(item)

        shop_act_list.select_by_event(event.trg, *XUEvent.Key.LEFT_RIGHT())
        if XUEvent.Key.BTN_A in event.trg:
            match shop_act_list.action:
                case "buy":
                    win = XUWinBase.find_parent_win(shop_act_list)
                    shop_act_list.enable = False
                    buy_menu= win.open("buy_menu")

                    # 販売アイテム設定
                    buy_list = buy_menu.find_by_id("buy_list")
                    buy_list.enable = False  # イベントはNumが決まってから
                    buy_list_db = BuyList(1)
                    for data in buy_list_db.data:
                        item = XUElem.new(template.xmlui, "shop_buy_item")
                        item.set_text(data["name"])
                        item.value = data["buy"]
                        buy_list.add_child(item)
                case "sell":
                    pass
                case "exit":
                    # バトルへ
                    pass

    # 個数を選択
    # -----------------------------------------------------
    @shop_select.list("buy_num", "shop_ui_item")
    def buy_num(buy_num:select.List, event:XUEvent):
        for item in buy_num.items:
            shop_ui_item(item)

        # 価格を変動させる
        buy_num.select_by_event(event.trg, *XUEvent.Key.LEFT_RIGHT())

        if XUEvent.Key.BTN_A in event.trg:
            buy_menu = buy_num.find_parent_by_id("buy_menu")
            buy_list = buy_menu.find_by_id("buy_list")
            buy_list.enable = True

        # 戻る
        if XUEvent.Key.BTN_B in event.trg:
            buy_num.close()

            # enableにしていたメニューを元に戻す
            win = XUWinBase.find_parent_win(buy_num)
            shop_act_list = win.find_by_id("shop_act_list")
            shop_act_list.enable = True

    @shop_select.list("buy_list", "shop_buy_item")
    def buy_list(buy_list:select.List, event:XUEvent):
        for item in buy_list.items:
            shop_buy_item(item, buy_list.enable)

        buy_list.select_by_event(event.trg, *XUEvent.Key.UP_DOWN())

        # 戻る
        if XUEvent.Key.BTN_B in event.trg:
            buy_list.enable = False

