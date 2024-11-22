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


# アニメーションテキスト表示用
class UI_PAGE_TEXT:
    # クラス定数
    SEPARATE_REGEXP:str = r"\\n"

    _state: 'UI_STATE'
    _page_line_num: int

    # 状態保存先
    _draw_count_attr: str  # 描画文字数
    _page_no_attr: str  # ページ番号

    # 最終テキスト
    _display_text: str

    # 改行コードに変換しておく
    def __init__(self, state:'UI_STATE', draw_count_attr:str):
        self._state = state
        self._draw_count_attr = draw_count_attr
        self._display_text = self._state.text.strip()

    def bind(self, params:dict[str, Any]={}, wrap:int=4096) -> 'UI_PAGE_TEXT':
        wrap = max(1, wrap)  # 0だと無限になってしまうので最低1を入れておく
        tmp_text = self._state.text.strip().format(**params)
        self._display_text = "\n".join([tmp_text[i:i+wrap].strip("\n") for i in range(0, len(tmp_text), wrap)])
        return self

    # draw_countの操作
    def setDrawCount(self, draw_count:int) -> 'UI_PAGE_TEXT':
        self._state.setAttr(self._draw_count_attr, draw_count)
        return self

    def next(self, add:int=1) -> 'UI_PAGE_TEXT':
        return self.setDrawCount(self.draw_count+add)

    def reset(self) -> 'UI_PAGE_TEXT':
        return self.setDrawCount(0)

    def finish(self) -> 'UI_PAGE_TEXT':
        return self.setDrawCount(len(self._display_text))

    # draw_countまでの文字列を改行分割
    @classmethod
    def _limitStr(cls, tmp_text, draw_count:int) -> str:
        # まずlimitまで縮める
        for i,c in enumerate(tmp_text):
            if c != "\n":
                draw_count -= 1
                if draw_count <= 0:
                    tmp_text = tmp_text[:i]
                    break
        return tmp_text.strip("\n")

    def split(self) -> list[str]:
        return self._limitStr(self.text, self.draw_count).splitlines()

    @property
    def text(self) -> str:
        return self._display_text

    @property
    def draw_count(self) -> int:
        return self._state.attrInt(self._draw_count_attr)

    @property
    def length(self) -> int:
        return len(self._display_text.replace("\n", ""))

    @property
    def is_finish(self) -> int:
        return self.draw_count >= self.length

    # Page関係
    # *************************************************************************
    def usePage(self, page_no_attr:str,  page_line_num:int) -> 'UI_PAGE_TEXT':
        self._page_no_attr = page_no_attr
        self._page_line_num = page_line_num
        return self

    # page_noの操作
    def setPageNo(self, page_no:int) -> 'UI_PAGE_TEXT':
        self._state.setAttr(self._page_no_attr, page_no)
        return self

    def nextPage(self, add:int=1) -> 'UI_PAGE_TEXT':
        self.reset()  # draw_countをリセットしておく
        return self.setPageNo(self.page_no+add)

    def splitPage(self) -> list[str]:
        return self._limitStr(self.page_text, self.draw_count).splitlines()

    @property
    def page_text(self) -> str:
        page_no = self._state.attrInt(self._page_no_attr, 0)
        return "\n".join(self._display_text.splitlines()[page_no*self._page_line_num:(page_no+1)*self._page_line_num])

    @property
    def page_length(self) -> int:
        return len(self.page_text.replace("\n", ""))

    @property
    def is_page_finish(self) -> int:
        return self.draw_count >= self.page_length

    # ページ情報取得
    @property
    def page_no(self) -> int:
        return self._state.attrInt(self._page_no_attr, 0)

    @property
    def page_max(self) -> int:
        line_num = len(self._display_text.splitlines())
        return (line_num+self._page_line_num-1)//self._page_line_num

    @property
    def is_pages_end(self) -> bool:
        return self.page_no >= self.page_max


class UI_EVENT:
    active:bool  # 現在アクティブかどうか

    # 入力状態の保存
    _receive:set[str]  # 次の状態受付
    _input:set[str]
    _trg:set[str]
    _release:set[str]

    def __init__(self, init_active=False):
        self.active = init_active
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


class UI_CURSOR:
    _state: 'UI_STATE'
    grid_w: int
    grid_h: int

    def __init__(self, state:'UI_STATE', grid_w:int, grid_h:int):
        self._state = state
        self.grid_w = grid_w
        self.grid_h = grid_h

    # 範囲限定付き座標設定
    def setCurPos(self, x:int, y:int, wrap:bool=False) -> 'UI_CURSOR':
        self._state.setAttr("cur_x", (x + self.grid_w) % self.grid_w if wrap else max(min(x, self.grid_w-1), 0))
        self._state.setAttr("cur_y", (y + self.grid_h) % self.grid_h if wrap else max(min(y, self.grid_h-1), 0))
        return self

    def moveLeft(self, wrap:bool=False) -> 'UI_CURSOR':
        return self.setCurPos(self._state.cur_x-1, self._state.cur_y, wrap)
    def moveRight(self, wrap:bool=False) -> 'UI_CURSOR':
        return self.setCurPos(self._state.cur_x+1, self._state.cur_y, wrap)
    def moveUp(self, wrap:bool=False) -> 'UI_CURSOR':
        return self.setCurPos(self._state.cur_x, self._state.cur_y-1, wrap)
    def moveDown(self, wrap:bool=False) -> 'UI_CURSOR':
        return self.setCurPos(self._state.cur_x, self._state.cur_y+1, wrap)

    def moveByEvent(self, input:set[str], leftEvent:str, rightEvent:str, upEvent:str, downEvent:str, x_wrap:bool=False, y_wrap:bool=False) -> 'UI_CURSOR':
        if leftEvent in input:
            self.moveLeft(x_wrap)
        if rightEvent in input:
            self.moveRight(x_wrap)
        if upEvent in input:
            self.moveUp(y_wrap)
        if downEvent in input:
            self.moveDown(y_wrap)
        return self

    @property
    def cur_x(self) -> int:
        return self._state.cur_x
    @property
    def cur_y(self) -> int:
        return self._state.cur_y

    @property
    def state(self) -> 'UI_STATE':
        return self._state

    def __repr__(self) -> str:
        return f"UI_CURSOR({self._state.x}, {self._state.y}, {self.grid_w}, {self.grid_h})"


# UIパーツの状態管理ラッパー
class UI_STATE:
    xmlui: 'XMLUI'  # ライブラリへのIF
    _element: Element  # 自身のElement

    def __init__(self, xmlui:'XMLUI', element:Element):
        # プロパティの初期化
        self.xmlui = xmlui
        self._element = element

    def disableEvent(self) -> 'UI_STATE':
        return self.setAttr("use_event", False)

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
    def text(self) -> str:
        return self._element.text.strip() if self._element.text else ""

    @property
    def area(self) -> UI_RECT:
        return UI_RECT(self.area_x, self.area_y, self.area_w, self.area_h)


    # ツリー操作用
    # *************************************************************************
    def addChild(self, child:'UI_STATE'):
        self._element.append(child._element)

    def remove(self):
        parent = self.parent
        if parent:
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
        while(parent):
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
                if result:
                    return result
            return None
        parent = _rec_parentSearch(self.xmlui.root._element, self._element)
        return UI_STATE(self.xmlui, parent) if parent else None

    # 子に別Element一式を追加する
    def open(self, template:'XMLUI|UI_STATE', id:str) -> 'UI_STATE':
        src = template.root if isinstance(template, XMLUI) else template
        try:
            return self.findByID(id)  # すでにいたらなにもしない
        except:
            # eventを有効にして追加する
            opend  = self.xmlui.duplicate(src.findByID(id))
            self.addChild(opend.setAttr("use_event", True))
            return opend

    def close(self, id:str):
        try:
            state = self.xmlui.root.findByID(id)
            state.remove()
        finally:
            return None

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

    @property
    def cur_x(self) -> int:  # 選択グリッドx
        return self.attrInt("cur_x", 0)
    @property
    def cur_y(self) -> int:  # 選択グリッドy
        return self.attrInt("cur_y", 0)


# XMLでUIライブラリ本体
# #############################################################################
class XMLUI:
    root: UI_STATE

    # 入力処理
    event: UI_EVENT

    # 処理関数の登録
    _update_funcs: dict[str, Callable[[UI_STATE,UI_EVENT], None]]
    _draw_funcs: dict[str, Callable[[UI_STATE], None]]

    # 更新管理(drawはupdateされたElementのみ対象に)
    _update_states_cache: list[UI_STATE]  # 更新対象のキャッシュ

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
        self.event = UI_EVENT(True)  # 唯一のactiveとする

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
        self.root.setAttr("use_event", True)  # rootはデフォルトではイベントをとるように

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
        self._update_states_cache = [UI_STATE(self, element) for element in self.root._element.iter() if element.attrib.get("enable", True)]

        # use_eventがTrueなstateだけ抜き出す
        use_event_states = list(filter(lambda state: state.use_event, self._update_states_cache))
        active_state = use_event_states[-1] if use_event_states else None  # 最後=Active

        # 更新処理
        for state in self._update_states_cache:
            self.updateElement(state.tag, state, self.event if state == active_state else UI_EVENT())


    # 描画用
    # *************************************************************************
    def draw(self):
        # 更新対象を取得(Updateされたもののみ対象)
        draw_states = [state for state in self._update_states_cache if state.visible]

        # エリア更新
        for state in draw_states:
            if state.parent:  # rootは親を持たないので更新不要
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
    def updateElement(self, name:str, state:UI_STATE, event:UI_EVENT):
        # デバッグ用
        state.setAttr("frame_color", 10 if event.active else 7)

        # 登録済みの関数だけ実行
        if name in self._update_funcs:
            self._update_funcs[name](state, event)

    def drawElement(self, name:str, state:UI_STATE):
        # 登録済みの関数だけ実行
        if name in self._draw_funcs:
            self._draw_funcs[name](state)

