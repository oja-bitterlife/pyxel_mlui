from xmlui import XMLUI,UI_STATE,UI_TEXT
from xml.etree.ElementTree import Element

import pyxel
font = pyxel.Font("assets/font/b12.bdf")
FONT_SIZE = 12


def msg_text_update(ui:XMLUI, state: UI_STATE):
    draw_count = state.update_count//2
    state.userData["draw_count"] = draw_count

    msg_cur = ui.findByTag("msg_cur")
    if msg_cur != None:
        ui_text = UI_TEXT(state.getText(), {"name":"world", "age":10})
        msg_cur.setAttr("visible", False if draw_count < ui_text.length else True)

# update関数テーブル
updateFuncs= {
    "msg_text": msg_text_update,
}


def msg_win_draw(ui:XMLUI, state: UI_STATE):
    bg_color = state.attrInt("bg_color", 12)
    fg_color = state.attrInt("fg_color", 7)
    pyxel.rect(state.area.x, state.area.y, state.area.w, state.area.h, bg_color)
    pyxel.rectb(state.area.x, state.area.y, state.area.w, state.area.h, fg_color)
    pyxel.rectb(state.area.x+1, state.area.y+1, state.area.w-2, state.area.h-2, fg_color)
    pyxel.rectb(state.area.x+3, state.area.y+3, state.area.w-6, state.area.h-6, fg_color)

def msg_text_draw(ui:XMLUI, state: UI_STATE):
    wrap = state.attrInt("wrap", 256)
    color = state.attrInt("color", 7)
    draw_count: int = state.userData.get("draw_count", 0)

    # テキスト表示
    ui_text = UI_TEXT(state.getText(), {"name":"world", "age":10})
    lines = ui_text.get(draw_count)
    for i,text in enumerate(lines):
        pyxel.text(state.area.x, state.area.y+i*FONT_SIZE, text, color, font)

def msg_cur_draw(ui:XMLUI, state: UI_STATE):
    tri_size = state.attrInt("size", 6)
    color = state.attrInt("color", 7)

    # カーソル表示
    x = state.area.x
    y = state.area.y
    pyxel.tri(x, y, x+tri_size, y, x+tri_size//2, y+tri_size//2, color)

def menu_win_draw(ui:XMLUI, state: UI_STATE):
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
        pyxel.text(text_x, state.area.y-2, title, 7, font)


# draw関数テーブル
drawFuncs= {
    "msg_win": msg_win_draw,
    "msg_text": msg_text_draw,
    "msg_cur": msg_cur_draw,
    "menu_win": menu_win_draw,
}


# 処理関数の登録
def setDefaults(xmlui: XMLUI):
    for key in drawFuncs:
        xmlui.setDrawFunc(key, drawFuncs[key])

    for key in updateFuncs:
        xmlui.setUpdateFunc(key, updateFuncs[key])
