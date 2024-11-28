from xui_pyxel import components as xui

from xmlui_core import *

ui_template = XMLUI.fromfile("assets/ui/test.xml")
ui_worker = XMLUI.mkworker("my_ui")

import pyxel
font = pyxel.Font("assets/font/b12.bdf")
FONT_SIZE = 12

# お試しパラメータ
test_params = {"name":"world", "age":10}

# 入力待ち
# *****************************************************************************
@ui_worker.update_func("my_ui")
def my_ui_update(my_ui:XUState, event:XUEvent):
    # メインメニューを開く
    if "button_a" in event.trg:
        my_ui.open(ui_template, "menu_command")


# コマンドメニュー
# *****************************************************************************
# 更新
# ---------------------------------------------------------
@ui_worker.update_func("menu_win")
def menu_win_update(menu_win:XUState, event:XUEvent):
    item_w, item_h = menu_win.attr_int("item_w"), menu_win.attr_int("item_h")

    # メニューアイテム
    menu = xui.MenuWindow(menu_win, "menu_row", "menu_item", item_w, item_h)
    menu.select_by_event("left", "right", "up", "down")

    # 選択アイテムの表示
    if "button_a" in event.trg:
        # メッセージウインドウ表示
        if menu == "speak":
            menu.open(ui_template, "win_message")

        # dialウインドウ表示
        if menu == "dial":
            menu.open(ui_template, "win_dial").set_pos(8, 2)

    # 閉じる
    if "button_b" in event.trg:
        menu_win.close()

# 描画
# ---------------------------------------------------------
@ui_worker.draw_func("menu_win")
def menu_win_draw(menu_win:XUStateRO, event:XUEvent):
    item_w, item_h = menu_win.attr_int("item_w"), menu_win.attr_int("item_h")

    bg_color = 12
    frame_color = 10 if event.active else 7
    title  = menu_win.attr_str("title")

    menu = xui.MenuWindow(menu_win.asRW(), "menu_row", "menu_item", item_w, item_h)
    menu.draw_win()

    if title:
        str_w = FONT_SIZE*len(title)
        text_x = menu_win.area.x+(menu_win.area.w-str_w)/2
        pyxel.rect(text_x,menu_win.area.y, str_w, FONT_SIZE, bg_color)
        pyxel.text(text_x, menu_win.area.y-2, title, frame_color, font)

@ui_worker.draw_func("menu_item")
def menu_item_draw(menu_item:XUStateRO, event:XUEvent):
    color = menu_item.attr_int("color", 7)
    pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, color, font)

    # カーソル表示
    if menu_item.selected:
        pyxel.tri(menu_item.area.x, menu_item.area.y+2, menu_item.area.x, menu_item.area.y+2+6, menu_item.area.x+6//2, menu_item.area.y+2+6//2, color)


# メッセージウインドウ
# *****************************************************************************
# 更新
# ---------------------------------------------------------
@ui_worker.update_func("msg_win")
def msg_win_update(msg_win:XUState, event:XUEvent):
    msg_cur = msg_win.find_by_tag("msg_cur")
    msg_text = msg_win.find_by_tag("msg_text")

    # 文字列更新
    text = XUPage(msg_text, msg_text.text.format(**test_params), 3, msg_text.attr_int("wrap")).nextcount()

    # 次のページありカーソル表示
    msg_cur.set_visible(not text.is_end_page and text.is_finish)

    if "button_a" in event.trg or "button_b" in event.trg:
        # 表示しきっていたらメニューごと閉じる
        if text.is_end_page:
            msg_win.close("menu_command")
        # なにか残っていたら適切なアクション(ライブラリにお任せ)
        else:
           text.action()

# 描画
# ---------------------------------------------------------
@ui_worker.draw_func("msg_win")
def msg_win_draw(msg_win:XUStateRO, event:XUEvent):
    frame_color = 10 if event.active else 7
    pyxel.rect(msg_win.area.x, msg_win.area.y, msg_win.area.w, msg_win.area.h, 12)
    pyxel.rectb(msg_win.area.x, msg_win.area.y, msg_win.area.w, msg_win.area.h, frame_color)
    pyxel.rectb(msg_win.area.x+1, msg_win.area.y+1, msg_win.area.w-2, msg_win.area.h-2, frame_color)
    pyxel.rectb(msg_win.area.x+3, msg_win.area.y+3, msg_win.area.w-6, msg_win.area.h-6, frame_color)

@ui_worker.draw_func("msg_text")
def msg_text_draw(msg_text:XUStateRO, event:XUEvent):
    # テキスト表示
    page = XUPageRO(msg_text)

    for i,page in enumerate(page.page_text.split()):
        pyxel.text(msg_text.area.x, msg_text.area.y+i*FONT_SIZE, page, 7, font)

@ui_worker.draw_func("msg_cur")
def msg_cur_draw(msg_cur:XUStateRO, event:XUEvent):
    tri_size = msg_cur.attr_int("size", 6)
    color = msg_cur.attr_int("color", 7)

    # カーソル表示
    x, y = msg_cur.area.x, msg_cur.area.y
    pyxel.tri(x, y, x+tri_size, y, x+tri_size//2, y+tri_size//2, color)


# ダイアル
# *****************************************************************************
@ui_worker.update_func("win_dial")
def win_dial_update(win_dial:XUState, event:XUEvent):
    # 数値変更
    dial = XUDial(win_dial, 5)
    dial.change_by_event(event.trg, "left", "right", "up", "down")

    # 確定
    if "button_a" in event.trg:
        win_dial.open(ui_template, "yes_no", "dial_yes_no")
        # dial_win.close() # 確定でも閉じる

    # 閉じる
    if "button_b" in event.trg:
        win_dial.close()

@ui_worker.draw_func("win_dial")
def dial_win_draw(dial_win:XUStateRO, event:XUEvent):
    frame_color = 10 if event.active else 7
    pyxel.rect(dial_win.area.x, dial_win.area.y, dial_win.area.w, dial_win.area.h, 12)
    pyxel.rectb(dial_win.area.x, dial_win.area.y, dial_win.area.w, dial_win.area.h, frame_color)

    # 数値表示
    dial = XUDialRO(dial_win)
    for i,digit in enumerate(dial.zenkaku_digits):
        pyxel.text(dial_win.area.x+3+(4-i)*FONT_SIZE, dial_win.area.y+2, digit, 2 if dial.edit_pos == i else 7, font)

@ui_worker.update_func("dial_yes_no")
def dial_yes_no_update(dial_yes_no:XUState, event:XUEvent):
    item_h = dial_yes_no.attr_int("item_h")

    grid = XUSelectList(dial_yes_no, "yes_no_item").arrange_items(0, item_h)
    grid.select_by_event(event.trg, "up", "down")

    # 閉じる
    if "button_b" in event.trg:
        dial_yes_no.close()

    # 決定
    if "button_a" in event.trg:
        # Yes時処理
        if grid.selected_item.value == "yes":
            test_params["age"] = XUDialRO(dial_yes_no.find_by_tagR("win_dial")).number
            dial_yes_no.xmlui.close("menu_command")

        # No時処理
        if grid.selected_item.value == "no":
            dial_yes_no.close()


@ui_worker.draw_func("dial_yes_no")
def dial_yes_no_draw(dial_yes_no:XUStateRO, event:XUEvent):
    frame_color = 10 if event.active else 7
    pyxel.rect(dial_yes_no.area.x+4, dial_yes_no.area.y+4, dial_yes_no.area.w, dial_yes_no.area.h, 12)
    pyxel.rectb(dial_yes_no.area.x+4, dial_yes_no.area.y+4, dial_yes_no.area.w, dial_yes_no.area.h, frame_color)

@ui_worker.draw_func("yes_no_item")
def dial_yes_no_item_draw(item:XUStateRO, event:XUEvent):
    pyxel.text(item.area.x+6, item.area.y, item.text, 7, font)  # Yes/No表示
    # カーソル表示
    if item.selected:
        pyxel.tri(item.area.x, item.area.y+2, item.area.x, item.area.y+2+6, item.area.x+6//2, item.area.y+2+6//2, 7)
