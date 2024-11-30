import pyxel

from xmlui_pyxel import xuc,win,font,input,label

# xmlui_pyxelの初期化
# *********************************************************
from xmlui_pyxel import xuc
import xmlui_pyxel

# ライブラリのインスタンス化
xmlui = xuc.XMLUI()

# キー定義。設定しない場合はデフォルトが使われる
# input.INPUT_LIST[input.BTN_A] = [pyxel.KEY_A]

# 初期化セット
xmlui_pyxel.initialize(xmlui,
        inputlist_dict = input.INPUT_LIST,
        font_path = "assets/font/b12.bdf"
    )

# (ライブラリ開発用)
xmlui.debug.level = xmlui.debug.DEBUG_LEVEL_LIB

# UIテンプレートXMLの読み込み
UI_TEMPLATE = "ui_template"
xmlui.template_fromfile("assets/ui/test.xml", "ui_template")


def draw_menu_cursor(state:xuc.XUStateRO, x:int, y:int):
    tri_size = 6
    left =state.area.x
    top  = state.area.y+2
    pyxel.tri(left, top, left, top+tri_size, left+tri_size//2, top+tri_size//2, 7)


# コマンドメニュー
# *****************************************************************************
# 更新
# ---------------------------------------------------------
@win.menu_update_bind(xmlui, "menu_win", "menu_row", "menu_item")
def menu_win_update(menu_win:win.Menu, event:xuc.XUEvent):
    item_w, item_h = menu_win.attr_int("item_w"), menu_win.attr_int("item_h")
    menu_win.arrange_items(item_w, item_h)

    # メニュー選択
    selected_item = menu_win.select_by_event(*input.CURSOR)

    # 選択アイテムの表示
    if input.BTN_A in event.trg:
        # メッセージウインドウ表示
        if selected_item == "speak":
            selected_item.open(UI_TEMPLATE, "win_message")

        # dialウインドウ表示
        if selected_item == "dial":
            selected_item.open(UI_TEMPLATE, "win_dial").set_pos(8, 2)

    # 閉じる
    if input.BTN_B in event.trg:
        menu_win.close()

# 描画
# ---------------------------------------------------------
@win.menu_draw_bind(xmlui, "menu_win", "menu_row", "menu_item")
def menu_win_draw(menu_win:win.MenuRO, event:xuc.XUEvent):
    menu_win.draw()
    draw_menu_cursor(menu_win.selected_item, 0, 0)


# メッセージウインドウ
# *****************************************************************************
# 更新
# ---------------------------------------------------------
@win.msg_update_bind(xmlui, "msg_win", "msg_text")
def msg_win_update(msg_win:win.Msg, event:xuc.XUEvent):
    if input.BTN_A in event.trg or input.BTN_B in event.trg:
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
def msg_win_draw(msg_win:win.MsgRO, event:xuc.XUEvent):
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
def win_dial_update(win_dial:xuc.XUState, event:xuc.XUEvent):
    # 数値変更
    dial = xuc.XUDial(win_dial, 5)
    dial.change_by_event(event.trg, *input.CURSOR)

    # 確定
    if input.BTN_A in event.trg:
        win_dial.open(UI_TEMPLATE, "yes_no", "dial_yes_no")
        # dial_win.close() # 確定でも閉じる

    # 閉じる
    if input.BTN_B in event.trg:
        win_dial.close()

@xmlui.draw_bind("win_dial")
def dial_win_draw(dial_win:xuc.XUStateRO, event:xuc.XUEvent):
    frame_color = 10 if event.active else 7
    pyxel.rect(dial_win.area.x, dial_win.area.y, dial_win.area.w, dial_win.area.h, 12)
    pyxel.rectb(dial_win.area.x, dial_win.area.y, dial_win.area.w, dial_win.area.h, frame_color)

    # 数値表示
    dial = xuc.XUDialRO(dial_win)
    for i,digit in enumerate(dial.zenkaku_digits):
        pyxel.text(dial_win.area.x+3+(4-i)*font.size, dial_win.area.y+2, digit, 2 if dial.edit_pos == i else 7, font.data)

@win.list_update_bind(xmlui, "yes_no", "yes_no_item")
def dial_yes_no_update(list_win:win.List, event:xuc.XUEvent):
    item_h = list_win.attr_int("item_h")
    list_win.arrange_items(0, item_h)

    # メニュー選択
    selected_item = list_win.select_by_event(*input.UP_DOWN)

    # 閉じる
    if input.BTN_B in event.trg:
        list_win.close()

    # 決定
    if input.BTN_A in event.trg:
        # Yes時処理
        if selected_item == "yes":
#            test_params["age"] = core.XUDialRO(list_win.find_by_tagR("win_dial")).number
            list_win.xmlui.close("menu_command")

        # No時処理
        if selected_item == "no":
            list_win.close()


@win.list_draw_bind(xmlui, "yes_no", "yes_no_item")
def dial_yes_no_draw(list_win:win.ListRO, event:xuc.XUEvent):
    list_win.draw()
    draw_menu_cursor(list_win.selected_item, 0, 0)


@label.nflabel_draw_bind(xmlui, "label")
def label_draw(label:label.NFLabelRO, event:xuc.XUEvent):
    label.draw()
