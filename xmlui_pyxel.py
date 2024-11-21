from xmlui import XMLUI,UI_STATE,UI_EVENT,UI_CURSOR

ui_template = XMLUI.createFromFile("assets/ui/test.xml")

import pyxel
font = pyxel.Font("assets/font/b12.bdf")
FONT_SIZE = 12


def my_ui_update(state: UI_STATE, event:UI_EVENT):
    # メインメニューを開く
    if "action" in event.trg:
        state.open(ui_template, "menu_command")


def menu_win_update(state: UI_STATE, event:UI_EVENT):
    item_w, item_h = state.attrInt("item_w"), state.attrInt("item_h")

    # メニューアイテム取得
    grid = state.arrayByTag("menu_row", "menu_item")

    # 各アイテムの位置設定
    for y,cols in enumerate(grid):
        for x,rows in enumerate(cols):
            rows.setAttr(["x", "y"], (x*item_w, y*item_h))

    # カーソル
    cursor = UI_CURSOR(state.findByTag("menu_cur"), len(grid[0]), len(grid)).moveByEvent(event.trg, "left", "right", "up", "down")
    cursor.state.setAttr(["x", "y"], (cursor.cur_x*item_w-6, cursor.cur_y*item_h+2))  # 表示位置設定

    # 選択アイテムの表示
    if "action" in event.trg:
        # メッセージウインドウ表示
        state.open(ui_template, "win_message")

    # 閉じる
    if "cancel" in event.trg:
        state.close(state.id)


def msg_win_update(state: UI_STATE, event:UI_EVENT):
    msg_cur = state.findByTag("msg_cur")
    msg_text = state.findByTag("msg_text")

    msg_cur.setAttr("visible", msg_text.attrBool("page_end"))

    if "action" in event.trg:
        if msg_text.attrBool("finish"):
            state.close("menu_command")  # メニューごと閉じる
        else:
            msg_text.setAttr("draw_count", 65536)  # 一気に表示する
    

    # 次のページへ
    if "action" in event.trg:
        msg_text.setAttr("page_no", msg_text.attrInt("page_no")+1)
        msg_text.attrInt("draw_count", 0)

    # メニューごと閉じる
    if "cancel" in event.trg:
        state.close("menu_command")


def msg_text_update(state: UI_STATE, event:UI_EVENT):
    wrap = state.attrInt("wrap", 1024)
    draw_count = state.attrInt("draw_count")

    state.setAttr("draw_count", draw_count+1)

    pages  = state.text.bind({"name":"world", "age":10}).limit(draw_count).getPages("page_no", 3)
    state.setAttr("page_end", draw_count >= len(pages.getText()))

    if pages.page_no >= len(pages):
        state.setAttr("finish", True)


# update関数テーブル
updateFuncs= {
    'my_ui': my_ui_update,
    "menu_win": menu_win_update,
    "msg_win": msg_win_update,
    "msg_text": msg_text_update,
}


def msg_win_draw(state:UI_STATE):
    bg_color = state.attrInt("bg_color", 12)
    frame_color = state.attrInt("frame_color", 7)
    pyxel.rect(state.area.x, state.area.y, state.area.w, state.area.h, bg_color)
    pyxel.rectb(state.area.x, state.area.y, state.area.w, state.area.h, frame_color)
    pyxel.rectb(state.area.x+1, state.area.y+1, state.area.w-2, state.area.h-2, frame_color)
    pyxel.rectb(state.area.x+3, state.area.y+3, state.area.w-6, state.area.h-6, frame_color)

def msg_text_draw(state:UI_STATE):
    wrap = state.attrInt("wrap", 1024)
    color = state.attrInt("color", 7)
    draw_count = state.attrInt("draw_count", 0)
    page_no = state.attrInt("page_no")
    page_no = 1

    # テキスト表示
    pages = state.text.bind({"name":"world", "age":10}, wrap=4).limit(draw_count)
    for i,text in enumerate(pages.splitlines()):
        pyxel.text(state.area.x, state.area.y+i*FONT_SIZE, text, color, font)

def msg_cur_draw(state:UI_STATE):
    tri_size = state.attrInt("size", 6)
    color = state.attrInt("color", 7)

    # カーソル表示
    x, y = state.area.x, state.area.y
    pyxel.tri(x, y, x+tri_size, y, x+tri_size//2, y+tri_size//2, color)

def menu_win_draw(state:UI_STATE):
    bg_color = state.attrInt("bg_color", 12)
    frame_color = state.attrInt("frame_color", 7)
    title  = state.attrStr("title", "")

    pyxel.rect(state.area.x, state.area.y, state.area.w, state.area.h, bg_color)
    pyxel.rectb(state.area.x, state.area.y, state.area.w, state.area.h, frame_color)
    pyxel.rectb(state.area.x+1, state.area.y+1, state.area.w-2, state.area.h-2, frame_color)

    if title:
        str_w = FONT_SIZE*len(title)
        text_x = state.area.x+(state.area.w-str_w)/2
        pyxel.rect(text_x,state.area.y, str_w, FONT_SIZE, bg_color)
        pyxel.text(text_x, state.area.y-2, title, frame_color, font)

def menu_item_draw(state:UI_STATE):
    color = state.attrInt("color", 7)
    pyxel.text(state.area.x, state.area.y, state.text, color, font)

def menu_cur_draw(state:UI_STATE):
    tri_size = state.attrInt("size", 6)
    color = state.attrInt("color", 7)

    # カーソル表示
    x = state.area.x
    y = state.area.y
    pyxel.tri(x, y, x, y+tri_size, x+tri_size//2, y+tri_size//2, color)

# draw関数テーブル
drawFuncs= {
    "msg_win": msg_win_draw,
    "msg_text": msg_text_draw,
    "msg_cur": msg_cur_draw,
    "menu_win": menu_win_draw,
    "menu_item": menu_item_draw,
    "menu_cur": menu_cur_draw,
}


# 処理関数の登録
def setDefaults(xmlui: XMLUI):
    for key in drawFuncs:
        xmlui.setDrawFunc(key, drawFuncs[key])

    for key in updateFuncs:
        xmlui.setUpdateFunc(key, updateFuncs[key])
