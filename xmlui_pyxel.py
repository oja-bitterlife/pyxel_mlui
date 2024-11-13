from xmlui import XMLUI,UI_STATE,UI_ATTR
from xml.etree.ElementTree import Element

import pyxel

def drawArea(state: UI_STATE, attr: UI_ATTR, element: Element):
    border_size = attr.getInt("border_size", 1)
    border_color = attr.getInt("border_color", 7)
    fill_color = attr.getInt("fill_color", 12)
    padding = attr.getInt("padding", 8)

    pyxel.rect(state.area.x, state.area.y, state.area.w, state.area.h, fill_color)

# 処理関数テーブル
defaultFuncs= {
    "area": drawArea,
}


# 処理関数の登録
def setDefaults(xmlui: XMLUI):
    for key in defaultFuncs:
        xmlui.setDrawFunc(key, defaultFuncs[key])
