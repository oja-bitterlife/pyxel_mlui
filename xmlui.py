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


class UI_STATE:
    # XML構造
    element: Element  # 自身のElement
    parent: 'UI_STATE|None' = None# 親Element
    id: str|None = None  # <tag id="ID">

    # 表示関係
    area: RECT = RECT(0, 0, 4096, 4096)  # 描画範囲
    hide: bool = False # 非表示フラグ
    remove: bool = False  # 削除フラグ

    def __init__(self, element: Element):
        self.element = element

        # ステート取得
        if "id" in self.element.attrib:
            self.id = self.element.attrib["id"]
        self.hide = self.attrBool("hide", False)

    # attribアクセス用
    def attrInt(self, key: str, default: int) -> int:
        return int(self.element.attrib.get(key, default))

    def attrStr(self, key: str, default: str) -> str:
        return self.element.attrib.get(key, default)

    def attrBool(self, key: str, default: bool) -> bool:
        return bool(self.element.attrib.get(key, default))

    def getText(self) -> str:
        return self.element.text.strip() if self.element.text != None else ""

    # dictと同じように扱えるように
    def get(self, key: str, default: Any) -> str:
        return self.element.attrib.get(key, default)
    
    def hasKey(self, key: str) -> bool:
        return key in self.element.attrib

    def __getitem__(self, key: str) -> str:
        return self.element.attrib[key]

    def __setitem__(self, key: str, value: Any):
        self.element.attrib[key] = value



class XMLUI:
    root: UI_STATE
    state_map: dict[Element, UI_STATE] = {}  # 状態保存用

    update_funcs: dict[str, Callable[[UI_STATE], None]] = {}
    draw_funcs: dict[str, Callable[[UI_STATE], None]] = {}

    # 初期化
    # *************************************************************************
    # ファイルから読み込み
    @classmethod
    def createFromFile(cls, fileName: str):
        with open(fileName, "r", encoding="utf8") as f:
            return cls.createFromString(f.read())

    # リソースから読み込み
    @classmethod
    def createFromString(cls, xml_data: str):
            return XMLUI(xml.etree.ElementTree.fromstring(xml_data))

    # 初期化。<xmlui>を持つXMLを突っ込む
    def __init__(self, dom: xml.etree.ElementTree.Element):
        # 最上位がxmluiでなくてもいい
        if dom.tag == "xmlui":
            self.root = UI_STATE(dom)
        else:
            # 最上位でないときは子から探す
            xmlui_root = dom.find("xmlui")
            if xmlui_root is None:
                raise Exception("<xmlui> not found")
            else:
                self.root = UI_STATE(xmlui_root)

        # 状態保存用
        for element in self.root.element.iter():
            self.state_map[element] = UI_STATE(element)

    # XML操作用
    # *************************************************************************
    def findByID(self, id: str) -> UI_STATE|None:
        for state in self.state_map.values():
            if state.id == id:
                return state
        return None

    # 更新用
    # *************************************************************************
    # 全体を呼び出す処理
    def update(self):
        for element in self.root.element.iter():
            state = self.state_map[element]
            self.updateElement(element.tag, state)

        # ツリー構造の更新
        self._updateTree()

    def _updateTree(self):
        # removeされたElementを親に持つ子にもremoveフラグを立てる


        # 削除フラグ対応
        for state in self.state_map.values():
            if state.remove and state.parent != None:
                # XMLに反映
                state.parent.element.remove(state.element)
        # 辞書からも削除
        self.state_map = {key:val for key,val in self.state_map.items() if not val.remove}

        # parentの更新
        parent_map = {child: parent for parent in self.root.element.iter() for child in parent}
        for element in self.root.element.iter():
            # rootは処理しない
            if element == self.root.element:
                continue
            self.state_map[element].parent = self.state_map[parent_map[element]]  # 親を覚えておく

    # 描画用
    # *************************************************************************
    def draw(self):
        # 表示領域の更新
        self._updateArea()

        for element in self.root.element.iter():
            self.drawElement(element.tag, self.state_map[element])

    def _updateArea(self):
        # ツリーで更新
        for element in self.root.element.iter():
            state = self.state_map[element]

            # root(parent==None)は処理しない
            if state.parent == None:
                # 一応root以外のparentに設定ミスがないかチェックしておく
                if(state.element != self.root.element):
                    raise Exception(f"Element has not parent: {state.element.tag}")
                continue

            # 子のエリア設定
            # ---------------------------------------------
            # 親からのオフセットで計算
            _x = int(element.attrib.get("x", 0))
            _y = int(element.attrib.get("y", 0))
            w = int(element.attrib.get("w", state.parent.area.w))
            h = int(element.attrib.get("h", state.parent.area.h))

            # paddingも設定できるように
            _x += sum([int(element.attrib.get(name, 0)) for name in ["padding_x", "padding_l", "padding_size"]])
            w -= sum([int(element.attrib.get(name, 0)) for name in ["padding_x", "padding_size"]])*2
            _y += sum([int(element.attrib.get(name, 0)) for name in ["padding_y", "padding_t", "padding_size"]])
            h -= sum([int(element.attrib.get(name, 0)) for name in ["padding_y", "padding_size"]])*2
            w -= sum([int(element.attrib.get(name, 0)) for name in ["padding_l", "padding_r"]])
            h -= sum([int(element.attrib.get(name, 0)) for name in ["padding_t", "padding_b"]])

            # 親の中だけ表示するようにintersect
            state.area = RECT(state.parent.area.x+_x, state.parent.area.y+_y, w, h).intersect(state.parent.area)


    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def updateElement(self, name: str, state: UI_STATE):
        if name in self.update_funcs:
            self.update_funcs[name](state)

    def drawElement(self, name: str, state: UI_STATE):
        # 非表示
        if state.hide:
            return

        # 無駄な描画は無くす
        if state.attrBool("force_draw", False) and (state.area.w <= 0 or state.area.h <= 0):
            return

        if name in self.draw_funcs:
            self.draw_funcs[name](state)

    # 個別処理登録
    def setUpdateFunc(self, name: str, func: Callable[[UI_STATE], None]):
        self.update_funcs[name] = func

    def setDrawFunc(self, name: str, func: Callable[[UI_STATE], None]):
        self.draw_funcs[name] = func

