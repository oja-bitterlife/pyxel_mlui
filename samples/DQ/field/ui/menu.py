import pyxel

from xmlui.core import XMLUI,XUEvent,XUWinInfo,XUSelectItem
from xmlui.lib import select,text

from ui_common import get_world_clip,draw_menu_cursor,KOJICHU_COL,get_text_color
from system_dq import system_font


def ui_init(xmlui:XMLUI):
    field_select = select.Decorator(xmlui)
    field_text = text.Decorator(xmlui)

    # コマンドメニュー
    # ---------------------------------------------------------
    def menu_item(menu_item:XUSelectItem):
        # ウインドウのクリップ状態に合わせて表示する
        if menu_item.area.y < get_world_clip(XUWinInfo.find_parent_win(menu_item)).bottom:
            col = KOJICHU_COL if menu_item.value == "工事中" else get_text_color()
            pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, col, system_font.font)

            # カーソル表示
            if menu_item.selected and menu_item.enable:
                draw_menu_cursor(menu_item, 0, 0)

    @field_select.grid("menu_grid", "menu_item")
    def menu_grid(menu_grid:select.XUGrid, event:XUEvent):
        # 各アイテムの描画
        for item in menu_grid.items:
            menu_item(item)

        # メニュー選択
        menu_grid.select_by_event(event.trg, *XUEvent.Key.CURSOR())

        # 選択アイテムの表示
        if XUEvent.Key.BTN_A in event.trg:
            match menu_grid.action:
                case "talk":
                    menu_grid.open("talk_dir")
                case "tools":
                    menu_grid.open("tools")
                case "stairs":
                    return "down_stairs"
                case "door":
                    return "open_door"
                case _:
                    menu_grid.xmlui.popup("under_construct")

        # アイテムの無効化(アイテムカーソル用)
        is_message_oepn = menu_grid.xmlui.exists_id("message")
        for item in menu_grid.items:
            item.enable = event.is_active and not is_message_oepn

        # 閉じる
        if XUEvent.Key.BTN_B in event.trg:
            XUWinInfo.find_parent_win(menu_grid).setter.start_close()

    # コマンドメニューのタイトル
    @field_text.label("title")
    # ---------------------------------------------------------
    def title(title:text.XULabel, event:XUEvent):
        clip = get_world_clip(XUWinInfo.find_parent_win(title)).intersect(title.area)
        pyxel.rect(title.area.x, title.area.y, title.area.w, clip.h, 0)  # タイトルの下地

        col = get_text_color()

        # テキストはセンタリング
        if title.area.y < clip.bottom:  # world座標で比較
            x, y = title.aligned_pos(system_font)
            pyxel.text(x, y-1, title.text, col, system_font.font)


    # 子メニューごとのタイトル(コマンドメニューと少し場所がずれる)
    # ---------------------------------------------------------
    @field_text.label("child_menu_title")
    def child_menu_title(child_menu_title:text.XULabel, event:XUEvent):
        clip = get_world_clip(XUWinInfo.find_parent_win(child_menu_title)).intersect(child_menu_title.area)
        clip.h = max(clip.h, 4)  # フレームを隠すように
        pyxel.rect(child_menu_title.area.x, child_menu_title.area.y, child_menu_title.area.w, clip.h, 0)  # タイトルの下地

        col = get_text_color()

        # テキストはセンタリングで常に表示
        x, y = child_menu_title.aligned_pos(system_font)
        pyxel.text(x, y-1, child_menu_title.text, col, system_font.font)
