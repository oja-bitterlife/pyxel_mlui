import xml.etree.ElementTree
from xml.etree.ElementTree import Element
from typing import Callable,Any

import re, math, copy
import unicodedata

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


# 半角を全角に変換
_from_hanakaku = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_to_zenkaku = "０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
_from_hanakaku += " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"  # 半角記号を追加
_to_zenkaku += "　！＂＃＄％＆＇（）＊＋，－．／：；＜＝＞？＠［￥］＾＿｀｛｜｝～"  # 全角記号を追加

_hankaku_zenkaku_dict = str.maketrans(_from_hanakaku, _to_zenkaku)
def convertHZ(hankaku:str):
    return unicodedata.normalize("NFKC", hankaku).translate(_hankaku_zenkaku_dict)

# アニメーションテキスト表示用
class UI_ANIM_TEXT:
    # クラス定数
    SEPARATE_REGEXP:str = r"\\n"

    _state: 'UI_STATE'
    _draw_count_attr: str  # 描画文字数
    _display_text: str  # 最終テキスト

    # 改行コードに変換しておく
    def __init__(self, state:'UI_STATE', draw_count_attr:str):
        self._state = state
        self._draw_count_attr = draw_count_attr
        self._display_text = re.sub(self.SEPARATE_REGEXP, "\n", self._state.text).strip()

    def bind(self, params:dict[str, Any]={}, wrap:int=4096) -> 'UI_ANIM_TEXT':
        wrap = max(1, wrap)  # 0だと無限になってしまうので最低1を入れておく
        tmp_text = convertHZ(re.sub(self.SEPARATE_REGEXP, "\n", self._state.text).strip().format(**params))
        # 各行に分解し、その行をさらにwrapで分解する
        self._display_text = "\n".join(["\n".join([line[i:i+wrap].strip("\n") for i in range(0, len(line), wrap)]) for line in tmp_text.splitlines()])
        return self

    # draw_countの操作
    def setDrawCount(self, draw_count:float) -> 'UI_ANIM_TEXT':
        self._state.setAttr(self._draw_count_attr, draw_count)
        return self

    def next(self, add:float=1) -> 'UI_ANIM_TEXT':
        return self.setDrawCount(self.draw_count+add)

    def reset(self) -> 'UI_ANIM_TEXT':
        return self.setDrawCount(0)

    def finish(self) -> 'UI_ANIM_TEXT':
        return self.setDrawCount(len(self._display_text))

    @property
    def draw_count(self) -> float:
        return self._state.attrFloat(self._draw_count_attr)

    # 分割
    def split(self) -> list[str]:
        return self._limitStr(self.text, self.draw_count).splitlines()

    # draw_countまでの文字列を改行分割
    @classmethod
    def _limitStr(cls, tmp_text, draw_count:float) -> str:
        limit = math.ceil(draw_count)
        # まずlimitまで縮める
        for i,c in enumerate(tmp_text):
            if (limit := limit if c == "\n" else limit-1) < 0:
                tmp_text = tmp_text[:i]
                break
        return tmp_text.strip("\n")

    # テキストアクセスプロパティ
    @property
    def text(self) -> str:
        return self._display_text

    @property
    def length(self) -> int:
        return len(self._display_text.replace("\n", ""))

    @property
    def is_finish(self) -> int:
        return math.ceil(self.draw_count) >= self.length

    def usePage(self, page_no_attr:str,  page_line_num:int) -> 'UI_ANIM_PAGE':
        return UI_ANIM_PAGE(self, page_no_attr, page_line_num)

# Page関係
class UI_ANIM_PAGE:
    _text: UI_ANIM_TEXT  # 作成元
    _page_line_num: int  # ページ行数
    _page_no_attr: str  # ページ番号

    def __init__(self, text:UI_ANIM_TEXT, page_no_attr:str,  page_line_num:int):
        self._text = text
        self._page_no_attr = page_no_attr
        self._page_line_num = page_line_num

    # page_noの操作
    def setPageNo(self, page_no:int) -> 'UI_ANIM_PAGE':
        self._text._state.setAttr(self._page_no_attr, page_no)
        return self

    def nextPage(self, add:int=1) -> 'UI_ANIM_PAGE':
        self._text.reset()  # draw_countをリセットしておく
        return self.setPageNo(self.page_no+add)

    # 分割
    def split(self) -> list[str]:
        return self._text._limitStr(self.text, self._text.draw_count).splitlines()

    def splitPage(self) -> list[list[str]]:
        lines = self._text._display_text.splitlines()
        return [lines[i:i+self._page_line_num] for i in range(0, len(lines), self._page_line_num)]

    # textと同じIF
    @property
    def draw_count(self) -> float:
        return self._text.draw_count

    @property
    def text(self) -> str:
        page_no = self._text._state.attrInt(self._page_no_attr, 0)
        return "\n".join(self.splitPage()[page_no])

    @property
    def length(self) -> int:
        return len(self.text.replace("\n", ""))

    @property
    def is_finish(self) -> int:
        return math.ceil(self._text.draw_count) >= self.length

    # ページ専用プロパティ
    @property
    def page_no(self) -> int:
        return self._text._state.attrInt(self._page_no_attr, 0)

    @property
    def page_max(self) -> int:
        return len(self.splitPage())

    @property
    def is_end_page(self) -> bool:
        return self.page_no+1 >= self.page_max


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
    _grid: list[list['UI_STATE']]  # グリッド保存

    def __init__(self, state:'UI_STATE', grid:list[list['UI_STATE']]):
        self._state = state
        self._grid = grid

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
    def grid_w(self) -> int:
        return len(self._grid[0])
    @property
    def grid_h(self) -> int:
        return len(self._grid)

    @property
    def cur_x(self) -> int:
        return self._state.cur_x
    @property
    def cur_y(self) -> int:
        return self._state.cur_y

    @property
    def state(self) -> 'UI_STATE':
        return self._state

    @property
    def selected(self) -> 'UI_STATE':
        return self._grid[self.cur_y][self.cur_x]

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

    def attrFloat(self, key:str, default:float=0) -> float:
        return float(self._element.attrib.get(key, default))

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

    # textアクセス用
    # *************************************************************************
    @property
    def text(self) -> str:
        return self._element.text.strip() if self._element.text else ""

    def getAnimText(self, draw_count_attr:str, params={}) -> UI_ANIM_TEXT:
        return UI_ANIM_TEXT(self, draw_count_attr)

    # その他
    # *************************************************************************
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

    def arrangeByTag(self, tag_outside:str, tag_inside:str, w:int, h:int) -> list[list['UI_STATE']]:
        grid = self.arrayByTag(tag_outside, tag_inside)
        for y,cols in enumerate(grid):
            for x,rows in enumerate(cols):
                rows.setAttr(["x", "y"], (x*w, y*h))
        return grid

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
                # absがあれば絶対座標、なければ親からのオフセット
                state.setAttr("area_x", state.abs_x if state.hasAttr("abs_x") else state.x + state.parent.area_x)
                state.setAttr("area_y", state.abs_y if state.hasAttr("abs_y") else state.y + state.parent.area_y)
                state.setAttr("area_w", state.attrInt("w", state.parent.area_w))
                state.setAttr("area_h", state.attrInt("h", state.parent.area_h))

        # 描画処理
        for state in draw_states:
            self.drawElement(state.tag, state)

    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def updateElement(self, tag_name:str, state:UI_STATE, event:UI_EVENT):
        # デバッグ用
        state.setAttr("frame_color", 10 if event.active else 7)

        # 登録済みの関数だけ実行
        if tag_name in self._update_funcs:
            self._update_funcs[tag_name](state, event)

    def drawElement(self, tag_name:str, state:UI_STATE):
        # 登録済みの関数だけ実行
        if tag_name in self._draw_funcs:
            self._draw_funcs[tag_name](state)


    # 処理登録
    # *************************************************************************
    def setUpdateFunc(self, tag_name:str, func:Callable[[UI_STATE,UI_EVENT], None]):
        self._update_funcs[tag_name] = func

    def setDrawFunc(self, tag_name:str, func:Callable[[UI_STATE], None]):
        self._draw_funcs[tag_name] = func

    # デコレータを用意
    def tag_update(self, tag_name:str):
        def wrapper(update_func:Callable[[UI_STATE,UI_EVENT], None]):
            self.setUpdateFunc(tag_name, update_func)
        return wrapper

    def tag_draw(self, tag_name:str):
        def wrapper(draw_func:Callable[[UI_STATE], None]):
            self.setDrawFunc(tag_name, draw_func)
        return wrapper
