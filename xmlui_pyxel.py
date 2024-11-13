from xmlui import XMLUI,UI_STATE
from xml.etree.ElementTree import Element

import pyxel

def intAttr(attr: dict[str,str], name: str, default: int) -> int:
    return int(attr[name]) if name in attr else default

def strAttr(attr: dict[str,str], name: str, default: str) -> str:
    return attr[name] if name in attr else default

def drawArea(state: UI_STATE, attr: dict[str,str], element: Element):
    border_size = intAttr(attr, "border_size", 1)
    border_color = intAttr(attr, "border_color", 7)
    fill_color = intAttr(attr, "fill_color", 11)
    padding = intAttr(attr, "padding", 8)

    print(state.area)
    pyxel.rect(state.area.x, state.area.y, state.area.w, state.area.h, fill_color)

# 処理関数テーブル
defaultFuncs= {
    "area": drawArea,
}


# 処理関数の登録
def setDefaults(xmlui: XMLUI):
    for key in defaultFuncs:
        xmlui.setDrawFunc(key, defaultFuncs[key])
