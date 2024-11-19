import xml.etree.ElementTree
from xml.etree.ElementTree import Element
from typing import Callable,Any

import re, copy

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
    id:str # 識別名
    _state: 'UI_STATE'  # 参照
    _grid: list[list[Any]]  # グリッド

    cur_x: int  # 現在位置x
    cur_y: int  # 現在位置y

    def __init__(self, id:str, state:'UI_STATE', grid:list[list[Any]]=[], init_cur_x:int=0, init_cur_y:int=0):
        self.id = id
        self._state = state
        self._grid = grid
        self.cur_x, self.cur_y = (init_cur_x, init_cur_y)

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
        return self._grid[self.cur_y][self.cur_x]

    # イベント発火
    def on(self, event:str) -> 'UI_MENU':
        self._state.on(event)
        return self

    @property
    def width(self) -> int:
        return len(self._grid[self.cur_y])

    @property
    def height(self) -> int:
        return len(self._grid)

    @property
    def length(self) -> int:
        return sum([len(line) for line in self._grid])


# UIパーツの状態管理ラッパー
class UI_STATE:
    _xmlui: 'XMLUI'  # ライブラリへのIF
    _element: Element  # 自身のElement

    def __init__(self, xmlui:'XMLUI', element: Element):
        # プロパティの初期化
        self._xmlui = xmlui
        self._element = element


    # attribアクセス用
    # *************************************************************************
    def attrInt(self, key:str, default:int=0) -> int:
        return int(self._element.attrib.get(key, default))

    def attrStr(self, key:str, default:str="") -> str:
        return self._element.attrib.get(key, default)

    def attrBool(self, key:str, default:bool=False) -> bool:
        attr = self._element.attrib.get(key)
        return default if attr is None else (True if attr.lower() in ["true", "ok", "yes"] else False)

    def getText(self) -> str:
        return self._element.text.strip() if self._element.text != None else ""

    def hasAttr(self, key: str) -> bool:
        return key in self._element.attrib

    def setAttr(self, key: str, value: Any) -> 'UI_STATE':
        self._element.attrib[key] = str(value)  # attribはdict[str,str]なのでstrで保存する
        return self

    @property
    def is_enable(self) -> bool:
        return self.attrBool("enable", True)

    @property
    def is_visible(self) -> bool:
        return self.attrBool("visible", True)

    @property
    def id(self) -> str:
        return self.attrStr("id", "")

    @property
    def tag(self) -> str:
        return self._element.tag

    @property
    def area(self) -> UI_RECT:
        return UI_RECT(self.attrInt("area_x"), self.attrInt("area_y"), self.attrInt("area_w", 4096), self.attrInt("area_h", 4096))


    # ツリー操作用
    # *************************************************************************
    def addChild(self, child:'UI_STATE') -> 'UI_STATE':
        self._element.append(child._element)
        return self

    def remove(self):
        parent = self.parent
        if parent is not None:
            parent._element.remove(self._element)

    def findByID(self, id:str) -> 'UI_STATE':
        for element in self._element.iter():
            if element.attrib.get("id") == id:
                return UI_STATE(self._xmlui, element)
        raise Exception(f"ID '{id}' not found in '{self.tag}' and children")

    def findByTagAll(self, tag:str) -> list['UI_STATE']:
        return [UI_STATE(self._xmlui, element) for element in self._element.iter() if element.tag == tag]

    def findByTag(self, tag:str) -> 'UI_STATE':
        elements = self.findByTagAll(tag)
        if elements:
            return elements[0]
        raise Exception(f"Tag '{tag}' not found in '{self.tag}' and children")

    @property
    def parent(self) -> 'UI_STATE|None':
        def _rec_parentSearch(element:Element, me:Element) -> Element|None:
            if me in element:
                return element
            for child in element:
                result = _rec_parentSearch(child, me)
                if result is not None:
                    return result
            return None
        parent = _rec_parentSearch(self._xmlui.root._element, self._element)
        return UI_STATE(self._xmlui, parent) if parent is not None else None


    # イベント管理用
    # *************************************************************************
    def openMenu(self, id:str, grid:list[list[Any]]=[], init_cur_x:int=0, init_cur_y:int=0) -> 'UI_STATE':
        self._xmlui._menu_map[self._element] = UI_MENU(id, self, grid, init_cur_x, init_cur_y)
        return self

    def getActiveMenu(self) -> UI_MENU|None:
        menus = [self._xmlui._menu_map[element] for element in self._element.iter() if element in self._xmlui._menu_map]
        return menus[-1] if menus else None

    def on(self, event:str) -> 'UI_STATE':
        self._xmlui.on(self, event)
        return self

    @property
    def menu(self) -> UI_MENU|None:
        return self._xmlui._menu_map.get(self._element, None)


    # デバッグ用
    # *************************************************************************
    def strTree(self, indent:str="  ", pre:str="") -> str:
        out = pre + self.tag
        out += ": " + self.attrStr("id") if "id" in self._element.attrib else ""
        out += " [menu]" if self._element not in self._xmlui._menu_map else ""
        for element in self._element:
            out += "\n" + UI_STATE(self._xmlui, element).strTree(indent, pre+indent)
        return out


# XMLでUIライブラリ本体
# #############################################################################
class XMLUI:
    root: UI_STATE
    _event_map: dict[Element, set[str]]  # イベント通知用
    _menu_map: dict[Element, UI_MENU]  # メニュー用

    # 処理関数の登録
    _update_funcs: dict[str, Callable[[UI_STATE,set[str]], None]]
    _draw_funcs: dict[str, Callable[[UI_STATE], None]]

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
        # elementの追加ステート
        self._event_map = {}
        self._menu_map = {}

        # 更新処理
        self._update_funcs = {}
        self._draw_funcs = {}

        # root_tag指定が無ければ最上位エレメント
        if root_tag is None:
            xmlui_root = dom
        else:
            # Noneでないときは子から探す
            xmlui_root = dom.find(root_tag)
            # 見つからなかったら未対応のXML
            if xmlui_root is None:
                raise Exception(f"<{root_tag}> not found")

        # rootを取り出しておく
        self.root = UI_STATE(self, xmlui_root)

    # Elmentを複製する
    def duplicate(self, src:Element|UI_STATE) -> UI_STATE:
        return UI_STATE(self, copy.deepcopy(src._element if isinstance(src, UI_STATE) else src))


    # XML操作
    # *************************************************************************
    def addChild(self, child:'UI_STATE') -> 'UI_STATE':
        return self.root.addChild(child)

    def findByID(self, id:str) -> UI_STATE:
        return self.root.findByID(id)

    def findByTagAll(self, tag:str) -> list[UI_STATE]:
        return self.root.findByTagAll(tag)

    def findByTag(self, tag:str) -> UI_STATE:
        return self.root.findByTag(tag)


    # 処理登録
    # *************************************************************************
    def setUpdateFunc(self, name:str, func:Callable[[UI_STATE,set[str]], None]):
        self._update_funcs[name] = func

    def setDrawFunc(self, name:str, func:Callable[[UI_STATE], None]):
        self._draw_funcs[name] = func

    def on(self, src:Element|UI_STATE, event:str):
        element = src._element if isinstance(src, UI_STATE) else src
        if src not in self._event_map:
            self._event_map[element] = set([])
        self._event_map[element].add(event)


    # 更新用
    # *************************************************************************
    def update(self):
        # 更新処理
        for element in self._rec_getUpdateElements(self.root._element):
            self.updateElement(element.tag, UI_STATE(self, element), self._event_map.get(element, set([])))

        # 状態のリセット
        self._event_map.clear()

    # updateが必要な要素をTree順で取り出す
    def _rec_getUpdateElements(self, element:Element) -> list[Element]:
        out: list[Element] = []
        # まず兄弟を処理
        for child in element:
            # disableな子は処理しない
            if child.attrib.get("enable", True):
                out.append(child)

        # その後子を再帰
        for child in element:
            # disableな子は処理しない
            if child.attrib.get("enable", True):
                out += self._rec_getUpdateElements(child)
        return out


    # 描画用
    # *************************************************************************
    def draw(self):
        # 更新対象Elementを取得
        draw_states = [UI_STATE(self, element) for element in self._rec_getDrawElements(self.root._element)]

        # エリア更新
        for state in draw_states:
            # if(state.tag == "menu_item"):
            #     print(state.parent)

            if state.parent is not None:  # rootは親を持たないので更新不要
                state.setAttr("area_x", state.attrInt("x") + state.parent.attrInt("area_x"))  # オフセット
                state.setAttr("area_y", state.attrInt("y") + state.parent.attrInt("area_y"))  # オフセット
                state.setAttr("area_w", state.attrInt("w", state.parent.attrInt("area_w")))
                state.setAttr("area_h", state.attrInt("h", state.parent.attrInt("area_h")))

        # 描画処理
        for state in draw_states:
            self.drawElement(state.tag, state)

    # drawが必要な要素をTree順で取り出す
    def _rec_getDrawElements(self, element:Element) -> list[Element]:
        out: list[Element] = []
        # まず兄弟を処理
        for child in element:
            # disableな子は処理しない
            if child.attrib.get("enable", True) and child.attrib.get("visible", True):
                out.append(child)

        # その後子を再帰
        for child in element:
            # disableな子は処理しない
            if child.attrib.get("enable", True) and child.attrib.get("visible", True):
                out += self._rec_getDrawElements(child)
        return out


    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def updateElement(self, name:str, state:UI_STATE, events:set[str]):
        # 登録済みの関数だけ実行
        if name in self._update_funcs:
            self._update_funcs[name](state, events)

    def drawElement(self, name:str, state:UI_STATE):
        # 登録済みの関数だけ実行
        if name in self._draw_funcs:
            self._draw_funcs[name](state)

