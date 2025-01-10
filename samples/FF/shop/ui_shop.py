import pyxel

from xmlui.core import XMLUI,XUEvent,XUSelectItem,XUWinBase,XUTextUtil,XURect
from xmlui.lib import select,text
from system import system_font, hand_cursor

from db import user_data

def ui_init(xmlui:XMLUI):
    shop_select = select.Decorator(xmlui)
    shop_text = text.Decorator(xmlui)

    # 基本ラベル
    @shop_text.label("label")
    def label(label:text.XULabel, event:XUEvent):
        text = XUTextUtil.format_zenkaku(label.text, {"gil":user_data.gil})
        x, y = label.aligned_pos(system_font, text)
        pyxel.text(x, y, text, 7, system_font.font)

    # ショップ選択
    # *************************************************************************
    # 基本選択物
    def shop_act_item(shop_act_item:XUSelectItem):
        area = shop_act_item.area
        pyxel.text(area.x, area.y, shop_act_item.text, 7, system_font.font)

        if shop_act_item.selected:
            hand_cursor.draw(area.x, area.y+4)

    # かう・うる・でるの選択
    # -----------------------------------------------------
    @shop_select.row_list("shop_act_list", "shop_ui_item")
    def shop_act(shop_act:select.XURowList, event:XUEvent):
        # 一時的にdisableになることがある
        if shop_act.enable == False:
            return

        # メニューアイテム表示
        for item in shop_act.items:
            shop_act_item(item)

        shop_act.select_by_event(event.repeat, *XUEvent.Key.LEFT_RIGHT())
        if XUEvent.Key.BTN_A in event.trg:
            shop_act_win = XUWinBase.find_parent_win(shop_act)
            shop_act.enable = False
            match shop_act.action:
                case "buy":
                    return "start_buy"
                case "sell":
                    return "start_sell"
                case "exit":
                    # バトルへ
                    return "exit"

    # メッセージ
    # *************************************************************************
    @shop_text.msg("shop_msg", "speed")
    def shop_msg(shop_msg:text.XUMsg, event:XUEvent):
        area = shop_msg.area
        x, y = area.aligned_pos(0, system_font.size, XURect.Align.LEFT, XURect.Align.from_str(shop_msg.attr_str("valign", "center")))
        pyxel.text(x, y, shop_msg.current_page.text, 7, system_font.font)


# メッセージ設定
# *************************************************************************
def set_shop_msg(xmlui:XMLUI, text_:str):
    msg = text.XUMsg(xmlui.find_by_id("shop_msg"))
    msg.clear_pages()
    msg.append_msg(text_)
