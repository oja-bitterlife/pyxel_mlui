from xmlui import XMLUI
from xml.etree.ElementTree import Element

import pyxel

def intAttr(attr: dict[str,str], name: str, default: int) -> int:
    return int(attr[name]) if name in attr else default

def strAttr(attr: dict[str,str], name: str, default: str) -> str:
    return attr[name] if name in attr else default

def drawArea(attr: dict[str,str], state: Element | None, element: Element):
    width = intAttr(attr, "width", pyxel.width)
    height = intAttr(attr, "height", pyxel.height)
    border_size = intAttr(attr, "border_size", 1)
    border_color = intAttr(attr, "border_color", 7)
    fill_color = intAttr(attr, "fill_color", 11)
    padding = intAttr(attr, "padding", 8)

    pyxel.rect(0, 0, width, height, fill_color)

# 処理関数テーブル
defaultFuncs= {
    "area": drawArea,
}


# 処理関数の登録
def setDefaults(xmlui: XMLUI):
    for key in defaultFuncs:
        xmlui.setDrawFunc(key, defaultFuncs[key])
