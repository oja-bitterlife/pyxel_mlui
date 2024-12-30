import pyxel

from xmlui.core import XMLUI,XUElem,XUTemplate,XUEvent,XUSelectItem,XUWinBase,XUSelectInfo,XUTextUtil,XURect
from xmlui.lib import select,text
from system import system_font, hand_cursor

from db import user_data
from FF.shop.shop_list import BuyList,SellList

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
                    init_buy_list(shop_act_win.open("buy_menu"))  # 販売アイテム設定
                case "sell":
                    init_sell_list(shop_act_win.open("sell_menu"))  # 買い取りアイテム設定
                case "exit":
                    # バトルへ
                    pass

    # かうメニュー
    # *************************************************************************
    def init_buy_list(buy_menu:XUElem):
        buy_list = buy_menu.find_by_id("buy_list")
        buy_list.enable = False  # イベントはNumが決まってから
        buy_list_data = BuyList.get(1)
        for data in buy_list_data:
            item = XUElem.new(buy_menu.xmlui, "shop_buy_item")
            item.set_attr("item_id", data["item_id"])
            item.set_text(data["name"])
            item.value = data["buy"]
            buy_list.add_child(item)

        # メッセージ更新
        set_shop_msg(buy_menu.xmlui, "なににいたしましょうか？")

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

    # アイテム購入
    # -----------------------------------------------------
    # 購入金額算出
    def get_buy_price(buy_menu:XUElem, buy_item:XUElem) -> int:
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
        price_text = XUTextUtil.format_zenkaku(get_buy_price(buy_menu, shop_buy_item))
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
            price = get_buy_price(buy_menu, buy_list.selected_item)
            user_data.gil -= price

            # DBの更新
            buy_num = XUSelectInfo(buy_menu.find_by_id("buy_num"))
            BuyList.add(buy_list.selected_item.attr_int("item_id"), int(buy_num.action))

            # メッセージ更新
            msg = text.Msg(buy_list.xmlui.find_by_id("shop_msg"))
            msg.clear_pages()
            msg.append_msg("ありがとうございます ほかには？")

        # 戻る
        if XUEvent.Key.BTN_B in event.trg:
            buy_list.enable = False

            # メッセージ更新
            set_shop_msg(buy_list.xmlui, "なににいたしましょうか？")

    # うるメニュー
    # *************************************************************************
    def init_sell_list(buy_menu:XUElem):
        sell_list = buy_menu.find_by_id("sell_list")
        sell_list.enable = False  # イベントはNumが決まってから
        sell_list_data = SellList.get()
        for data in sell_list_data:
            item = XUElem.new(buy_menu.xmlui, "shop_sell_item")
            item.set_attr("item_id", data["item_id"])
            item.set_text(data["name"])
            item.value = data["sell"]  # 売却価格
            item.set_attr("num", data["num"])
            sell_list.add_child(item)

        for _ in range(8*2-len(sell_list_data)):
            item = XUElem.new(buy_menu.xmlui, "shop_sell_item")
            sell_list.add_child(item)

        # メッセージ更新
        set_shop_msg(buy_menu.xmlui, "なにを うりますか？")

    # 個数を選択
    # -----------------------------------------------------
    @shop_select.list("sell_num", "shop_ui_item")
    def sell_num(sell_num:select.List, event:XUEvent):
        for item in sell_num.items:
            shop_ui_item(item)

        # 価格を変動させる
        sell_num.select_by_event(event.trg, *XUEvent.Key.LEFT_RIGHT())

        if XUEvent.Key.BTN_A in event.trg:
            sell_menu = sell_num.find_parent_by_id("sell_menu")
            sell_list = sell_menu.find_by_id("sell_list")
            sell_list.enable = True

        # 戻る
        if XUEvent.Key.BTN_B in event.trg:
            # DBの更新
            sell_menu = sell_num.find_parent_by_id("sell_menu")
            sell_list = XUSelectInfo(sell_menu.find_by_id("sell_list"))
            SellList.set(1, [(item.attr_int("item_id"), item.attr_int("num")) for item in sell_list.items if item.attr_int("num") > 0])

            sell_num.close()

            # disableにしていたメニューを元に戻す
            win = XUWinBase.find_parent_win(sell_num)
            shop_act_list = win.find_by_id("shop_act_list")
            shop_act_list.enable = True

            # メッセージ更新
            set_shop_msg(sell_num.xmlui, "いらっしゃい どのようなごようけんで？")

    # アイテム売却
    # -----------------------------------------------------
    def get_sell_num(selected_item:XUSelectItem):
        sell_menu = selected_item.find_parent_by_id("sell_menu")
        sell_num = XUSelectInfo(sell_menu.find_by_id("sell_num"))

        return selected_item.attr_int("num") if sell_num.action == "all" else 1

    def get_sell_price(selected_item:XUSelectItem):
        value = selected_item.attr_int("value")
        return get_sell_num(selected_item) * value

    # 売却アイテムリスト表示
    def shop_sell_item(shop_sell_item:XUSelectItem, parent_enable:bool):
        area = shop_sell_item.area

        # カーソルは常に表示
        if shop_sell_item.selected and parent_enable:
            hand_cursor.draw(area.x, area.y+4)

        # 個数(0の場合は空欄)
        num = shop_sell_item.attr_int("num")
        if num == 0:
            return

        # 商品名
        num_text = ("　" if num < 10 else "") + XUTextUtil.format_zenkaku(num)
        pyxel.text(area.x+8, area.y, shop_sell_item.text, 7, system_font.font)
        pyxel.text(area.x+8+9*system_font.size, area.y, "：", 7, system_font.font)
        pyxel.text(area.x+8+9*system_font.size+8, area.y, num_text, 7, system_font.font)

    # 売却アイテム選択
    SELL_WAIT_ATTR = "wait_sell"
    @shop_select.grid("sell_list", "shop_sell_item")
    def sell_list(sell_list:select.Grid, event:XUEvent):
        for item in sell_list.items:
            shop_sell_item(item, sell_list.enable)

        # 決定待ち
        if sell_list.attr_bool(SELL_WAIT_ATTR):
            if XUEvent.Key.BTN_A in event.trg or XUEvent.Key.BTN_B in event.trg:
                # 売却決定
                if XUEvent.Key.BTN_A in event.trg:
                    # お金をふやす
                    user_data.gil += get_sell_price(sell_list.selected_item)

                    # 個数を減らす
                    sell_list.selected_item.set_attr("num", sell_list.selected_item.attr_int("num")-get_sell_num(sell_list.selected_item))

                # 戻る
                sell_list.set_attr(SELL_WAIT_ATTR, False)
                set_shop_msg(sell_list.xmlui, "なににいたしましょうか？")
            return

        # 所持アイテム選択
        sell_list.select_by_event(event.trg, *XUEvent.Key.CURSOR())
        if XUEvent.Key.BTN_A in event.trg:
            # 0個以上の時だけ決定できる
            num = sell_list.selected_item.attr_int("num")
            if num > 0:
                price_text = XUTextUtil.format_zenkaku(get_sell_price(sell_list.selected_item))
                price_text = "　"*(7-len(price_text)) + price_text
                msg = text.Msg(sell_list.xmlui.find_by_id("shop_msg"))
                msg.clear_pages()
                msg.append_msg(f"それなら {price_text}ギルになります")

                # 決定待ちへ
                sell_list.set_attr(SELL_WAIT_ATTR, True)

        # 戻る
        if XUEvent.Key.BTN_B in event.trg:
            sell_list.enable = False
            set_shop_msg(sell_list.xmlui, "なににいたしましょうか？")


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

