import pyxel

from xmlui.core import XUTemplate,XUEvent,XUWinBase,XUSelectItem,XUTextUtil,XUElem
from xmlui.lib import select
from xmlui_modules import dq
from ui_common import system_font,get_world_clip,draw_menu_cursor

from db import user_data,tools_data

def ui_init(template:XUTemplate):
    field_select = select.Decorator(template)

    # どうぐメニュー
    # ---------------------------------------------------------
    def tools_item(tools_item:XUSelectItem):
        # ウインドウのクリップ状態に合わせて表示する
        if tools_item.area.y < get_world_clip(XUWinBase.find_parent_win(tools_item)).bottom():
            pyxel.text(6+tools_item.area.x, tools_item.area.y, tools_item.text, 7, system_font.font)

        # カーソル表示
        if tools_item.selected and tools_item.enable:
            draw_menu_cursor(tools_item, 0, 0)

    @field_select.list("tools_list", "tools_item")
    def tools_list(tools_list:select.List, event:XUEvent):
        # アイテム表示の準備
        if event.on_init:
            tools_list.clear_children()
            tools_list.add_child(XUElem(tools_list.xmlui, Element("tools_item")))
            # for 
            #             <tools_item action="やくそう">やくそう</tools_item>


        # 各アイテムの描画
        for item in tools_list.items:
            tools_item(item)

        tools_list.select_by_event(event.trg, *XUEvent.Key.UP_DOWN())

        if XUEvent.Key.BTN_A in event.trg:
            try:
                data = tools_data.get_data(tools_list.action)
            except:
                tools_list.xmlui.popup("under_construct")
                return

            # 効果発現
            msg = tools_effect(data)

            # メッセージウインドウを開く
            XUWinBase.find_parent_win(tools_list).start_close()
            msg_win = tools_list.xmlui.find_by_id("menu").open("message")
            msg_text = dq.MsgDQ(msg_win.find_by_id("msg_text"))
            msg_text.append_msg(msg)  # systemメッセージ
        
        # 閉じる
        if XUEvent.Key.BTN_B in event.trg:
            XUWinBase.find_parent_win(tools_list).start_close()

    # どうぐ処理
    # ---------------------------------------------------------
    def tools_effect(data) -> str:
        match data["type"]:
            case "やくそう":
                value = data["value"]
                user_data.hp += value
                return XUTextUtil.format_zenkaku(data["msg"], {"value":value})

        return "なにもおこらなかった"
