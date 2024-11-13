from xmlui import XMLUI,UI_STATE
from xml.etree.ElementTree import Element

import pyxel

def drawArea(state: UI_STATE, element: Element):
    border_size = state.attr.getInt("border_size", 1)
    border_color = state.attr.getInt("border_color", 7)
    fill_color = state.attr.getInt("fill_color", 12)
    padding = state.attr.getInt("padding", 8)

    pyxel.rect(state.area.x, state.area.y, state.area.w, state.area.h, fill_color)

# 処理関数テーブル
defaultFuncs= {
    "area": drawArea,
}


# 処理関数の登録
def setDefaults(xmlui: XMLUI):
    for key in defaultFuncs:
        xmlui.setDrawFunc(key, defaultFuncs[key])
