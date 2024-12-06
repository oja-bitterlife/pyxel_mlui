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
xmlui_pyxel.init(xmlui,
        inputlist_dict = input.INPUT_LIST,
        font_path = "samples/common_assets/font/b12.bdf"
    )

# (ライブラリ開発用)
xmlui.debug.level = xmlui.debug.DEBUG_LEVEL_LIB

# UIテンプレートXMLの読み込み
UI_TEMPLATE = "ui_template"
xmlui.template_fromfile("samples/sample1/assets/ui/test.xml", "ui_template")


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


# 表示物
# *****************************************************************************
# 角丸ウインドウ
# ---------------------------------------------------------
@win.round(xmlui, "round_win")
def round_win_draw(win:win.Round, event:xuc.XUEvent):
    clip = win.area.to_offset()
    clip.h = int(win.update_count*win.speed)
    win.draw_buf(pyxel.screen.data_ptr(), [7,13,5], 12, clip)

# 四角ウインドウ
# ---------------------------------------------------------
@win.rect(xmlui, "rect_win")
def rect_win_draw(win:win.Rect, event:xuc.XUEvent):
    clip = win.area.to_offset()
    clip.h = int(win.update_count*win.speed)
    win.draw_buf(pyxel.screen.data_ptr(), [7,13,5], 12, clip)


# メニューアイテム
# ---------------------------------------------------------
@select.item(xmlui, "menu_item")
def menu_item(menu_item:select.Item, event:xuc.XUEvent):
    pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, 7, text.default.font)

# ラベル
# ---------------------------------------------------------
@text.label(xmlui, "title", "center", "top")
def title_draw(label:text.Label, event:xuc.XUEvent):
    pyxel.rect(label.area.x, label.area.y, label.area.w, label.area.h, 12)
    x, y = label.aligned_pos(text.default)
    pyxel.text(x, y, label.text, 7, text.default.font)

@text.label(xmlui, "ok_title", "center", "top")
def ok_title_draw(label:text.Label, event:xuc.XUEvent):
    pyxel.rect(label.area.x, label.area.y, label.area.w, label.area.h, 12)
    x, y = label.aligned_pos(text.default)
    pyxel.text(x, y-3, label.text, 7, text.default.font)


# メニュー
# *****************************************************************************
# コマンドメニュー
@select.grid(xmlui, "menu_grid", "menu_item", "rows", "item_w", "item_h")
def menu_grid(menu_grid:select.Grid, event:xuc.XUEvent):
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


@select.list(xmlui, "yes_no_list", "menu_item", "item_h")
def yes_no_list(list_win:select.List, event:xuc.XUEvent):
    # メニュー選択
    list_win.select_by_event(event.trg, *input.UP_DOWN)

    # 閉じる
    if input.BTN_B in event.trg:
        list_win.close()

    # 決定
    if input.BTN_A in event.trg:
        # Yes時処理
        if list_win.selected_item == "yes":
            list_win.close_parent_on("command_menu_win", "dial_yes")

        # No時処理
        if list_win.selected_item == "no":
            list_win.close()

    # カーソル追加
    draw_menu_cursor(list_win.selected_item, 0, 0)


# メッセージウインドウ
# *****************************************************************************
@text.msg(xmlui, "msg_text")
def msg_text(msg_text:text.Msg, event:xuc.XUEvent):
    if input.BTN_A in event.trg or input.BTN_B in event.trg:
        action = msg_text.check_action()
        match action:
            case "close":
                msg_text.close_parent("command_menu_win")  # メニューごと閉じる
            case "finish":
                msg_text.finish_count()
            case "next_page":
                msg_text.add_page()

    # テキスト描画
    area = msg_text.area  # areaは重いので必ずキャッシュ
    for i,page in enumerate(msg_text.page_text.split()):
        pyxel.text(area.x, area.y+i*text.default.size, page, 7, text.default.font)

    # カーソル表示
    if msg_text.is_next_wait:
        draw_msg_cursor(msg_text)


# ダイアル
# *****************************************************************************
@input.dial(xmlui, "dial", 5)
def dial(dial:input.Dial, event:xuc.XUEvent):
    dial.change_by_event(event.trg, *input.CURSOR)

    for i,digit in enumerate(dial.zenkaku_digits):
        color = 2 if dial.edit_pos == i else 7
        x,y = dial.aligned_zenkaku_pos(text.default, 4, 4)
        pyxel.text(x + i*text.default.size, y, digit, color, text.default.font)

    # 確定
    if input.BTN_A in event.trg:
        yesno= dial.open(UI_TEMPLATE, "yes_no", "dial_yes_no")
        yesno.set_attr("value", dial.digits)

    # 閉じる
    if input.BTN_B in event.trg:
        dial.close_on()



# 工事中
# *****************************************************************************
# ポップアップウインドウ
# ---------------------------------------------------------
@win.rect(xmlui, "popup_win", 1000)  # アニメはしない
def popup_win_draw(win:win.Rect, event:xuc.XUEvent):
    clip = win.area.to_offset()
    clip.h = int(win.update_count*win.speed)
    win.draw_buf(pyxel.screen.data_ptr(), [7,13,5], 12, clip)

@text.msg(xmlui, "popup_text")
def popup_text(popup_text:text.Msg, event:xuc.XUEvent):
    popup_text.finish_count()  # 常に一気に表示

    if input.BTN_A in event.trg or input.BTN_B in event.trg:
        popup_text.close()

    # テキスト描画
    area = popup_text.area  # areaは重いので必ずキャッシュ

    h = len(popup_text.page_text.split()) * text.default.size
    y = area.aligned_y(h, "center")
    for i,page in enumerate(popup_text.page_text.split()):
        x = area.aligned_x(text.default.font.text_width(page), "center")
        pyxel.text(x, y+i*text.default.size, page, 7, text.default.font)
