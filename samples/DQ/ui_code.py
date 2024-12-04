import pyxel

from xmlui_core import XUState,XUEvent
from xmlui_pyxel import win,text,select,input
from ui_common import xmlui,draw_menu_cursor,draw_msg_cursor


# 表示物
# *****************************************************************************
# 角丸ウインドウ
# ---------------------------------------------------------
@win.round(xmlui, "round_win")
def round_win_draw(win:win.Round, event:XUEvent):
    clip = win.area.to_offset()
    clip.h = int(win.update_count*win.speed)
    win.draw_buf(pyxel.screen.data_ptr(), [7,13,5], 12, clip)

# 四角ウインドウ
# ---------------------------------------------------------
@win.rect(xmlui, "rect_win")
def rect_win_draw(win:win.Rect, event:XUEvent):
    clip = win.area.to_offset()
    clip.h = int(win.update_count*win.speed)
    win.draw_buf(pyxel.screen.data_ptr(), [7,13,5], 12, clip)


# メニューアイテム
# ---------------------------------------------------------
@select.item(xmlui, "menu_item")
def menu_item(menu_item:select.Item, event:XUEvent):
    pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, 7, text.default.font)

# ラベル
# ---------------------------------------------------------
@text.label(xmlui, "title", "center", "top")
def title_draw(label:text.Label, event:XUEvent):
    pyxel.rect(label.area.x, label.area.y, label.area.w, label.area.h, 12)
    x, y = label.aligned_pos(text.default)
    pyxel.text(x, y, label.text, 7, text.default.font)

@text.label(xmlui, "ok_title", "center", "top")
def ok_title_draw(label:text.Label, event:XUEvent):
    pyxel.rect(label.area.x, label.area.y, label.area.w, label.area.h, 12)
    x, y = label.aligned_pos(text.default)
    pyxel.text(x, y-3, label.text, 7, text.default.font)


# メニュー
# *****************************************************************************
# コマンドメニュー
@select.grid(xmlui, "menu_grid", "menu_item", "rows", "item_w", "item_h")
def menu_grid(menu_grid:select.Grid, event:XUEvent):
    # メニュー選択
    menu_grid.select_by_event(event.trg, *input.CURSOR)

    # 選択アイテムの表示
    if input.BTN_A in event.trg:
        match menu_grid:
            case "speak":
                menu_grid.open(UI_TEMPLATE, "win_message")
            case "dial":
                menu_grid.open(UI_TEMPLATE, "win_dial")
            case "status":
                menu_grid.open(UI_TEMPLATE, "under_construct")

    # 閉じる
    if input.BTN_B in event.trg:
        menu_grid.close()

    # カーソル追加
    draw_menu_cursor(menu_grid.selected_item, 0, 0)




# メッセージウインドウ
# *****************************************************************************
@text.msg(xmlui, "msg_text")
def msg_text(msg_text:text.Msg, event:XUEvent):
    if input.BTN_A in event.trg or input.BTN_B in event.trg:
        action = msg_text.check_action()
        match action:
            case "close":
                msg_text.close_parent("command_menu_win")  # メニューごと閉じる
            case "finish":
                msg_text.finish()
            case "next_page":
                msg_text.next_page()

    # テキスト描画
    area = msg_text.area  # areaは重いので必ずキャッシュ
    for i,page in enumerate(msg_text.page_text.split()):
        pyxel.text(area.x, area.y+i*text.default.size, page, 7, text.default.font)

    # カーソル表示
    if msg_text.is_next_wait:
        draw_msg_cursor(msg_text)


# ダイアル
# *****************************************************************************
# @input.dial(xmlui, "dial", 5)
# def dial(dial:input.Dial, event:XUEvent):
#     dial.change_by_event(event.trg, *input.CURSOR)

#     for i,digit in enumerate(dial.zenkaku_digits):
#         color = 2 if dial.edit_pos == i else 7
#         x,y = dial.aligned_zenkaku_pos(text.default, 4, 4)
#         pyxel.text(x + i*text.default.size, y, digit, color, text.default.font)

#     # 確定
#     if input.BTN_A in event.trg:
#         yesno= dial.open(UI_TEMPLATE, "yes_no", "dial_yes_no")
#         yesno.set_attr("value", dial.digits)

#     # 閉じる
#     if input.BTN_B in event.trg:
#         dial.close_on()
