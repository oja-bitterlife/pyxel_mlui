from xmlui import XMLUI,UI_STATE
from xml.etree.ElementTree import Element

import pyxel
font = pyxel.Font("assets/font/b12.bdf")


def window(state: UI_STATE):
    bg_color = state.attrInt("bg_color", 12)
    fg_color = state.attrInt("fg_color", 7)
    pyxel.rect(state.area.x, state.area.y, state.area.w, state.area.h, bg_color)
    pyxel.rectb(state.area.x, state.area.y, state.area.w, state.area.h, fg_color)
    pyxel.rectb(state.area.x+1, state.area.y+1, state.area.w-2, state.area.h-2, fg_color)
    pyxel.rectb(state.area.x+3, state.area.y+3, state.area.w-6, state.area.h-6, fg_color)

def text(state: UI_STATE):
    wrap = state.attrInt("wrap", 256)
    color = state.attrInt("color", 7)
    text = state.getText()
    pyxel.text(state.area.x, state.area.y, text, color, font)

# 処理関数テーブル
defaultFuncs= {
    "window": window,
    "text": text,
}


# 処理関数の登録
def setDefaults(xmlui: XMLUI):
    for key in defaultFuncs:
        xmlui.setDrawFunc(key, defaultFuncs[key])
