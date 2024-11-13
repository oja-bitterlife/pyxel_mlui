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

class UI_ATTR:
    def __init__(self, attr: dict[str, str]):
        self.attr = attr

    # ユーティリティ
    def getInt(self, key: str, default: int) -> int:
        return int(self.attr.get(key, default))

    def getStr(self, key: str, default: str) -> str:
        return self.attr.get(key, default)

    def getBool(self, key: str, default: bool) -> bool:
        return bool(self.attr.get(key, default))


    # dictと同じように扱えるように
    def get(self, key: str, default: Any) -> str:
        return self.attr.get(key, default)

    def __getitem__(self, key: str) -> str:
        return self.attr[key]

    def __setitem__(self, key: str, value: Any):
        self.attr[key] = value

    def __repr__(self) -> str:
        return self.attr.__repr__()



class UI_STATE:
    # 共通でもつもの
    parent: Element
    area: RECT

    # 個々で用意するもの
    def set(self, key:str, value:Any):
        setattr(self, key, value)

    def get(self, key:str, default:Any):
        getattr(self, key, default)


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
            state = self.state_map[element]

            # 自分のエリアを計算
            if element != self.root:
                # 親の中でしか活動できない
                parent = self.state_map[element].parent
                parent_area = self.state_map[parent].area

                # 親からのオフセットで計算
                _x = int(element.attrib.get("x", 0))
                _y = int(element.attrib.get("y", 0))
                w = int(element.attrib.get("w", parent_area.w))
                h = int(element.attrib.get("h", parent_area.h))

                # paddingも設定できるように
                _x += sum([int(element.attrib.get(name, 0)) for name in ["padding_x", "padding_l", "padding_size"]])
                w -= sum([int(element.attrib.get(name, 0)) for name in ["padding_x", "padding_size"]])*2
                _y += sum([int(element.attrib.get(name, 0)) for name in ["padding_y", "padding_t", "padding_size"]])
                h -= sum([int(element.attrib.get(name, 0)) for name in ["padding_y", "padding_size"]])*2
                w -= sum([int(element.attrib.get(name, 0)) for name in ["padding_l", "padding_r"]])
                h -= sum([int(element.attrib.get(name, 0)) for name in ["padding_t", "padding_b"]])

                state.area = RECT(parent_area.x+_x, parent_area.y+_y, w, h).intersect(parent_area)

            self.drawElement(element.tag, state, UI_ATTR(element.attrib), element)


    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def updateElement(self, name: str, state: UI_STATE, attr: UI_ATTR, element: Element):
        if name in self.update_funcs:
            self.update_funcs[name](state, attr, element)

    def drawElement(self, name: str, state: UI_STATE, attr: UI_ATTR, element: Element):
        # 非表示
        if attr.getBool("hide", False):
            return

        # 無駄な描画は無くす
        if attr.getBool("force_draw", False) and (state.area.w <= 0 or state.area.h <= 0):
            return

        if name in self.draw_funcs:
            self.draw_funcs[name](state, attr, element)

    # 個別処理登録
    def setUpdateFunc(self, name: str, func: Callable[[UI_STATE, UI_ATTR, Element], None]):
        self.update_funcs[name] = func

    def setDrawFunc(self, name: str, func: Callable[[UI_STATE, UI_ATTR, Element], None]):
        self.draw_funcs[name] = func
