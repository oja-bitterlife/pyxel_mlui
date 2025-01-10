import pyxel

from xmlui.core import XMLUI,XUElem,XUEvent,XUSelectItem,XUWinInfo,XUSelectInfo,XUTextUtil,XURect
from xmlui.lib import select,text
from system import system_font, hand_cursor

from db import user_data
from FF.ui_common import get_world_clip
from FF.shop.shop_list import SellList
from FF.shop.ui_shop import set_shop_msg

def ui_init(xmlui:XMLUI):
    shop_select = select.Decorator(xmlui)

    # 個数選択
    # *************************************************************************
    # 基本選択物
    def sell_num_item(shop_ui_item:XUSelectItem):
        area = shop_ui_item.area
        pyxel.text(area.x, area.y, shop_ui_item.text, 7, system_font.font)

        if shop_ui_item.selected:
            hand_cursor.draw(area.x, area.y+4)

    # 個数を選択
    # -----------------------------------------------------
    @shop_select.row_list("sell_num", "shop_ui_item")
    def sell_num(sell_num:select.XURowList, event:XUEvent):
        for item in sell_num.items:
            sell_num_item(item)

        # 価格を変動させる
        sell_num.select_by_event(event.repeat, *XUEvent.Key.LEFT_RIGHT())

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
            win = XUWinInfo.find_parent_win(sell_num)
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
    def sell_item(sell_item:XUSelectItem, parent_enable:bool):
        area = sell_item.area

        # ウインドウが表示されてる場所のみ描画
        clip = get_world_clip(XUWinInfo.find_parent_win(sell_item))
        if clip.bottom < area.y+system_font.size:
            return

        # カーソルは常に表示
        if sell_item.selected and parent_enable:
            hand_cursor.draw(area.x, area.y+4)

        # 個数(0の場合は空欄)
        num = sell_item.attr_int("num")
        if num == 0:
            return

        # 商品名
        num_text = ("　" if num < 10 else "") + XUTextUtil.format_zenkaku(num)
        pyxel.text(area.x+8, area.y, sell_item.text, 7, system_font.font)
        pyxel.text(area.x+8+9*system_font.size, area.y, "：", 7, system_font.font)
        pyxel.text(area.x+8+9*system_font.size+8, area.y, num_text, 7, system_font.font)

    # 売却アイテム選択
    SELL_WAIT_ATTR = "wait_sell"
    @shop_select.grid("sell_list", "shop_sell_item")
    def sell_list(sell_list:select.XUGrid, event:XUEvent):
        for item in sell_list.items:
            sell_item(item, sell_list.enable)

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
        sell_list.select_by_event(event.repeat, *XUEvent.Key.CURSOR())
        if XUEvent.Key.BTN_A in event.trg:
            # 0個以上の時だけ決定できる
            num = sell_list.selected_item.attr_int("num")
            if num > 0:
                price_text = XUTextUtil.format_zenkaku(get_sell_price(sell_list.selected_item))
                price_text = "　"*(7-len(price_text)) + price_text
                msg = text.XUMsg(sell_list.xmlui.find_by_id("shop_msg"))
                msg.clear_pages()
                msg.append_msg(f"それなら {price_text}ギルになります")

                # 決定待ちへ
                sell_list.set_attr(SELL_WAIT_ATTR, True)

        # 戻る
        if XUEvent.Key.BTN_B in event.trg:
            sell_list.enable = False
            set_shop_msg(sell_list.xmlui, "なににいたしましょうか？")


# うるメニュースタート
# *************************************************************************
def init_sell_list(xmlui:XMLUI):
    sell_menu = XUWinInfo.find_parent_win(xmlui.find_by_id("shop_act_list")).open("sell_menu")

    sell_list = sell_menu.find_by_id("sell_list")
    sell_list.enable = False  # イベントはNumが決まってから
    sell_list_data = SellList.get()
    for data in sell_list_data:
        item = XUElem.new(sell_menu.xmlui, "shop_sell_item")
        item.set_attr("item_id", data["item_id"])
        item.set_text(data["name"])
        item.value = data["sell"]  # 売却価格
        item.set_attr("num", data["num"])
        sell_list.add_child(item)

    for _ in range(8*2-len(sell_list_data)):
        item = XUElem.new(sell_menu.xmlui, "shop_sell_item")
        sell_list.add_child(item)

    # メッセージ更新
    set_shop_msg(sell_menu.xmlui, "なにを うりますか？")
