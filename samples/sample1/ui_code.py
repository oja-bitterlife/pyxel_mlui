import pyxel


# xmlui_pyxelの初期化
# *********************************************************
from xmlui_pyxel import select, xuc,text,win,input
import xmlui_pyxel

# ライブラリのインスタンス化
xmlui = xuc.XMLUI()

# キー定義。設定しない場合はデフォルトが使われる
# input.INPUT_LIST[input.BTN_A] = [pyxel.KEY_A]

# 初期化セット
xmlui_pyxel.initialize(xmlui,
        inputlist_dict = input.INPUT_LIST,
        font_path = "samples/assets/font/b12.bdf"
    )

# (ライブラリ開発用)
xmlui.debug.level = xmlui.debug.DEBUG_LEVEL_LIB

# UIテンプレートXMLの読み込み
UI_TEMPLATE = "ui_template"
xmlui.template_fromfile("samples/assets/ui/dq.xml", "ui_template")


# ユーティリティ
# *****************************************************************************
# カーソル描画
def draw_menu_cursor(state:xuc.XUState, x:int, y:int):
    tri_size = 6
    left = state.area.x + x
    top = state.area.y+2 + y
    pyxel.tri(left, top, left, top+tri_size, left+tri_size//2, top+tri_size//2, 7)

def draw_msg_cursor(state:xuc.XUState):
    tri_size = 6
    center_x = state.area.center_x(tri_size)
    bottom = state.area.bottom(tri_size) - 2
    pyxel.tri(center_x, bottom, center_x+tri_size, bottom, center_x+tri_size//2, bottom+tri_size//2, 7)


# ウインドウ
# *****************************************************************************
# 角丸ウインドウ
# ---------------------------------------------------------
@win.round(xmlui, "round_win", speed=1)
def round_win_draw(win:win.Round, event:xuc.XUEvent):
    win.draw()

# コマンドメニュー
# *****************************************************************************
@select.item(xmlui, select.Grid.item_tagname("menu_item"))
def menu_item(menu_item:select.Item, event:xuc.XUEvent):
    pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, 7, text.default.font)


# コマンドメニュー
# *****************************************************************************
@select.grid(xmlui, "menu_grid", "menu_item", "rows", "item_w", "item_h")
def menu_grid(menu_grid:select.Grid, event:xuc.XUEvent):
    # メニュー選択
    selected_item = menu_grid.select_by_event(event.trg, *input.CURSOR)

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
        menu_grid.close()

    # カーソル追加
    draw_menu_cursor(menu_grid.selected_item, 0, 0)


# メッセージウインドウ
# *****************************************************************************
@text.msg(xmlui, "msg_text")
def msg_text(msg_text:text.Msg, event:xuc.XUEvent):
    if input.BTN_A in event.trg or input.BTN_B in event.trg:
        action = msg_text.check_action()
        match action:
            case "close":
                msg_text.close("command_menu_win")  # メニューごと閉じる
            case "finish":
                msg_text.finish()
            case "next_page":
                msg_text.next_page()

    msg_text.draw()

    # カーソル表示
    if msg_text.is_next_wait:
        draw_msg_cursor(msg_text)



# ダイアル
# *****************************************************************************
# @xmlui.update_bind("win_dial")
# def win_dial_update(win_dial:xuc.XUState, event:xuc.XUEvent):
#     # 数値変更
#     dial = xuc.XUDial(win_dial, 5)
#     dial.change_by_event(event.trg, *input.CURSOR)

#     # 確定
#     if input.BTN_A in event.trg:
#         win_dial.open(UI_TEMPLATE, "yes_no", "dial_yes_no")
#         # dial_win.close() # 確定でも閉じる

#     # 閉じる
#     if input.BTN_B in event.trg:
#         win_dial.close()

# @xmlui.draw_bind("win_dial")
# def dial_win_draw(dial_win:xuc.XUStateRO, event:xuc.XUEvent):
#     frame_color = 10 if event.active else 7
#     pyxel.rect(dial_win.area.x, dial_win.area.y, dial_win.area.w, dial_win.area.h, 12)
#     pyxel.rectb(dial_win.area.x, dial_win.area.y, dial_win.area.w, dial_win.area.h, frame_color)

#     # 数値表示
#     dial = xuc.XUDialBase(dial_win)
#     for i,digit in enumerate(dial.zenkaku_digits):
#         pyxel.text(dial_win.area.x+3+(4-i)*text.default.size, dial_win.area.y+2, digit, 2 if dial.edit_pos == i else 7, text.default.data)

@select.list(xmlui, "yes_no", "yes_no_item", "item_h")
def dial_yes_no_update(list_win:select.List, event:xuc.XUEvent):
    # メニュー選択
    selected_item = list_win.select_by_event(event.trg, *input.UP_DOWN)

    # 閉じる
    # if input.BTN_B in event.trg:
    #     list_win.close()

    # 決定
    if input.BTN_A in event.trg:
        # Yes時処理
        if selected_item == "yes":
#            test_params["age"] = core.XUDialRO(list_win.find_by_tagR("win_dial")).number
            list_win.xmlui.close("menu_command")

        # No時処理
        # if selected_item == "no":
        #     list_win.close()

    list_win.draw()
    draw_menu_cursor(list_win.selected_item, 0, 0)


# ラベル全般
# *****************************************************************************
@text.label(xmlui, "title")
def title_draw(label:text.Label, event:xuc.XUEvent):
    label.draw()
