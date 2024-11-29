import pyxel

from xmlui_pyxel import core, win,font

# xmlui_pyxelの初期化
# *********************************************************
from xmlui_pyxel import core
import xmlui_pyxel

# UIで使うフォント設定

# ライブラリのインスタンス化
xmlui = core.XMLUI()
xmlui_pyxel.initialize(xmlui, "assets/font/b12.bdf", 12)  # 楽したいセット

# (ライブラリ開発用)
xmlui.debug.level = xmlui.debug.DEBUG_LEVEL_LIB

# UIテンプレートXMLの読み込み
xmlui.template_fromfile("assets/ui/test.xml", "ui_template")


def draw_menu_cursor(state:core.XUStateRO, x:int, y:int):
    tri_size = 6
    left =state.area.x
    top  = state.area.y+2
    pyxel.tri(left, top, left, top+tri_size, left+tri_size//2, top+tri_size//2, 7)


# 入力待ち
# *****************************************************************************
@xmlui.update_bind("root")
def my_ui_update(my_ui:core.XUState, event:core.XUEvent):
    # メインメニューを開く
    if "button_a" in event.trg:
        my_ui.open("ui_template", "menu_command")


# コマンドメニュー
# *****************************************************************************
# 更新
# ---------------------------------------------------------
@win.menu_update_bind(xmlui, "menu_win", "menu_row", "menu_item")
def menu_win_update(menu_win:win.Menu, event:core.XUEvent):
    item_w, item_h = menu_win.attr_int("item_w"), menu_win.attr_int("item_h")
    menu_win.arrange_items(item_w, item_h)

    # メニュー選択
    selected_item = menu_win.select_by_event("left", "right", "up", "down")

    # 選択アイテムの表示
    if "button_a" in event.trg:
        # メッセージウインドウ表示
        if selected_item == "speak":
            selected_item.open("ui_template", "win_message")

        # dialウインドウ表示
        if selected_item == "dial":
            selected_item.open("ui_template", "win_dial").set_pos(8, 2)

    # 閉じる
    if "button_b" in event.trg:
        menu_win.close()

# 描画
# ---------------------------------------------------------
@win.menu_draw_bind(xmlui, "menu_win", "menu_row", "menu_item")
def menu_win_draw(menu_win:win.MenuRO, event:core.XUEvent):
    bg_color = 12
    frame_color = 10 if event.active else 7
    title  = menu_win.attr_str("title")

    menu_win.draw()
    draw_menu_cursor(menu_win.selected_item, 0, 0)

    # メニュータイトル
    if title:
        str_w = font.font_size*len(title)
        text_x = menu_win.area.x+(menu_win.area.w-str_w)/2
        pyxel.rect(text_x,menu_win.area.y, str_w, font.font_size, bg_color)
        pyxel.text(text_x, menu_win.area.y-2, title, frame_color, font.font)


# メッセージウインドウ
# *****************************************************************************
# 更新
# ---------------------------------------------------------
@win.msg_update_bind(xmlui, "msg_win", "msg_text")
def msg_win_update(msg_win:win.Msg, event:core.XUEvent):
    if "button_a" in event.trg or "button_b" in event.trg:
        action = msg_win.page.check_action()
        if action == "close":
            msg_win.close("menu_command")  # メニューごと閉じる
        elif action == "finish":
            msg_win.page.finish()
        elif action == "next_page":
            msg_win.page.next_page()

# 描画
# ---------------------------------------------------------
@win.msg_draw_bind(xmlui, "msg_win", "msg_text")
def msg_win_draw(msg_win:win.MsgRO, event:core.XUEvent):
    msg_win.draw()

    # カーソル表示
    if msg_win.page.is_next_wait:
        tri_size = 6
        center_x = msg_win.area.center_x(tri_size)
        bottom = msg_win.area.bottom(tri_size) - 2
        pyxel.tri(center_x, bottom, center_x+tri_size, bottom, center_x+tri_size//2, bottom+tri_size//2, 7)


# ダイアル
# *****************************************************************************
@xmlui.update_bind("win_dial")
def win_dial_update(win_dial:core.XUState, event:core.XUEvent):
    # 数値変更
    dial = core.XUDial(win_dial, 5)
    dial.change_by_event(event.trg, "left", "right", "up", "down")

    # 確定
    if "button_a" in event.trg:
        win_dial.open("ui_template", "yes_no", "dial_yes_no")
        # dial_win.close() # 確定でも閉じる

    # 閉じる
    if "button_b" in event.trg:
        win_dial.close()

@xmlui.draw_bind("win_dial")
def dial_win_draw(dial_win:core.XUStateRO, event:core.XUEvent):
    frame_color = 10 if event.active else 7
    pyxel.rect(dial_win.area.x, dial_win.area.y, dial_win.area.w, dial_win.area.h, 12)
    pyxel.rectb(dial_win.area.x, dial_win.area.y, dial_win.area.w, dial_win.area.h, frame_color)

    # 数値表示
    dial = core.XUDialRO(dial_win)
    for i,digit in enumerate(dial.zenkaku_digits):
        pyxel.text(dial_win.area.x+3+(4-i)*font.font_size, dial_win.area.y+2, digit, 2 if dial.edit_pos == i else 7, font.font)

@win.list_update_bind(xmlui, "yes_no", "yes_no_item")
def dial_yes_no_update(list_win:win.List, event:core.XUEvent):
    item_h = list_win.attr_int("item_h")
    list_win.arrange_items(0, item_h)

    # メニュー選択
    selected_item = list_win.select_by_event("up", "down")

    # 閉じる
    if "button_b" in event.trg:
        list_win.close()

    # 決定
    if "button_a" in event.trg:
        # Yes時処理
        if selected_item == "yes":
#            test_params["age"] = core.XUDialRO(list_win.find_by_tagR("win_dial")).number
            list_win.xmlui.close("menu_command")

        # No時処理
        if selected_item == "no":
            list_win.close()


@win.list_draw_bind(xmlui, "yes_no", "yes_no_item")
def dial_yes_no_draw(list_win:win.ListRO, event:core.XUEvent):
    list_win.draw()
    draw_menu_cursor(list_win.selected_item, 0, 0)
