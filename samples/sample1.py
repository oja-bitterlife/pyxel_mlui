from xmlui_pyxel import xui

ui_template = xui.core.XMLUI.fromfile("assets/ui/test.xml")
ui_worker = xui.core.XMLUI.mkworker("my_ui")

import pyxel
# font = pyxel.Font("assets/font/b12.bdf")
font = xui.font
FONT_SIZE = xui.FONT_SIZE

# お試しパラメータ
test_params = {"name":"world", "age":10}

# 入力待ち
# *****************************************************************************
@ui_worker.update_bind("my_ui")
def my_ui_update(my_ui:xui.core.XUState, event:xui.core.XUEvent):
    # メインメニューを開く
    if "button_a" in event.trg:
        my_ui.open(ui_template, "menu_command")


# コマンドメニュー
# *****************************************************************************
# 更新
# ---------------------------------------------------------
@xui.win.menu_update_bind(ui_worker, "menu_win", "menu_row", "menu_item")
def menu_win_update(menu_win:xui.win.Menu, event:xui.XUEvent):
    item_w, item_h = menu_win.attr_int("item_w"), menu_win.attr_int("item_h")
    menu_win._grid_root.arrange_items(item_w, item_h)

    # メニュー選択
    selected_item = menu_win.select_by_event("left", "right", "up", "down")

    # 選択アイテムの表示
    if "button_a" in event.trg:
        # メッセージウインドウ表示
        if selected_item == "speak":
            selected_item.open(ui_template, "win_message")

        # dialウインドウ表示
        if selected_item == "dial":
            selected_item.open(ui_template, "win_dial").set_pos(8, 2)

    # 閉じる
    if "button_b" in event.trg:
        menu_win.close()

# 描画
# ---------------------------------------------------------
@xui.win.menu_draw_bind(ui_worker, "menu_win", "menu_row", "menu_item")
def menu_win_draw(menu_win:xui.win.MenuRO, event:xui.XUEvent):
    bg_color = 12
    frame_color = 10 if event.active else 7
    title  = menu_win.attr_str("title")

    menu_win.draw()

    # カーソル表示
    item = menu_win.selected_item
    tri_size = 6
    left = item.area.x
    top  = item.area.y+2
    pyxel.tri(left, top, left, top+tri_size, left+tri_size//2, top+tri_size//2, 7)

    # メニュータイトル
    if title:
        str_w = FONT_SIZE*len(title)
        text_x = menu_win.area.x+(menu_win.area.w-str_w)/2
        pyxel.rect(text_x,menu_win.area.y, str_w, FONT_SIZE, bg_color)
        pyxel.text(text_x, menu_win.area.y-2, title, frame_color, font)


# メッセージウインドウ
# *****************************************************************************
# 更新
# ---------------------------------------------------------
@xui.win.msg_update_bind(ui_worker, "msg_win", "msg_text")
def msg_win_update(msg_win:xui.win.Msg, event:xui.XUEvent):
    if "button_a" in event.trg or "button_b" in event.trg:
        # 表示しきっていたらメニューごと閉じる
        if msg_win.page.is_end_page:
            msg_win.close("menu_command")
        # なにか残っていたら適切なアクション(ライブラリにお任せ)
        else:
           msg_win.page.action()

# 描画
# ---------------------------------------------------------
@xui.win.msg_draw_bind(ui_worker, "msg_win", "msg_text")
def msg_win_draw(msg_win:xui.win.MsgRO, event:xui.XUEvent):
    msg_win.draw()

    # カーソル表示
    if msg_win.page.is_next_wait:
        tri_size = 6
        center_x = msg_win.area.center_x(tri_size)
        bottom = msg_win.area.bottom(tri_size) - 2
        pyxel.tri(center_x, bottom, center_x+tri_size, bottom, center_x+tri_size//2, bottom+tri_size//2, 7)


# ダイアル
# *****************************************************************************
@ui_worker.update_bind("win_dial")
def win_dial_update(win_dial:xui.core.XUState, event:xui.XUEvent):
    # 数値変更
    dial = xui.core.XUDial(win_dial, 5)
    dial.change_by_event(event.trg, "left", "right", "up", "down")

    # 確定
    if "button_a" in event.trg:
        win_dial.open(ui_template, "yes_no", "dial_yes_no")
        # dial_win.close() # 確定でも閉じる

    # 閉じる
    if "button_b" in event.trg:
        win_dial.close()

@ui_worker.draw_bind("win_dial")
def dial_win_draw(dial_win:xui.core.XUStateRO, event:xui.XUEvent):
    frame_color = 10 if event.active else 7
    pyxel.rect(dial_win.area.x, dial_win.area.y, dial_win.area.w, dial_win.area.h, 12)
    pyxel.rectb(dial_win.area.x, dial_win.area.y, dial_win.area.w, dial_win.area.h, frame_color)

    # 数値表示
    dial = xui.core.XUDialRO(dial_win)
    for i,digit in enumerate(dial.zenkaku_digits):
        pyxel.text(dial_win.area.x+3+(4-i)*FONT_SIZE, dial_win.area.y+2, digit, 2 if dial.edit_pos == i else 7, font)

@ui_worker.update_bind("dial_yes_no")
def dial_yes_no_update(dial_yes_no:xui.core.XUState, event:xui.XUEvent):
    item_h = dial_yes_no.attr_int("item_h")

    grid = xui.core.XUSelectList(dial_yes_no, "yes_no_item").arrange_items(0, item_h)
    grid.select_by_event(event.trg, "up", "down")

    # 閉じる
    if "button_b" in event.trg:
        dial_yes_no.close()

    # 決定
    if "button_a" in event.trg:
        # Yes時処理
        if grid.selected_item.value == "yes":
            test_params["age"] = xui.core.XUDialRO(dial_yes_no.find_by_tagR("win_dial")).number
            dial_yes_no.xmlui.close("menu_command")

        # No時処理
        if grid.selected_item.value == "no":
            dial_yes_no.close()


@ui_worker.draw_bind("dial_yes_no")
def dial_yes_no_draw(dial_yes_no:xui.core.XUStateRO, event:xui.XUEvent):
    frame_color = 10 if event.active else 7
    pyxel.rect(dial_yes_no.area.x+4, dial_yes_no.area.y+4, dial_yes_no.area.w, dial_yes_no.area.h, 12)
    pyxel.rectb(dial_yes_no.area.x+4, dial_yes_no.area.y+4, dial_yes_no.area.w, dial_yes_no.area.h, frame_color)

@ui_worker.draw_bind("yes_no_item")
def dial_yes_no_item_draw(item:xui.core.XUStateRO, event:xui.XUEvent):
    pyxel.text(item.area.x+6, item.area.y, item.text, 7, font)  # Yes/No表示
    # カーソル表示
    if item.selected:
        pyxel.tri(item.area.x, item.area.y+2, item.area.x, item.area.y+2+6, item.area.x+6//2, item.area.y+2+6//2, 7)
