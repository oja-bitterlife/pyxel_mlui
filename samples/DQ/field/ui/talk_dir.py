import pyxel

from xmlui.core import XMLUI,XUEvent,XUWinInfo,XUSelectItem
from xmlui.lib import select

from system_dq import system_font
from ui_common import get_world_clip,draw_menu_cursor,get_text_color

def ui_init(xmlui:XMLUI):
    field_select = select.Decorator(xmlui)

    # 会話方向
    # ---------------------------------------------------------
    def dir_item(dir_item:XUSelectItem):
        col = get_text_color()

        # ウインドウのクリップ状態に合わせて表示する
        if dir_item.area.y < get_world_clip(XUWinInfo.find_parent_win(dir_item)).bottom:
            pyxel.text(dir_item.area.x, dir_item.area.y, dir_item.text, col, system_font.font)

        # カーソル表示
        if dir_item.selected and dir_item.enable:
            draw_menu_cursor(dir_item, -5, 0)

    @field_select.list("dir_select", "dir_item")
    def dir_select(dir_select:select.XUList, event:XUEvent):
        # 各アイテムの描画
        for item in dir_select.items:
            dir_item(item)

        # 会話ウインドウは特別な配置
        if XUEvent.Key.UP in event.trg:
            dir_select.select(0)
        if XUEvent.Key.LEFT in event.trg:
            dir_select.select(1)
        if XUEvent.Key.RIGHT in event.trg:
            dir_select.select(2)
        if XUEvent.Key.DOWN in event.trg:
            dir_select.select(3)

        if XUEvent.Key.BTN_A in event.trg:
            dir_win = XUWinInfo.find_parent_win(dir_select)
            dir_win.setter.start_close()
            return f"start_talk_{dir_select.action}"

        # 閉じる
        if XUEvent.Key.BTN_B in event.trg:
            XUWinInfo.find_parent_win(dir_select).setter.start_close()
