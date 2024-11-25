from xmlui import XMLUI,UI_STATE,UI_EVENT,UI_GRID_CURSOR,UI_PAGE,UI_PAGE_RO,UI_DIAL,UI_DIAL_RO

ui_template = XMLUI.createFromFile("assets/ui/test.xml")
ui_worker = XMLUI.createWorker("my_ui")

import pyxel
font = pyxel.Font("assets/font/b12.bdf")
FONT_SIZE = 12

# お試しパラメータ
test_params = {"name":"world", "age":10}

# 入力待ち
# *****************************************************************************
@ui_worker.update_func("my_ui")
def my_ui_update(my_ui:UI_STATE, event:UI_EVENT):
    # メインメニューを開く
    if "button_a" in event.trg:
        my_ui.open(ui_template, "menu_command")


# コマンドメニュー
# *****************************************************************************
# 更新
# ---------------------------------------------------------
@ui_worker.update_func("menu_win")
def menu_win_update(menu_win:UI_STATE, event:UI_EVENT):
    item_w, item_h = menu_win.attrInt("item_w"), menu_win.attrInt("item_h")

    # メニューアイテム
    grid = menu_win.arrangeGridByTag("menu_row", "menu_item", item_w, item_h)
    cursor = UI_GRID_CURSOR(menu_win.findByTag("menu_cur"), grid).moveByEvent(event.trg, "left", "right", "up", "down")

    # 選択アイテムの表示
    if "button_a" in event.trg:
        # メッセージウインドウ表示
        if cursor.selected.attrStr("action") == "speak":
            menu_win.open(ui_template, "win_message")

        # dialウインドウ表示
        if cursor.selected.attrStr("action") == "dial":
            cursor.selected.open(ui_template, "win_dial").setPos(8, -2)

    # 閉じる
    if "button_b" in event.trg:
        menu_win.close()

# 描画
# ---------------------------------------------------------
@ui_worker.draw_func("menu_win")
def menu_win_draw(menu_win:UI_STATE, event:UI_EVENT):
    bg_color = 12
    frame_color = 10 if event.active else 7
    title  = menu_win.attrStr("title")

    pyxel.rect(menu_win.area.x, menu_win.area.y, menu_win.area.w, menu_win.area.h, bg_color)
    pyxel.rectb(menu_win.area.x, menu_win.area.y, menu_win.area.w, menu_win.area.h, frame_color)
    pyxel.rectb(menu_win.area.x+1, menu_win.area.y+1, menu_win.area.w-2, menu_win.area.h-2, frame_color)

    if title:
        str_w = FONT_SIZE*len(title)
        text_x = menu_win.area.x+(menu_win.area.w-str_w)/2
        pyxel.rect(text_x,menu_win.area.y, str_w, FONT_SIZE, bg_color)
        pyxel.text(text_x, menu_win.area.y-2, title, frame_color, font)

@ui_worker.draw_func("menu_item")
def menu_item_draw(menu_item:UI_STATE, event:UI_EVENT):
    color = menu_item.attrInt("color", 7)
    pyxel.text(menu_item.area.x, menu_item.area.y, menu_item.text, color, font)

@ui_worker.draw_func("menu_cur")
def menu_cur_draw(menu_cur:UI_STATE, event:UI_EVENT):
    tri_size = menu_cur.attrInt("size", 6)
    color = menu_cur.attrInt("color", 7)

    # カーソル表示
    x = menu_cur.area.x-6
    y = menu_cur.area.y+2
    pyxel.tri(x, y, x, y+tri_size, x+tri_size//2, y+tri_size//2, color)


# メッセージウインドウ
# *****************************************************************************
# 更新
# ---------------------------------------------------------
@ui_worker.update_func("msg_win")
def msg_win_update(msg_win:UI_STATE, event:UI_EVENT):
    msg_cur = msg_win.findByTag("msg_cur")
    msg_text = msg_win.findByTag("msg_text")

    # 文字列更新
    text = UI_PAGE(msg_text, msg_text.text.format(**test_params), 3).next()

    # 次のページありカーソル表示
    msg_cur.setVisible(not text.is_end_page and text.is_finish)

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
def msg_win_draw(msg_win:UI_STATE, event:UI_EVENT):
    frame_color = 10 if event.active else 7
    pyxel.rect(msg_win.area.x, msg_win.area.y, msg_win.area.w, msg_win.area.h, 12)
    pyxel.rectb(msg_win.area.x, msg_win.area.y, msg_win.area.w, msg_win.area.h, frame_color)
    pyxel.rectb(msg_win.area.x+1, msg_win.area.y+1, msg_win.area.w-2, msg_win.area.h-2, frame_color)
    pyxel.rectb(msg_win.area.x+3, msg_win.area.y+3, msg_win.area.w-6, msg_win.area.h-6, frame_color)

@ui_worker.draw_func("msg_text")
def msg_text_draw(msg_text:UI_STATE, event:UI_EVENT):
    # テキスト表示
    text = UI_PAGE_RO(msg_text)

    for i,text in enumerate(text.page_text.split()):
        pyxel.text(msg_text.area.x, msg_text.area.y+i*FONT_SIZE, text, 7, font)

@ui_worker.draw_func("msg_cur")
def msg_cur_draw(msg_cur:UI_STATE, event:UI_EVENT):
    tri_size = msg_cur.attrInt("size", 6)
    color = msg_cur.attrInt("color", 7)

    # カーソル表示
    x, y = msg_cur.area.x, msg_cur.area.y
    pyxel.tri(x, y, x+tri_size, y, x+tri_size//2, y+tri_size//2, color)


# ダイアル
# *****************************************************************************
@ui_worker.update_func("dial_win")
def dial_win_update(dial_win:UI_STATE, event:UI_EVENT):
    # 数値変更
    dial = UI_DIAL(dial_win, 5)
    dial.changeByEvent(event.trg, "left", "right", "up", "down")

    # 確定
    if "button_a" in event.trg:
        test_params["age"] = dial.number
        dial_win.close() # 確定でも閉じる

    # 閉じる
    if "button_b" in event.trg:
        dial_win.close()

@ui_worker.draw_func("dial_win")
def dial_win_draw(dial_win:UI_STATE, event:UI_EVENT):
    frame_color = 10 if event.active else 7
    pyxel.rect(dial_win.area.x, dial_win.area.y, dial_win.area.w, dial_win.area.h, 12)
    pyxel.rectb(dial_win.area.x, dial_win.area.y, dial_win.area.w, dial_win.area.h, frame_color)

    # 数値表示
    dial = UI_DIAL_RO(dial_win)
    for i,digit in enumerate(dial.zenkakuDigits):
        pyxel.text(dial_win.area.x+3+(4-i)*FONT_SIZE, dial_win.area.y+2, digit, 2 if dial.digit_pos == i else 7, font)
