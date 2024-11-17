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


# UIパーツの状態保存用
class UI_STATE:
    # プロパティ定義
    # 一度しか初期化されないので定義と同時に配列等オブジェクトを代入すると事故る
    # のでconstructorで初期化する
    # XML構造
    element: Element  # 自身のElement
    parent: 'UI_STATE'  # 親Element
    remove: bool  # 削除フラグ
    append_list: list['UI_STATE']  # 追加リスト

    # 表示関係
    area: UI_RECT  # 描画範囲
    update_count: int  # 更新カウンター

    def __init__(self, element: Element):
        # プロパティの初期化
        self.element = element
        self.remove = False
        self.append_list = []

        self.area = UI_RECT(0, 0, 4096, 4096)
        self.update_count = 0

        # ステート取得
        if "id" in self.element.attrib:
            self.id = self.element.attrib["id"]

    # attribアクセス用
    def attrInt(self, key:str, default:int=0) -> int:
        return int(self.element.attrib.get(key, default))

    def attrStr(self, key:str, default:str="") -> str:
        return self.element.attrib.get(key, default)

    def attrBool(self, key:str, default:bool=False) -> bool:
        attr = self.element.attrib.get(key)
        return default if attr == None else (True if attr.lower() in ["true", "ok", "yes"] else False)

    def getText(self) -> str:
        return self.element.text.strip() if self.element.text != None else ""

    def hasAttr(self, key: str) -> bool:
        return key in self.element.attrib

    def setAttr(self, key: str, value: Any):
        self.element.attrib[key] = str(value)  # attribはdict[str,str]なのでstrで保存する

    @property
    def enable(self) -> bool:
        return self.attrBool("enable", True) and not self.attrBool("disable", False)

    @property
    def visible(self) -> bool:
        return self.attrBool("visible", True) and self.attrBool("show", True) and not self.attrBool("hide", False)

    # ツリー操作用
    def addChild(self, state:'UI_STATE'):
        self.append_list.append(state)

    def makeElement(self, name:str, attr:dict[str,str]={}) -> 'UI_STATE':
        return UI_STATE(self.element.makeelement(name, attr))

    def duplicate(self) -> 'UI_STATE':
        return UI_STATE(self.element.makeelement(self.element.tag, self.element.attrib.copy()))


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
    grid: list[list[Any]]  # グリッド
    state: UI_STATE  # 操作対象Element
    remove: bool  # 削除フラグ

    cur_x: int  # 現在位置x
    cur_y: int  # 現在位置y

    def __init__(self, grid:list[list[Any]], state:UI_STATE, init_cur_x:int=0, init_cur_y:int=0):
        self.grid = grid
        self.state = state
        self.remove = False
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
        return self.grid[self.cur_y][self.cur_x]

    # メニュー終了時処理
    def close(self):
        self.remove = True
        self.state.remove = True

    @property
    def width(self) -> int:
        return len(self.grid[self.cur_y])

    @property
    def height(self) -> int:
        return len(self.grid)

    @property
    def length(self) -> int:
        return sum([len(line) for line in self.grid])


# メニュー階層管理
class UI_MENU_GROUP:
    stack: list['UI_MENU|UI_MENU_GROUP']

    def __init__(self, menu_list:list['UI_MENU|UI_MENU_GROUP']|UI_MENU=[]):
        if isinstance(menu_list, UI_MENU):
            menu_list = [menu_list]
        self.stack = menu_list

    def push(self, menu: 'UI_MENU|UI_MENU_GROUP'):
        self.stack.append(menu)

    # メニューを閉じる
    def close(self):
        for menu in self.stack:
            menu.close()  # 子を全て閉じる

    def getActive(self) -> UI_MENU|None:
        available = [menu for menu in self.stack if not menu.remove]  # 生きてるものだけ取り出す
        if len(available) == 0:
            return None
        active = available[-1]
        if isinstance(active, UI_MENU):
            return active

        # グループならグループ内のactiveを返す
        return active.getActive()

    # 不要になったメニューを削除
    def update(self):
        for group in [group for group in self.stack if isinstance(group, UI_MENU_GROUP)]:
            group.update()  # 子も更新
        self.stack = [menu for menu in self.stack if not menu.remove]

    # メニューリスト内検索
    def findByID(self, id:str) -> UI_MENU|None:
        for menu in self.stack:
            if isinstance(menu, UI_MENU_GROUP):
                return menu.findByID(id)
            if menu.state.attrStr("id") == id:
                return menu
        return None

    def findByTag(self, tag:str) -> list[UI_MENU]:
        out = []
        for menu in self.stack:
            if isinstance(menu, UI_MENU_GROUP):
                out += menu.findByTag(tag)
            elif menu.state.element.tag == tag:
                out.append(menu)
        return out

    @property
    def remove(self) -> bool:
        return len(self.stack) == 0  # 空のグループは不要


# XMLでUIライブラリ本体
# #############################################################################
class XMLUI:
    root: UI_STATE
    state_map: dict[Element, UI_STATE]  # 状態保存用

    # メニュー管理
    menu: UI_MENU_GROUP

    # 処理関数の登録
    update_funcs: dict[str, Callable[['XMLUI',UI_STATE], None]]
    draw_funcs: dict[str, Callable[['XMLUI',UI_STATE], None]]

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
        self.state_map = {}
        self.menu = UI_MENU_GROUP()
        self.update_funcs = {}
        self.draw_funcs = {}

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
    def setID(self, state:UI_STATE, id:str):
        # グローバルキーなのでかぶってはいけない
        exists = [element.attrib["id"] for element in self.root.element.iter() if "id" in element.attrib]
        if id in exists:
            raise Exception(f"ID {id} already exists")
        state.setAttr("id", id)

    def findByID(self, id:str, root:UI_STATE|None=None) -> UI_STATE|None:
        rootElement = root.element if root != None else self.root.element
        for element in rootElement.iter():
            if element.attrib.get("id") == id:
                return self.state_map[element]
        return None

    def findByTag(self, tag:str, root:UI_STATE|None=None) -> list[UI_STATE]:
        out = []
        rootElement = root.element if root != None else self.root.element
        for element in rootElement.iter():
            if element.tag == tag:
                out.append(self.state_map[element])
        return out


    # Menu操作用
    # *************************************************************************
    def openMenu(self, menu:UI_MENU|UI_MENU_GROUP):
        self.menu.stack.append(menu)


    # 更新用
    # *************************************************************************
    # 全体を呼び出す処理
    def update(self):
        # 更新処理
        self._updateTreeRec(self.root.element)

        # ノードの追加と削除
        for state in self.state_map.values():
            # removeがマークされたノードは削除
            if state.remove and state != self.root:
                state.parent.element.remove(state.element)

            # appendされたノードを追加
            for child in state.append_list:
                state.element.append(child.element)
            state.append_list = []

        # Treeが変更されたかもなのでstateを更新
        self.state_map = XMLUI._makeState(self.root.element, self.state_map)

        # 不要になったメニューを削除
        self.menu.update()

    # ツリーのノード以下を再帰処理
    def _updateTreeRec(self, parent: Element):
        state = self.state_map[parent]

        # disableなら子も含めてUpdateしない
        if not state.enable:
            return

        # 更新処理
        self.updateElement(parent.tag, state)

        # 子の処理
        for child in parent:
            self._updateTreeRec(child)

        state.update_count += 1  # 実行後に更新

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
        if not state.visible or not state.enable:  # disable時も表示しない
            return

        # エリア更新
        if state != self.root:  # rootは親を持たないので更新不要
            state.area = UI_RECT(  # 親からのオフセットでarea計算
                state.attrInt("x", 0) + state.parent.area.x,
                state.attrInt("y", 0) + state.parent.area.y,
                state.attrInt("w", state.parent.area.w),
                state.attrInt("h", state.parent.area.h))

        # 子を上に描画するため親を先に描画する
        self.drawElement(parent.tag, state)

        # 子の描画
        for child in parent:
            self._drawTreeRec(child)


    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def updateElement(self, name: str, state: UI_STATE):
        # 登録済みの関数だけ実行
        if name in self.update_funcs:
            self.update_funcs[name](self, state)

    def drawElement(self, name: str, state: UI_STATE):
        # 登録済みの関数だけ実行
        if name in self.draw_funcs:
            self.draw_funcs[name](self, state)

    # 個別処理登録
    def setUpdateFunc(self, name: str, func: Callable[['XMLUI',UI_STATE], None]):
        self.update_funcs[name] = func

    def setDrawFunc(self, name: str, func: Callable[['XMLUI',UI_STATE], None]):
        self.draw_funcs[name] = func

