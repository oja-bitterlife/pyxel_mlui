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
    def __init__(self, text:str, params:dict[str,Any]={}, sep_exp:str=r"\n|\\n"):
        self.src = re.sub(sep_exp, "\n", text.format(**params))  # 改行コードで統一

    # 最大文字数に減らして取得
    def getTokens(self, limit:int=65535, wrap:int=1024) -> list[str]:
        tokens:list[str] = []
        for line in self.src[:int(limit)].splitlines():  # 行分割
            tokens += [line[i:i+wrap] for i in range(0, len(line), wrap)]  # wrap分割
        return tokens

    @property
    def length(self) -> int:
        return len(self.src.replace("\n", ""))  # 改行を外してカウント


class UI_EVENT:
    # 入力状態の保存
    _receive:set[str]  # 次の状態受付
    _input:set[str]
    _trg:set[str]
    _release:set[str]

    def __init__(self):
        self._input = set([])
        self._trg = set([])
        self._release = set([])
        self._receive = set([])

    # 更新
    def update(self):
        # 状態更新
        self._trg = set([i for i in self._receive if i not in self._input])
        self._relase = set([i for i in self._input if i not in self._receive])
        self._input = self._receive

        # 取得し直す
        self._receive = set([])

    # 入力
    def on(self, text:str) -> 'UI_EVENT':
        self._receive.add(text)
        return self

    # 取得
    @property
    def input(self) -> set[str]:
        return self._input  # 現在押されているか

    @property
    def trg(self) -> set[str]:
        return self._trg  # 新規追加された入力を取得

    @property
    def release(self) -> set[str]:
        return self._release  # 解除された入力を取得



# UIパーツの状態管理ラッパー
class UI_STATE:
    xmlui: 'XMLUI'  # ライブラリへのIF
    _element: Element  # 自身のElement

    def __init__(self, xmlui:'XMLUI', element:Element):
        # プロパティの初期化
        self.xmlui = xmlui
        self._element = element

    def useEvent(self, use_event:bool=True) -> 'UI_STATE':
        return self.setAttr("use_event", True)

    # UI_STATEは都度使い捨てなので、対象となるElementで比較する
    def __eq__(self, other) -> bool:
        return other._element == self._element if isinstance(other, UI_STATE) else False

    # attribアクセス用
    # *************************************************************************
    def attrInt(self, key:str, default:int=0) -> int:
        return int(self._element.attrib.get(key, default))

    def attrStr(self, key:str, default:str="") -> str:
        return self._element.attrib.get(key, default)

    def attrBool(self, key:str, default:bool=False) -> bool:
        attr = self._element.attrib.get(key)
        return default if attr is None else (True if attr.lower() in ["true", "ok", "yes", "on"] else False)

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
    def tag(self) -> str:
        return self._element.tag

    @property
    def area(self) -> UI_RECT:
        return UI_RECT(self.area_x, self.area_y, self.area_w, self.area_h)


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


    # デバッグ用
    # *************************************************************************
    def strTree(self, indent:str="  ", pre:str="") -> str:
        out = pre + self.tag
        out += ": " + self.id if self.id else ""
        for element in self._element:
            out += "\n" + UI_STATE(self.xmlui, element).strTree(indent, pre+indent)
        return out


    # xmluiで特別な意味を持つアトリビュート一覧
    # わかりやすく全てプロパティを用意しておく(デフォルト値も書く)
    # 面倒でも頑張って書く
    # *************************************************************************
    @property
    def id(self) -> str:  # ID。xmlではかぶらないように(精神論)
        return self.attrStr("id", "")

    @property
    def enable(self) -> bool:  # 有効フラグ
        return self.attrBool("enable", True)
    @property
    def visible(self) -> bool:  # 表示フラグ
        return self.attrBool("visible", True)

    @property
    def x(self) -> int:  # 親からの相対座標x
        return self.attrInt("x", 0)
    @property
    def y(self) -> int:  # 親からの相対座標y
        return self.attrInt("y", 0)
    @property
    def abs_x(self) -> int:  # 絶対座標x
        return self.attrInt("abs_x", 0)
    @property
    def abs_y(self) -> int:  # 絶対座標y
        return self.attrInt("abs_y", 0)
    @property
    def w(self) -> int:  # elementの幅
        return self.attrInt("w", 4096)
    @property
    def h(self) -> int:  # elementの高さ
        return self.attrInt("h", 4096)

    @property
    def area_x(self) -> int:  # 表示最終座標x
        return self.attrInt("area_x", 0)
    @property
    def area_y(self) -> int:  # 表示最終座標y
        return self.attrInt("area_y", 0)
    @property
    def area_w(self) -> int:  #  表示最終幅
        return self.attrInt("area_w", 4096)
    @property
    def area_h(self) -> int:  #  表示最終高さ
        return self.attrInt("area_h", 4096)

    @property
    def use_event(self) -> bool:  # eventを使うかどうか
        return self.attrBool("use_event", False)

    @property
    def wrap(self) -> int:  # テキスト自動改行文字数
        return self.attrInt("wrap", 1024)


# XMLでUIライブラリ本体
# #############################################################################
class XMLUI:
    root: UI_STATE

    # 入力処理
    event: UI_EVENT

    # 処理関数の登録
    _update_funcs: dict[str, Callable[[UI_STATE,UI_EVENT], None]]
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
        # 入力
        self.event = UI_EVENT()

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
    def setUpdateFunc(self, name:str, func:Callable[[UI_STATE,UI_EVENT], None]):
        self._update_funcs[name] = func

    def setDrawFunc(self, name:str, func:Callable[[UI_STATE], None]):
        self._draw_funcs[name] = func


    # 更新用
    # *************************************************************************
    def update(self):
        # (入力)イベントの更新
        self.event.update()

        # 更新対象Elementを取得
        update_states = [UI_STATE(self, element) for element in self.root._element.iter() if element.attrib.get("enable", True)]

        # use_eventがTrueなstateだけ抜き出す
        use_event_states = list(filter(lambda state: state.use_event, update_states))
        active_state = use_event_states[-1] if use_event_states else None  # 最後=Active

        # 更新処理
        for state in update_states:
            self.updateElement(state.tag, state, self.event if state == active_state else UI_EVENT())


    # 描画用
    # *************************************************************************
    def draw(self):
        # 更新対象Elementを取得
        draw_states = [UI_STATE(self, element) for element in self.root._element.iter() if element.attrib.get("enable", True) and element.attrib.get("visible", True)]

        # エリア更新
        for state in draw_states:
            if state.parent is not None:  # rootは親を持たないので更新不要
                if state.hasAttr("abs_x"):
                    state.setAttr("area_x", state.abs_x)  # 絶対座標
                else:
                    state.setAttr("area_x", state.x + state.parent.area_x)  # オフセット
                if state.hasAttr("abs_y"):
                    state.setAttr("area_y", state.abs_y)  # 絶対座標
                else:
                    state.setAttr("area_y", state.y + state.parent.area_y)  # オフセット
                state.setAttr("area_w", state.attrInt("w", state.parent.area_w))
                state.setAttr("area_h", state.attrInt("h", state.parent.area_h))

        # 描画処理
        for state in draw_states:
            self.drawElement(state.tag, state)

    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def updateElement(self, name:str, state:UI_STATE, active_event:UI_EVENT):
        # 登録済みの関数だけ実行
        if name in self._update_funcs:
            self._update_funcs[name](state, active_event)

    def drawElement(self, name:str, state:UI_STATE):
        # 登録済みの関数だけ実行
        if name in self._draw_funcs:
            self._draw_funcs[name](state)

