from xmlui import XMLUI,UI_STATE,UI_TEXT
from xml.etree.ElementTree import Element

import pyxel
font = pyxel.Font("assets/font/b12.bdf")
FONT_SIZE = 12

def msg_win(state: UI_STATE):
    bg_color = state.attrInt("bg_color", 12)
    fg_color = state.attrInt("fg_color", 7)
    pyxel.rect(state.area.x, state.area.y, state.area.w, state.area.h, bg_color)
    pyxel.rectb(state.area.x, state.area.y, state.area.w, state.area.h, fg_color)
    pyxel.rectb(state.area.x+1, state.area.y+1, state.area.w-2, state.area.h-2, fg_color)
    pyxel.rectb(state.area.x+3, state.area.y+3, state.area.w-6, state.area.h-6, fg_color)

def msg_text(state: UI_STATE):
    wrap = state.attrInt("wrap", 256)
    color = state.attrInt("color", 7)

    draw_count = state.update_count//2

    # テキスト表示
    ui_text = UI_TEXT(state.getText(), {"name":"world", "age":10})
    lines = ui_text.get(draw_count)
    for i,text in enumerate(lines):
        pyxel.text(state.area.x, state.area.y+i*FONT_SIZE, text, color, font)

    # カーソル表示
    if draw_count > len(ui_text):
        tri_size = 6
        x = state.area.x+state.area.w//2 -tri_size//2
        y = state.area.y+state.area.h -tri_size//2 + 1
        pyxel.tri(x, y, x+tri_size, y, x+tri_size//2, y+tri_size//2, color)


# 処理関数テーブル
defaultFuncs= {
    "msg_win": msg_win,
    "msg_text": msg_text,
}


# 処理関数の登録
def setDefaults(xmlui: XMLUI):
    for key in defaultFuncs:
        xmlui.setDrawFunc(key, defaultFuncs[key])
