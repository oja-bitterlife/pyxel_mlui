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

    # 改行とwrapで分割する
    def __init__(self, text:str, params:dict[str,Any]={}, sepexp:str=r"\n|\\n"):
        self.src = re.sub(sepexp, "\n", text.format(**params))  # 改行コードで統一

    # 最大文字数に減らして取得
    def getTokens(self, limit:int=65535, wrap:int=1024) -> list[str]:
        tokens:list[str] = []
        for line in self.src[:int(limit)].splitlines():  # 行分割
            tokens += [line[i:i+wrap] for i in range(0, len(line), wrap)]  # wrap分割
        return tokens

    @property
    def length(self) -> int:
        return len(self.src.replace("\n", ""))  # 改行を外してカウント


class UI_INPUT:
    # 入力状態の保存
    _input:list[str]
    _old:list[str]
    _trg:list[str]
    _release:list[str]

    def __init__(self):
        self._input = []
        self._old = []

    # 更新
    def update(self):
        _trg = [i for i in self._input if i not in self._old]
        _relase = [i for i in self._old if i not in self._input]
        self._old = self._input
        self._input = []

    # 入力
    def add(self, text:str) -> 'UI_INPUT':
        self._input.append(text)
        return self

    # 取得
    @property
    def trg(self) -> list[str]:
        return self._trg  # 新規追加された入力を取得

    @property
    def release(self) -> list[str]:
        return self._release  # 解除された入力を取得

    @property
    def pressed(self) -> list[str]:
        return self._old  # 現在押されているか


# UIパーツの状態管理ラッパー
class UI_STATE:
    xmlui: 'XMLUI'  # ライブラリへのIF
    _element: Element  # 自身のElement

    def __init__(self, xmlui:'XMLUI', element: Element):
        # プロパティの初期化
        self.xmlui = xmlui
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

    def setAttr(self, key:str|list[str], value: Any) -> 'UI_STATE':
        # attribはdict[str,str]なのでstrで保存する
        if isinstance(key, list):
            for i, k in enumerate(key):
                self._element.attrib[k] = str(value[i])
        else:
            self._element.attrib[key] = str(value)
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
    def addChild(self, child:'UI_STATE'):
        self._element.append(child._element)

    def remove(self):
        parent = self.parent
        if parent is not None:
            parent._element.remove(self._element)

    def findByID(self, id:str) -> 'UI_STATE':
        for element in self._element.iter():
            if element.attrib.get("id") == id:
                return UI_STATE(self.xmlui, element)
        raise Exception(f"ID '{id}' not found in '{self.tag}' and children")

    def findByTagAll(self, tag:str) -> list['UI_STATE']:
        return [UI_STATE(self.xmlui, element) for element in self._element.iter() if element.tag == tag]

    def findByTag(self, tag:str) -> 'UI_STATE':
        elements = self.findByTagAll(tag)
        if elements:
            return elements[0]
        raise Exception(f"Tag '{tag}' not found in '{self.tag}' and children")

    def findByTagR(self, tag:str) -> 'UI_STATE':
        parent = self.parent
        while(parent is not None):
            if parent.tag == tag:
                return parent
            parent = parent.parent
        raise Exception(f"Tag '{tag}' not found in parents")

    # 子の2D配列を返す
    def arrayByTag(self, tag_outside:str, tag_inside:str) -> list[list['UI_STATE']]:
        outsides = self.findByTagAll(tag_outside)
        return [outside.findByTagAll(tag_inside) for outside in outsides]

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
        parent = _rec_parentSearch(self.xmlui.root._element, self._element)
        return UI_STATE(self.xmlui, parent) if parent is not None else None


    # イベント管理用
    # *************************************************************************
    @property
    def input(self) -> UI_INPUT:
        return self.xmlui._input


    # デバッグ用
    # *************************************************************************
    def strTree(self, indent:str="  ", pre:str="") -> str:
        out = pre + self.tag
        out += ": " + self.attrStr("id") if "id" in self._element.attrib else ""
        for element in self._element:
            out += "\n" + UI_STATE(self.xmlui, element).strTree(indent, pre+indent)
        return out


# XMLでUIライブラリ本体
# #############################################################################
class XMLUI:
    root: UI_STATE
    _event_map: dict[Element, set[str]]  # イベント通知用

    _input: UI_INPUT

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

        # 入力
        self._input = UI_INPUT()

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
    def addChild(self, child:'UI_STATE'):
        self.root.addChild(child)

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
        # 存在しなければ作っておく
        if src not in self._event_map:
            self._event_map[element] = set([])
        self._event_map[element].add(event)


    # 更新用
    # *************************************************************************
    def update(self):
        # 入力の更新
        self._input.update()

        # 更新対象Elementを取得
        update_states = [UI_STATE(self, element) for element in self.root._element.iter() if element.attrib.get("enable", True)]

        # 更新処理
        for states in update_states:
            self.updateElement(states.tag, states, self._event_map.get(states._element, set([])))

        # 状態のリセット
        self._event_map.clear()

    # 描画用
    # *************************************************************************
    def draw(self):
        # 更新対象Elementを取得
        draw_states = [UI_STATE(self, element) for element in self.root._element.iter() if element.attrib.get("enable", True) and element.attrib.get("visible", True)]

        # エリア更新
        for state in draw_states:
            if state.parent is not None:  # rootは親を持たないので更新不要
                if state.hasAttr("abs_x"):
                    state.setAttr("area_x", state.attrInt("abs_x"))  # 絶対座標
                else:
                    state.setAttr("area_x", state.attrInt("x") + state.parent.attrInt("area_x"))  # オフセット
                if state.hasAttr("abs_y"):
                    state.setAttr("area_y", state.attrInt("abs_y"))  # 絶対座標
                else:
                    state.setAttr("area_y", state.attrInt("y") + state.parent.attrInt("area_y"))  # オフセット
                state.setAttr("area_w", state.attrInt("w", state.parent.attrInt("area_w")))
                state.setAttr("area_h", state.attrInt("h", state.parent.attrInt("area_h")))

        # 描画処理
        for state in draw_states:
            self.drawElement(state.tag, state)

    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def updateElement(self, name:str, state:UI_STATE, events:set[str]):
        # 登録済みの関数だけ実行
        if name in self._update_funcs:
            self._update_funcs[name](state, events)

    def drawElement(self, name:str, state:UI_STATE):
        # 登録済みの関数だけ実行
        if name in self._draw_funcs:
            self._draw_funcs[name](state)

