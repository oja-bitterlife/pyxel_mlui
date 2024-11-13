from xmlui import XMLUI,UI_STATE,UI_ATTR
from xml.etree.ElementTree import Element

import pyxel

def fill(state: UI_STATE, attr: UI_ATTR, element: Element):
    color = attr.getInt("color", 12)
    pyxel.rect(state.area.x, state.area.y, state.area.w, state.area.h, color)

# 処理関数テーブル
defaultFuncs= {
    "fill": fill,
}


# 処理関数の登録
def setDefaults(xmlui: XMLUI):
    for key in defaultFuncs:
        xmlui.setDrawFunc(key, defaultFuncs[key])
