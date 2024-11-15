import xml.etree.ElementTree
from xml.etree.ElementTree import Element
from typing import Callable,Any

class UI_RECT:
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
        return UI_RECT(left, top, right-left, bottom-top)
    
    def contains(self, x, y):
        return self.x <= x < self.x+self.w and self.y <= y < self.y+self.h

    def __repr__(self) -> str:
        return f"RECT({self.x}, {self.y}, {self.w}, {self.h})"


class UI_STATE:
    # XML構造
    element: Element  # 自身のElement
    parent: 'UI_STATE|None' = None # 親Element
    id: str|None = None  # <tag id="ID">

    # 表示関係
    area: UI_RECT = UI_RECT(0, 0, 4096, 4096)  # 描画範囲
    hide: bool = False # 非表示フラグ

    # 制御関係
    update_count : int = 0  # 更新カウンター
    remove: bool = False  # 削除フラグ
    append_list: list['UI_STATE'] = []  # 追加リスト

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
        attr = self.element.attrib.get(key)
        return default if attr == None else (True if attr.lower() == "true"else False)

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
            xmlui_root = dom
        else:
            # 最上位でないときは子から探す
            xmlui_root = dom.find("xmlui")
            # 見つからなかったら未対応のXML
            if xmlui_root is None:
                raise Exception("<xmlui> not found")

        # state_mapの作成
        self.state_map = XMLUI._makeState(xmlui_root, {})

        # rootを取り出しておく
        self.root = self.state_map[xmlui_root]


    # XML操作用
    # *************************************************************************
    def findByID(self, id: str) -> UI_STATE|None:
        for state in self.state_map.values():
            if state.id == id:
                return state
        return None

    def addChild(self, parent:UI_STATE, child:UI_STATE):
        parent.append_list.append(child)

    def addLast(self, befor:UI_STATE, child:UI_STATE):
        if befor.parent == None:
            raise Exception("root is not have a paret")
        befor.parent.append_list.append(child)


    # 更新用
    # *************************************************************************
    # 全体を呼び出す処理
    def update(self):
        # 各ノードのUpdate
        for element in self.root.element.iter():
            state = self.state_map[element]

            # 更新処理
            self.updateElement(element.tag, state)
            state.update_count += 1  # 実行後に更新

        # removeがマークされたノード(以下)を削除
        for state in self.state_map.values():
            if state.remove and state.parent != None:
                state.parent.element.remove(state.element)
                state.parent = None

        # appendがマークされたノードを追加
        for state in self.state_map.values():
            for child in state.append_list:
                state.element.append(child)
            state.append_list = []

        # Treeが変更されたかもなのでstateを更新
        self.state_map = XMLUI._makeState(self.root.element, self.state_map)

    # stateの更新
    @classmethod
    def _makeState(cls, root_element: Element, old_map: dict[Element,UI_STATE]) -> dict[Element,UI_STATE]:
        # state_mapの更新
        state_map = {element: old_map.get(element, UI_STATE(element)) for element in root_element.iter()}

        # state_mapのparentを更新
        def _updateStateParentRec(parent: Element):
            for child in parent:
                state_map[child].parent = state_map[parent]
                _updateStateParentRec(child)
        _updateStateParentRec(root_element)

        return state_map


    # 描画用
    # *************************************************************************
    def draw(self):
        # ツリーの描画
        self._drawTreeRec(self.root.element)

    # ツリーのノード以下を再帰処理
    def _drawTreeRec(self, parent: Element):
        state = self.state_map[parent]

        # 非表示なら子も含めて描画しない
        if state.hide:
            return

        # 親を先に描画する(子を上に描画)
        state.area = XMLUI._updateArea(state)  # エリア更新
        self.drawElement(parent.tag, state)

        # 子の処理
        for node in parent:
            self._drawTreeRec(node)

    # 子のエリア設定(親のエリア内に収まるように)
    @classmethod
    def _updateArea(cls, state:UI_STATE) -> UI_RECT:
        # rootの場合はなにもしない
        if state.parent == None:
            return state.area

        element = state.element

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
        return UI_RECT(state.parent.area.x+_x, state.parent.area.y+_y, w, h).intersect(state.parent.area)


    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def updateElement(self, name: str, state: UI_STATE):
        if name in self.update_funcs:
            self.update_funcs[name](state)

    def drawElement(self, name: str, state: UI_STATE):
        # 無駄な描画は無くす
        if state.area.w <= 0 or state.area.h <= 0:
            # 強制描画の時は無駄でも描画する
            if  not state.attrBool("force_draw", False):
                return

        if name in self.draw_funcs:
            self.draw_funcs[name](state)

    # 個別処理登録
    def setUpdateFunc(self, name: str, func: Callable[[UI_STATE], None]):
        self.update_funcs[name] = func

    def setDrawFunc(self, name: str, func: Callable[[UI_STATE], None]):
        self.draw_funcs[name] = func

