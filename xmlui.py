import xml.etree.ElementTree
from xml.etree.ElementTree import Element
from typing import Callable,Any

class RECT:
    def __init__(self, x:int, y:int, w:int, h:int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def intersect(self, other):
        right = min(self.x+self.w, other.x+other.w)
        left = max(self.x, other.x)
        bottom = min(self.y+self.h, other.y+other.h)
        top = max(self.y, other.y)
        return RECT(left, top, right-left, bottom-top)
    
    def contains(self, x, y):
        return self.x <= x < self.x+self.w and self.y <= y < self.y+self.h

    def __repr__(self) -> str:
        return f"RECT({self.x}, {self.y}, {self.w}, {self.h})"

class UI_ATTR(dict):
    def __init__(self, attr: dict[str, str]):
        self.attr = attr

    # ユーティリティ
    def getInt(self, name: str, default: int) -> int:
        return int(self.attr[name]) if name in self.attr else default

    def getStr(self, name: str, default: str) -> str:
        return self.attr[name] if name in self.attr else default


class UI_STATE(dict):
    parent: Element
    area: RECT

class XMLUI:
    root: Element
    state_map: dict[Element, UI_STATE]  # 状態保存用

    update_funcs: dict[str, Callable[[UI_STATE, UI_ATTR, Element], None]] = {}
    draw_funcs: dict[str, Callable[[UI_STATE, UI_ATTR, Element], None]] = {}

    # ファイルから読み込み
    @classmethod
    def createFromFile(cls, fileName: str):
        with open(fileName, "r") as f:
            return cls.createFromString(f.read())

    # リソースから読み込み
    @classmethod
    def createFromString(cls, xml_data: str):
            return XMLUI(xml.etree.ElementTree.fromstring(xml_data))

    # 初期化。<xmlui>を持つXMLを突っ込む
    def __init__(self, dom: xml.etree.ElementTree.Element):
        # 最上位がxmluiでなくてもいい
        if dom.tag == "xmlui":
            self.root = dom
        else:
            # 最上位でないときは子から探す
            xmlui = dom.find("xmlui")
            if xmlui is None:
                raise Exception("<xmlui> not found")
            else:
                self.root = xmlui

        # 状態保存用
        self.state_map = {self.root: UI_STATE()}
        for element in self.root.iter():
            self.state_map[element] = UI_STATE()


    # 全体を呼び出す処理
    def update(self):
        for element in self.root.iter():
            state = self.state_map[element]
            attr = UI_ATTR(element.attrib)
            self.updateElement(element.tag, state, attr, element)

        # parentの更新
        parent_map = {c: p for p in self.root.iter() for c in p}
        for element in self.root.iter():
            if element != self.root:
                self.state_map[element].parent = parent_map[element]  # 親をstateに覚えておく

    def draw(self, x, y, w, h):
        self.state_map[self.root].area = RECT(x,y,w,h)

        for element in self.root.iter():
            state: dict[str,Any] = self.state_map[element]

            # 自分のエリアを計算
            if element != self.root:
                # 親の中でしか活動できない
                parent = self.state_map[element].parent
                parent_area = self.state_map[parent].area
                # 親からのオフセットで計算
                _x = int(element.attrib["x"]) if "x" in element.attrib else 0
                _y = int(element.attrib["y"]) if "y" in element.attrib else 0
                w = int(element.attrib["w"]) if "w" in element.attrib else parent_area.w-_x
                h = int(element.attrib["h"]) if "h" in element.attrib else parent_area.h-_y
                state.area = RECT(parent_area.x+_x, parent_area.y+_y, w, h).intersect(parent_area)

            self.drawElement(element.tag, state, UI_ATTR(element.attrib), element)


    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def updateElement(self, name: str, state: UI_STATE, attr: UI_ATTR, element: Element):
        if name in self.update_funcs:
            self.update_funcs[name](state, attr, element)

    def drawElement(self, name: str, state: UI_STATE, attr: UI_ATTR, element: Element):
        # 無駄な描画は無くす
        if "force_draw" not in attr and (state.area.w <= 0 or state.area.h <= 0):
            return

        if name in self.draw_funcs:
            self.draw_funcs[name](state, attr, element)

    # 個別処理登録
    def setUpdateFunc(self, name: str, func: Callable[[UI_STATE, UI_ATTR, Element], None]):
        self.update_funcs[name] = func

    def setDrawFunc(self, name: str, func: Callable[[UI_STATE, UI_ATTR, Element], None]):
        self.draw_funcs[name] = func
