import xml.etree.ElementTree
from xml.etree.ElementTree import Element
from typing import Callable,Any

import re

# 描画領域計算用
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
    
    def contains(self, x, y) -> bool:
        return self.x <= x < self.x+self.w and self.y <= y < self.y+self.h

    def __repr__(self) -> str:
        return f"RECT({self.x}, {self.y}, {self.w}, {self.h})"


# テキスト表示用
class UI_TEXT:
    src: str  # パラメータ置換済み文字列
    tokens: list[str]  # 行(+wrap)分割済み文字列

    # 改行とwrapで分割する
    def __init__(self, text:str, params:dict[str,Any]={}, wrap:int=1024, sepexp=r"\n|\\n"):
        self.src = text.format(**params)
        self.tokens = []

        # 行分割
        lines = re.split(sepexp, self.src)

        # wrap分割
        for line in lines:
            while(len(line) > wrap):
                self.tokens.append(line[:wrap])
                line = line[wrap:]
            # 残りを保存
            if len(line) > 0:
                self.tokens.append(line[:wrap])

    # 最大文字数に減らして取得
    def getTokens(self, limit:int=65535):
        limit = int(limit)  # 計算式だとfloatが型チェックをスルーする
        out = []

        count = 0
        for token in self.tokens:
            # limitに届いていない間はそのまま保存
            if len(token)+count < limit:
                out.append(token)
                count += len(token)
            # limitを越えそう
            else:
                # limitまで取得
                over = token[:limit-count]
                if len(over) > 0:
                    out.append(over)
                break

        return out

    @property
    def length(self) -> int:
        return len("".join(self.tokens))


# 表内移動Wrap付き
class UI_MENU:
    state: 'UI_STATE|None'
    grid: list[list[Any]]  # グリッド

    cur_x: int  # 現在位置x
    cur_y: int  # 現在位置y

    def __init__(self, id:str, grid:list[list[Any]]=[], init_cur_x:int=0, init_cur_y:int=0):
        self.id = id
        self.state = None
        self.grid = grid
        self.cur_x, self.cur_y = (init_cur_x, init_cur_y)

    def close(self):
        if self.state is not None:
            self.state._remove = True

    # 範囲限定付き座標設定
    def setPos(self, x:int, y:int, wrap:bool=False) -> 'UI_MENU':
        self.cur_x, self.cur_y = ((x + self.width) % self.width, (y + self.height) % self.height) if wrap else (max(min(x, self.width-1), 0), max(min(y, self.height-1), 0))
        return self

    def moveUp(self, wrap:bool=False) -> 'UI_MENU':
        return self.setPos(self.cur_x, self.cur_y-1, wrap)

    def moveDown(self, wrap:bool=False) -> 'UI_MENU':
        return self.setPos(self.cur_x, self.cur_y+1, wrap)

    def moveLeft(self, wrap:bool=False) -> 'UI_MENU':
        return self.setPos(self.cur_x-1, self.cur_y, wrap)

    def moveRight(self, wrap:bool=False) -> 'UI_MENU':
        return self.setPos(self.cur_x+1, self.cur_y, wrap)

    # girdの内容取得
    def getData(self) -> Any:
        return self.grid[self.cur_y][self.cur_x]

    @property
    def width(self) -> int:
        return len(self.grid[self.cur_y])

    @property
    def height(self) -> int:
        return len(self.grid)

    @property
    def length(self) -> int:
        return sum([len(line) for line in self.grid])


# UIパーツの状態保存用
class UI_STATE:
    # プロパティ定義
    # 一度しか初期化されないので定義と同時に配列等オブジェクトを代入すると事故る
    # のでconstructorで初期化する

    # ライブラリ用。アプリ側で使うのは非推奨
    _xmlui: 'XMLUI'  # ライブラリへのIF
    _parent: 'UI_STATE'  # 親Element
    _remove: bool  # 削除フラグ
    _append_list: list['UI_STATE']  # 追加リスト

    # XML構造
    element: Element  # 自身のElement

    # メニュー管理
    menu: UI_MENU|None

    def __init__(self, xmlui:'XMLUI', element: Element):
        # プロパティの初期化
        self._xmlui = xmlui
        self._remove = False
        self._append_list = []

        self.element = element

        self.menu = None

    # attribアクセス用
    # *************************************************************************
    def attrInt(self, key:str, default:int=0) -> int:
        return int(self.element.attrib.get(key, default))

    def attrStr(self, key:str, default:str="") -> str:
        return self.element.attrib.get(key, default)

    def attrBool(self, key:str, default:bool=False) -> bool:
        attr = self.element.attrib.get(key)
        return default if attr is None else (True if attr.lower() in ["true", "ok", "yes"] else False)

    def getText(self) -> str:
        return self.element.text.strip() if self.element.text != None else ""

    def hasAttr(self, key: str) -> bool:
        return key in self.element.attrib

    def setAttr(self, key: str, value: Any) -> 'UI_STATE':
        self.element.attrib[key] = str(value)  # attribはdict[str,str]なのでstrで保存する
        return self

    @property
    def is_enable(self) -> bool:
        return self.attrBool("enable", True)

    @property
    def is_visible(self) -> bool:
        return self.attrBool("visible", True)

    @property
    def area(self) -> UI_RECT:
        return UI_RECT(self.attrInt("area_x"), self.attrInt("area_y"), self.attrInt("area_w", 4096), self.attrInt("area_h", 4096))

    # ツリー操作用
    # *************************************************************************
    def addChild(self, state:'UI_STATE') -> 'UI_STATE':
        self._append_list.append(state)

        state._parent = self  # 親の更新
        self._xmlui.state_map[state.element] = state  # すぐに使えるように登録しておく
        return state

    def dupAddChild(self, state:'UI_STATE') -> 'UI_STATE':
        return self.addChild(self._xmlui.duplicate(state))

    def remove(self):
        self._remove = True

    def findByID(self, id:str) -> 'UI_STATE':
        for element in self.element.iter():
            if element.attrib.get("id") == id:
                return self._xmlui.state_map[element]
        raise Exception(f"ID '{id}' not found in '{self.element.tag}'")

    def findByTagAll(self, tag:str) -> list['UI_STATE']:
        return [self._xmlui.state_map[element] for element in self.element.iter() if element.tag == tag]

    def findByTag(self, tag:str) -> 'UI_STATE':
        elements = self.findByTagAll(tag)
        if elements:
            return elements[0]
        raise Exception(f"Tag '{tag}' not found in '{self.element.tag}'")

    @property
    def is_remove(self) -> bool:
        return self._remove

    def updateTree(self) -> 'UI_STATE':
        # appendされたノードを追加
        for child in self._append_list:
            self.element.append(child.element)

        # removeがマークされたノードは削除
        if self._remove and self._parent is not None:
            self._parent.element.remove(self.element)

        # 子もUpdate
        for child in self._append_list:
            child.updateTree()

        self._append_list = []
        return self


    # Menu操作用
    # *************************************************************************
    def openMenu(self, menu:UI_MENU) -> 'UI_STATE':
        self.menu = menu
        menu.state = self
        return self

    def getActiveMenu(self) -> UI_MENU|None:
        # 子までたぐりきる
        for child in self.element:
            state = self._xmlui.state_map[child]
            if state.menu is not None:
                return state.menu
        return self.menu


    # デバッグ用
    # *************************************************************************
    def strTree(self, indent:str="  ", pre:str="") -> str:
        out = pre + self.element.tag
        out += ": " + self.attrStr("id") if "id" in self.element.attrib else ""
        out += " [menu]" if self.menu is not None else ""
        for element in self.element:
            out += "\n" + self._xmlui.state_map[element].strTree(indent, pre+indent)
        return out


# XMLでUIライブラリ本体
# #############################################################################
class XMLUI:
    root: UI_STATE
    state_map: dict[Element, UI_STATE]  # 状態保存用

    # 処理関数の登録
    update_funcs: dict[str, Callable[[UI_STATE], None]]
    draw_funcs: dict[str, Callable[[UI_STATE], None]]

    # 初期化
    # *************************************************************************
    # ファイルから読み込み
    @classmethod
    def createFromFile(cls, fileName:str, root_tag:str|None=None):
        with open(fileName, "r", encoding="utf8") as f:
            return cls.createFromString(f.read())

    # リソースから読み込み
    @classmethod
    def createFromString(cls, xml_data:str, root_tag:str|None=None):
        return XMLUI(xml.etree.ElementTree.fromstring(xml_data))

    # ワーカーの作成
    @classmethod
    def createWorker(cls, root_tag:str):
        return XMLUI(Element(root_tag))

    # 初期化。<xmlui>を持つXMLを突っ込む
    def __init__(self, dom:xml.etree.ElementTree.Element, root_tag:str|None=None):
        self.state_map = {}
        self.update_funcs = {}
        self.draw_funcs = {}

        # root_tag指定が無ければ最上位エレメント
        if root_tag is None:
            xmlui_root = dom
        else:
            # Noneでないときは子から探す
            xmlui_root = dom.find(root_tag)
            # 見つからなかったら未対応のXML
            if xmlui_root is None:
                raise Exception(f"<{root_tag}> not found")

        # state_mapの作成
        self._updateState(xmlui_root, {})

        # rootを取り出しておく
        self.root = self.state_map[xmlui_root]

    def duplicate(self, src_state:UI_STATE) -> UI_STATE:
        # まずは複製
        dup_state =  UI_STATE(self, src_state.element.makeelement(src_state.element.tag, src_state.element.attrib.copy()))
        dup_state.element.text = src_state.element.text

        # 子も複製してぶら下げておく
        for child in src_state.element:
            dup_child = self.duplicate(src_state._xmlui.state_map[child])
            dup_state.addChild(dup_child)

        return dup_state

    # 更新用
    # *************************************************************************
    # 全体を呼び出す処理
    def update(self):
        # 更新処理
        self._updateTreeRec(self.root.element)

        # ノードの追加と削除
        self.root.updateTree()

        # Treeが変更されたかもなのでstateを更新
        self._updateState(self.root.element, self.state_map)

    # ツリーのノード以下を再帰処理
    def _updateTreeRec(self, element: Element):
        state = self.state_map[element]

        # disableなら子も含めてUpdateしない
        if not state.is_enable:
            return

        # 更新処理
        self.updateElement(element.tag, state)

        # 子の処理
        for child in element:
            self._updateTreeRec(child)

    # stateの更新
    def _updateState(self, root_element: Element, old_map: dict[Element,UI_STATE]):
        # state_mapの更新
        self.state_map = {element: old_map.get(element, UI_STATE(self, element)) for element in root_element.iter()}

        # state_mapのparentを更新
        def _updateStateParentRec(parent: Element):
            for child in parent:
                self.state_map[child]._parent = self.state_map[parent]
                _updateStateParentRec(child)
        _updateStateParentRec(root_element)


    # 描画用
    # *************************************************************************
    def draw(self):
        # ツリーの描画
        self._drawTreeRec(self.root.element)

    # ツリーのノード以下を再帰処理
    def _drawTreeRec(self, element: Element):
        state = self.state_map[element]

        # 非表示なら子も含めて描画しない
        if not state.is_visible or not state.is_enable:  # disable時も表示しない
            return

        # エリア更新
        if state != self.root:  # rootは親を持たないので更新不要
            state.setAttr("area_x", state.attrInt("x") + state._parent.attrInt("area_x"))  # オフセット
            state.setAttr("area_y", state.attrInt("y") + state._parent.attrInt("area_y"))  # オフセット
            state.setAttr("area_w", state.attrInt("w", state._parent.attrInt("area_w")))
            state.setAttr("area_h", state.attrInt("h", state._parent.attrInt("area_h")))

        # 子を上に描画するため親を先に描画する
        self.drawElement(element.tag, state)

        # 子の描画
        for child in element:
            self._drawTreeRec(child)


    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def updateElement(self, name:str, state:UI_STATE):
        # 登録済みの関数だけ実行
        if name in self.update_funcs:
            self.update_funcs[name](state)

    def drawElement(self, name:str, state:UI_STATE):
        # 登録済みの関数だけ実行
        if name in self.draw_funcs:
            self.draw_funcs[name](state)

    # 個別処理登録
    def setUpdateFunc(self, name:str, func:Callable[[UI_STATE], None]):
        self.update_funcs[name] = func

    def setDrawFunc(self, name:str, func:Callable[[UI_STATE], None]):
        self.draw_funcs[name] = func

