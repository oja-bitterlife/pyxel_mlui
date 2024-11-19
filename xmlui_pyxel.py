from xmlui import XMLUI,UI_STATE,UI_TEXT,UI_MENU

ui_template = XMLUI.createFromFile("assets/ui/test.xml")

import pyxel
font = pyxel.Font("assets/font/b12.bdf")
FONT_SIZE = 12

def menu_win_update(state: UI_STATE, events:set[str]):
    if state.menu is None:
        raise Exception("menu not found")

    item_w = state.attrInt("item_w")
    item_h = state.attrInt("item_h")
    cursor = state.findByTag("menu_cur")

    grid = state.menu.getItemGrid("menu_row", "menu_item")
    for y,cols in enumerate(grid):
        for x,rows in enumerate(cols):
            # 各アイテムの位置設定
            rows.setAttr(("x", "y"), (x*item_w, y*item_h))

    # カーソル表示位置設定
    cursor.setAttr(["x", "y"], [state.menu.cur_x*item_w-6, state.menu.cur_y*item_h+2])

    if "action" in events:
        if state.menu.getData() == "speak":
            msg_win = state.xmlui.duplicate(ui_template.findByID("win_message"))
            msg_win_menu = UI_MENU("message", msg_win).setCloseState(state)
            state.addChild(msg_win.openMenu(msg_win_menu))

    if "cancel" in events:
        state.menu.close()

def msg_win_update(state: UI_STATE, events:set[str]):
    msg_cur = state.findByTag("msg_cur")
    msg_text = state.findByTag("msg_text")

    if msg_cur and msg_text:
        msg_cur.setAttr("visible", msg_text.attrBool("finish"))

    if "action" in events:
        state.menu.close()  # TODO: メッセージ送りに

    if "cancel" in events:
        state.menu.close()

def msg_text_update(state: UI_STATE, events:set[str]):
    draw_count = state.attrInt("draw_count")
    ui_text = UI_TEXT(state.getText(), {"name":"world", "age":10})

    state.setAttr("draw_count", draw_count+1)
    state.setAttr("finish", draw_count >= ui_text.length)


# update関数テーブル
updateFuncs= {
    "menu_win": menu_win_update,
    "msg_win": msg_win_update,
    "msg_text": msg_text_update,
}


def msg_win_draw(state:UI_STATE, ):
    bg_color = state.attrInt("bg_color", 12)
    fg_color = state.attrInt("fg_color", 7)
    pyxel.rect(state.area.x, state.area.y, state.area.w, state.area.h, bg_color)
    pyxel.rectb(state.area.x, state.area.y, state.area.w, state.area.h, fg_color)
    pyxel.rectb(state.area.x+1, state.area.y+1, state.area.w-2, state.area.h-2, fg_color)
    pyxel.rectb(state.area.x+3, state.area.y+3, state.area.w-6, state.area.h-6, fg_color)

def msg_text_draw(state:UI_STATE):
    wrap = state.attrInt("wrap", 256)
    color = state.attrInt("color", 7)
    draw_count = state.attrInt("draw_count", 0)

    # テキスト表示
    ui_text = UI_TEXT(state.getText(), {"name":"world", "age":10})
    tokens = ui_text.getTokens(draw_count)
    for i,text in enumerate(tokens):
        pyxel.text(state.area.x, state.area.y+i*FONT_SIZE, text, color, font)

def msg_cur_draw(state:UI_STATE):
    tri_size = state.attrInt("size", 6)
    color = state.attrInt("color", 7)

    # カーソル表示
    x = state.area.x
    y = state.area.y
    pyxel.tri(x, y, x+tri_size, y, x+tri_size//2, y+tri_size//2, color)

def menu_win_draw(state:UI_STATE):
    bg_color = state.attrInt("bg_color", 12)
    fg_color = state.attrInt("fg_color", 7)
    title  = state.attrStr("title", "")

    pyxel.rect(state.area.x, state.area.y, state.area.w, state.area.h, bg_color)
    pyxel.rectb(state.area.x, state.area.y, state.area.w, state.area.h, fg_color)
    pyxel.rectb(state.area.x+1, state.area.y+1, state.area.w-2, state.area.h-2, fg_color)

    if title:
        str_w = FONT_SIZE*len(title)
        text_x = state.area.x+(state.area.w-str_w)/2
        pyxel.rect(text_x,state.area.y, str_w, FONT_SIZE, bg_color)
        pyxel.text(text_x, state.area.y-2, title, fg_color, font)

def menu_item_draw(state:UI_STATE):
    title  = state.attrStr("title", "")
    color = state.attrInt("color", 7)
    if title:
        pyxel.text(state.area.x, state.area.y, title, color, font)

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
