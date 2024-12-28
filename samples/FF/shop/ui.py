import pyxel

from xmlui.core import XMLUI,XUElem,XUTemplate,XUEvent,XUSelectItem,XUWinBase,XUSelectInfo,XUTextUtil,XURect
from xmlui.lib import select,text
from system import system_font, hand_cursor

from db import user_data
from shop.buy_list import BuyList

def ui_init(template:XUTemplate):
    shop_select = select.Decorator(template)
    shop_text = text.Decorator(template)

    # 基本ラベル
    @shop_text.label("label")
    def label(label:text.Label, event:XUEvent):
        text = XUTextUtil.format_zenkaku(label.text, {"gil":user_data.gil})
        x, y = label.aligned_pos(system_font, text)
        pyxel.text(x, y, text, 7, system_font.font)

    # ショップ選択
    # *************************************************************************
    # 基本選択物
    def shop_ui_item(shop_ui_item:XUSelectItem):
        area = shop_ui_item.area
        pyxel.text(area.x, area.y, shop_ui_item.text, 7, system_font.font)

        if shop_ui_item.selected:
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
            shop_act_win = XUWinBase.find_parent_win(shop_act_list)
            shop_act_list.enable = False
            match shop_act_list.action:
                case "buy":
                    buy_menu= shop_act_win.open("buy_menu")

                    # 販売アイテム設定
                    buy_list = buy_menu.find_by_id("buy_list")
                    buy_list.enable = False  # カーソル移動は個数を決定したあと
                    buy_list_db = BuyList(1)
                    for data in buy_list_db.data:
                        item = XUElem.new(shop_act_list.xmlui, "shop_buy_item")
                        item.set_text(data["name"])
                        item.value = data["buy"]  # 価格
                        buy_list.add_child(item)

                    # メッセージ更新
                    set_shop_msg(buy_list.xmlui, "なににいたしましょうか？")

                case "sell":
                    sell_menu= shop_act_win.open("sell_menu")
                case "exit":
                    # バトルへ
                    pass

    # かうメニュー
    # *************************************************************************
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

            # メッセージ更新
            set_shop_msg(buy_num.xmlui, "いらっしゃい どのようなごようけんで？")

    # 購入できるアイテムのリスト
    # -----------------------------------------------------
    # 購入金額算出
    def get_price(buy_menu:XUElem, buy_item:XUElem) -> int:
        buy_num = XUSelectInfo(buy_menu.find_by_id("buy_num"))

        price = int(buy_item.value) * int(buy_num.action)
        match buy_num.action:  # 割引
            case "4":
                price -= price * 26 // 256
            case "10":
                price -= price * 51 // 256
        return price

    # 購入アイテムリスト
    def shop_buy_item(shop_buy_item:XUSelectItem, parent_enable:bool):
        buy_menu = shop_buy_item.find_parent_by_id("buy_menu")

        # 商品名
        area = shop_buy_item.area
        pyxel.text(area.x, area.y, shop_buy_item.text, 7, system_font.font)

        # お値段
        price_text = XUTextUtil.format_zenkaku(get_price(buy_menu, shop_buy_item))
        x,y = area.aligned_pos(system_font.text_width(price_text)+8, 0, XURect.Align.RIGHT)
        pyxel.text(x, area.y, price_text, 7, system_font.font)

        if shop_buy_item.selected and parent_enable:
            hand_cursor.draw(area.x, area.y+4)

    # 購入アイテム選択
    @shop_select.list("buy_list", "shop_buy_item")
    def buy_list(buy_list:select.List, event:XUEvent):
        for item in buy_list.items:
            shop_buy_item(item, buy_list.enable)

        buy_list.select_by_event(event.trg, *XUEvent.Key.UP_DOWN())
        if XUEvent.Key.BTN_A in event.trg:
            buy_menu = buy_list.find_parent_by_id("buy_menu")
            price = get_price(buy_menu, buy_list.selected_item)
            user_data.gil -= price

            # メッセージ更新
            msg = text.Msg(buy_list.xmlui.find_by_id("shop_msg"))
            msg.clear_pages()
            msg.append_msg("ありがとうございます ほかには？")

        # 戻る
        if XUEvent.Key.BTN_B in event.trg:
            buy_list.enable = False

            # メッセージ更新
            set_shop_msg(buy_list.xmlui, "なににいたしましょうか？")

    # メッセージ
    # *************************************************************************
    # メッセージ設定
    def set_shop_msg(xmlui:XMLUI, text_:str):
        msg = text.Msg(xmlui.find_by_id("shop_msg"))
        msg.clear_pages()
        msg.append_msg(text_)

    @shop_text.msg("shop_msg", "speed")
    def shop_msg(shop_msg:text.Msg, event:XUEvent):
        area = shop_msg.area
        x, y = area.aligned_pos(0, system_font.size, XURect.Align.LEFT, XURect.Align.from_str(shop_msg.attr_str("valign", "center")))
        pyxel.text(x, y, shop_msg.current_page.text, 7, system_font.font)

