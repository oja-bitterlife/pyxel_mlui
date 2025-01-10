import pyxel

from xmlui.core import XMLUI,XUElem,XUEvent,XUSelectItem,XUWinBase,XUSelectInfo,XUTextUtil,XURect
from xmlui.lib import select,text
from system import system_font, hand_cursor

from db import user_data
from FF.ui_common import get_world_clip
from FF.shop.shop_list import BuyList
from FF.shop.ui_shop import set_shop_msg


def ui_init(xmlui:XMLUI):
    buy_select = select.Decorator(xmlui)

    # 基本選択物
    def buy_num_item(shop_ui_item:XUSelectItem):
        area = shop_ui_item.area
        pyxel.text(area.x, area.y, shop_ui_item.text, 7, system_font.font)

        if shop_ui_item.selected:
            hand_cursor.draw(area.x, area.y+4)

    # 個数を選択
    # -----------------------------------------------------
    @buy_select.row_list("buy_num", "shop_ui_item")
    def buy_num(buy_num:select.XURowList, event:XUEvent):
        for item in buy_num.items:
            buy_num_item(item)

        # 価格を変動させる
        buy_num.select_by_event(event.repeat, *XUEvent.Key.LEFT_RIGHT())

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
    def buy_item(buy_item:XUSelectItem, parent_enable:bool):
        buy_menu = buy_item.find_parent_by_id("buy_menu")

        area = buy_item.area

        # ウインドウが表示されてる場所のみ描画
        clip = get_world_clip(XUWinBase.find_parent_win(buy_item))
        if clip.bottom < area.y:
            return

        # 商品名
        pyxel.text(area.x, area.y, buy_item.text, 7, system_font.font)

        # お値段
        price_text = XUTextUtil.format_zenkaku(get_buy_price(buy_menu, buy_item))
        x,y = area.aligned_pos(system_font.text_width(price_text)+8, 0, XURect.Align.RIGHT)
        pyxel.text(x, area.y, price_text, 7, system_font.font)

        if buy_item.selected and parent_enable:
            hand_cursor.draw(area.x, area.y+4)

    # 購入アイテム選択
    @buy_select.list("buy_list", "shop_buy_item")
    def buy_list(buy_list:select.XUList, event:XUEvent):
        for item in buy_list.items:
            buy_item(item, buy_list.enable)

        buy_list.select_by_event(event.repeat, *XUEvent.Key.UP_DOWN())
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


# かうメニュースタート
# *************************************************************************
def init_buy_list(xmlui:XMLUI):
    buy_menu = XUWinBase.find_parent_win(xmlui.find_by_id("shop_act_list")).open("buy_menu")

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
