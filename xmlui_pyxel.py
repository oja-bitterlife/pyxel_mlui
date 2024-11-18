from xmlui import XMLUI,UI_STATE,UI_TEXT,UI_MENU
from xml.etree.ElementTree import Element

import pyxel
font = pyxel.Font("assets/font/b12.bdf")
FONT_SIZE = 12

def msg_win_update(state: UI_STATE):
    msg_cur = state.findByTag("msg_cur")
    msg_text = state.findByTag("msg_text")
    if msg_cur and msg_text:
        msg_cur.setAttr("visible", msg_text.attrBool("finish"))

def msg_text_update(state: UI_STATE):
    draw_count = state.update_count//2
    ui_text = UI_TEXT(state.getText(), {"name":"world", "age":10})

    state.setAttr("draw_count", draw_count)
    state.setAttr("finish", draw_count >= ui_text.length)

def menu_grid_update(state: UI_STATE):
    item_w = state.attrInt("item_w", 0)
    item_h = state.attrInt("item_h", 0)

    # item_data  = state.menu.findByID("dup_cmd_menu")
    # if item_data is None:
    #     return

    # アイテムを並べる
    # rows = state.findByTag("menu_row")
    # for y,row in enumerate(rows):
    #     item_y = y*item_h
    #     row.setAttr("y", item_y)

    #     items = row.findByTag("menu_item")
    #     for x,item in enumerate(items):
    #         item_x = x*item_w
    #         item.setAttr("x",item_x )

    #         if x == item_data.cur_x and y == item_data.cur_y:
    #             cursor = state.findByTag("menu_cur")[0]
    #             if cursor:
    #                 cursor.setAttr("x", item_x -6)
    #                 cursor.setAttr("y", item_y+2)

# update関数テーブル
updateFuncs= {
    "msg_win": msg_win_update,
    "msg_text": msg_text_update,
    "menu_grid": menu_grid_update,
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
