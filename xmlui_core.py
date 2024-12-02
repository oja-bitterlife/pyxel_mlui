# XMLを使うよ
import xml.etree.ElementTree
from xml.etree.ElementTree import Element

# 日本語対応
import unicodedata

# その他よく使う奴
import re
import math
import copy
from typing import Generator,Callable,Any,Self  # 型を使うよ
import weakref


# 描画領域計算用
# #############################################################################
class XURect:
    def __init__(self, x:int, y:int, w:int, h:int):
        self.x = x
        self.y = y
        self.w = max(0, w)
        self.h = max(0, h)

    def intersect(self, other:"XURect") -> "XURect":
        right = min(self.x+self.w, other.x+other.w)
        left = max(self.x, other.x)
        bottom = min(self.y+self.h, other.y+other.h)
        top = max(self.y, other.y)
        return XURect(left, top, right-left, bottom-top)

    def inflate(self, size) -> "XURect":
        return XURect(self.x-size, self.y-size, self.w+size*2, self.h+size*2)

    def contains(self, x, y) -> bool:
        return self.x <= x < self.x+self.w and self.y <= y < self.y+self.h

    def center_x(self, w:int=0) -> int:
        return self.x + (self.w-w)//2

    def center_y(self, h:int=0) -> int:
        return self.y + (self.h-h)//2

    def right(self, w:int=0) -> int:
        return self.x + self.w - w

    def bottom(self, h:int=0) -> int:
        return self.y + self.h - h

    @property
    def cx(self) -> int:
        return self.center_x()

    @property
    def cy(self) -> int:
        return self.center_y()

    @property
    def is_empty(self) -> int:
        return self.w <= 0 or self.h <= 0

    def __repr__(self) -> str:
        return f"RECT({self.x}, {self.y}, {self.w}, {self.h})"


# イベント管理用
class XUEvent:
    def __init__(self, init_active=False):
        self.active = init_active  # アクティブなイベントかどうか
        self.on_init = False
        self.clear()

    def clear(self):
        self._receive:set[str] = set([])  # 次の状態受付
        self._input:set[str] = set([])
        self._trg:set[str] = set([])
        self._release:set[str] = set([])

    def clearTrg(self):
        self._trg:set[str] = set([])
        self._release:set[str] = set([])

    # 更新
    def update(self):
        # 状態更新
        self._trg = set([i for i in self._receive if i not in self._input])
        self._relase = set([i for i in self._input if i not in self._receive])
        self._input = self._receive

        # 取得し直す
        self._receive = set([])

    # 入力
    def on(self, text:str) -> Self:
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


# UIパーツの状態取得
# #############################################################################
# XMLの状態管理ReadOnly
class XUStateRO:
    def __init__(self, xmlui:'XMLUI', element:Element):
        self.xmlui = xmlui  # ライブラリへのIF
        self._element = element  # 自身のElement

    def __eq__(self, other) -> bool:
        # UI_Stateは都度使い捨てなので、対象となるElementで比較する
        if isinstance(other, XUStateRO):
            return other._element is self._element
        # 文字列との比較はvalueとで行う(イベント用)
        elif isinstance(other, str):
            return self.value == other
        else:
            return False

    # attribアクセス用
    # *************************************************************************
    def attr_int(self, key:str, default:int=0) -> int:
        return int(self._element.attrib.get(key, default))

    def attr_float(self, key:str, default:float=0) -> float:
        return float(self._element.attrib.get(key, default))

    def attr_str(self, key:str, default:str="") -> str:
        return self._element.attrib.get(key, default)

    def attr_bool(self, key:str, default:bool=False) -> bool:
        attr = self._element.attrib.get(key)
        return default if attr is None else (True if attr.lower() in ["true", "ok", "yes", "on"] else False)

    def has_attr(self, key: str) -> bool:
        return key in self._element.attrib

    # textアクセス用
    # *************************************************************************
    @property
    def text(self) -> str:
        return self._element.text.strip() if self._element.text else ""

    # その他
     # *************************************************************************
    @property
    def area(self) -> XURect:  # 親からの相対座標
        # areaは良く呼ばれるので、一回でもparent探しのdictアクセスを軽減する
        parent = self.parent
        parent_area = parent.area if parent else XURect(0, 0, 4096, 4096)

        # x,yはアトリビュートなのでローカルにしておく
        offset_x = self.x
        offset_y = self.y

        # absがあれば絶対座標、なければ親からのオフセット
        return XURect(
            self.abs_x if self.has_attr("abs_x") else offset_x + parent_area.x,
            self.abs_y if self.has_attr("abs_y") else offset_y + parent_area.y,
            self.attr_int("w", parent_area.w-offset_x),
            self.attr_int("h", parent_area.h-offset_y)
        )

    @property
    def tag(self) -> str:
        return self._element.tag

    def asRW(self) -> 'XUState':
        return XUState(self.xmlui, self._element)

    # ツリー操作用
    # *************************************************************************
    def find_by_ID(self, id:str) -> 'XUStateRO':
        for element in self._element.iter():
            if element.attrib.get("id") == id:
                return XUState(self.xmlui, element)
        raise Exception(f"ID '{id}' not found in '{self.tag}' and children")

    def find_by_tagall(self, tag:str) -> list['XUStateRO']:
        return [XUState(self.xmlui, element) for element in self._element.iter() if element.tag == tag]

    def find_by_tag(self, tag:str) -> 'XUStateRO':
        elements:list[XUStateRO] = self.find_by_tagall(tag)
        if elements:
            return elements[0]
        raise Exception(f"Tag '{tag}' not found in '{self.tag}' and children")

    # ツリーを遡って親を探す
    def find_parent(self, id:str) -> 'XUStateRO':
        parent = self.parent
        while parent:
            if parent.id == id:
                return parent
            parent = parent.parent
        raise Exception(f"Parent '{id}' not found in '{self.tag}' and parents")

    @property
    def parent(self) -> 'XUStateRO|None':
        return self.xmlui._parent_cache.get(self._element, None)

    # すでにidツリーに存在するか
    def is_open(self, id:str) -> bool:
        try:
            self.find_by_ID(id)
            return True
        except:
            return False
 
    # デバッグ用
    # *************************************************************************
    def strtree(self, indent:str="  ", pre:str="") -> str:
        out = pre + self.tag
        out += f": {self.id}" if self.id else ""
        out += f" {self.marker}"
        for element in self._element:
            out += "\n" + XUState(self.xmlui, element).strtree(indent, pre+indent)
        return out

    # xmluiで特別な意味を持つアトリビュート一覧
    # わかりやすく全てプロパティを用意しておく(デフォルト値も省略せず書く)
    # 面倒でも頑張って書く
    # *************************************************************************
    @property
    def id(self) -> str:  # ID。xmlではかぶらないように(精神論)
        return self.attr_str("id", "")

    @property
    def value(self) -> str:  # 汎用値取得
        return self.attr_str("value", "")

    @property
    def enable(self) -> bool:  # 有効フラグ
        return self.attr_bool("enable", True)
    @property
    def visible(self) -> bool:  # 表示フラグ
        return self.attr_bool("visible", True)

    @property
    def x(self) -> int:  # 親からの相対座標x
        return self.attr_int("x", 0)
    @property
    def y(self) -> int:  # 親からの相対座標y
        return self.attr_int("y", 0)
    @property
    def abs_x(self) -> int:  # 絶対座標x
        return self.attr_int("abs_x", 0)
    @property
    def abs_y(self) -> int:  # 絶対座標y
        return self.attr_int("abs_y", 0)
    @property
    def w(self) -> int:  # elementの幅
        return self.attr_int("w", 4096)
    @property
    def h(self) -> int:  # elementの高さ
        return self.attr_int("h", 4096)

    @property
    def update_count(self) -> int:  # updateが行われた回数
        return self.attr_int("update_count", 0)

    @property
    def speed(self) -> float:  # スピード/秒。アニメーション等で使う
        return self.attr_float("speed", 1.0)

    @property
    def use_event(self) -> bool:  # eventを使うかどうか
        return self.attr_bool("use_event", False)

    @property
    def layer(self) -> int:  # 描画レイヤ
        if self.has_attr("layer") or self.parent is None:
            return self.attr_int("layer", 0)
        else:  # 無ければ親のlayerを持ってくる
            return self.parent.layer

    @property
    def marker(self) -> str:  # デバッグ用
        return self.attr_str("marker", "")

# XMLの状態設定
class XUState(XUStateRO):
    # attribアクセス用
    # *************************************************************************
    def set_attr(self, key:str|list[str], value: Any) -> Self:
        # attribはdict[str,str]なのでstrで保存する
        if isinstance(key, list):
            for i, k in enumerate(key):
                self._element.attrib[k] = str(value[i])
        else:
            self._element.attrib[key] = str(value)
        return self

    # textアクセス用
    # *************************************************************************
    def set_text(self, text:str) -> Self:
        self._element.text = text
        return self

    # その他
    # *************************************************************************
    def set_pos(self, x:int, y:int) -> Self:
        return self.set_attr(["x", "y"], [x, y])

    def set_abspos(self, x:int, y:int) -> Self:
        return self.set_attr(["abs_x", "abs_y"], [x, y])

    def set_enable(self, enable:bool) -> Self:
        return self.set_attr("enable", enable)

    def set_visible(self, visible:bool) -> Self:
        return self.set_attr("visible", visible)

    # ツリー操作用
    # *************************************************************************
    def add_child(self, child:XUStateRO):
        self._element.append(child._element)
        self.xmlui._update_cache()

    def clear_children(self):
        self._element.clear()

    def remove(self):  # removeの後なにかすることはないのでNone
        # 処理対象から外れるように
        self.set_attr("enable", False)
        if self.parent:  # 親から外す
            self.parent._element.remove(self._element)

    # 子に別Element一式を追加する
    def open(self, template_name:str, id:str, id_alias:str|None=None) -> "XUState":
        # open/closeが連続しないようTrg入力を落とす
        self.xmlui.event.clearTrg()

        # idがかぶらないよう別名を付けられる
        id_alias = id if id_alias is None else id_alias

        # IDがかぶってはいけない
        if self.xmlui.is_open(id_alias):
            raise Exception(f"ID '{id_alias}' already exists")

        opend = self.xmlui._templates[template_name].duplicate(id).set_attr("id", id_alias)
        self.add_child(opend)
        return opend

     # 閉じる
    def close(self, id:str|None=None):  # closeの後なにもしないのでNone
        # open/closeが連続しないようTrg入力を落とす
        self.xmlui.event.clearTrg()

        # idをもつものを遡って閉じる
        def _rec_close(state:XUState, id:str|None=None) -> bool:  # closeの後なにもしないのでNone
            # idが一致している。id指定がない場合はidを持っていれば値は問わない
            if state.id == id or (id is None and state.id):
                state.remove()
                return True

            # 一番上まで検索した
            if state.parent is None or state.parent == state.xmlui:
                return False  # なにもcloseできなかった

            # 親があるなら遡って閉じに行く
            return _rec_close(state.parent.asRW(), id)

        if not _rec_close(self, id):
            self.remove()  # 何もcloseできなかったら自分をclose


# XMLでUIライブラリ本体
# #############################################################################
# テンプレート用
class XMLUI_Template(XUStateRO):
    # 初期化
    # *************************************************************************
    # ファイルから読み込み
    @classmethod
    def _fromfile(cls, xmlui:'XMLUI', fileName:str, root_tag:str|None=None) -> "XMLUI_Template":
        with open(fileName, "r", encoding="utf8") as f:
            return cls._fromstring(xmlui, f.read())

    # リソースから読み込み
    @classmethod
    def _fromstring(cls, xmlui:'XMLUI', xml_data:str) -> "XMLUI_Template":
        return XMLUI_Template(XUState(xmlui, xml.etree.ElementTree.fromstring(xml_data)))

    def __init__(self, root:XUStateRO):
        super().__init__(root.xmlui, root._element)

    # XML操作
    # *************************************************************************
    # Elmentを複製して取り出す
    def duplicate(self, id:str) -> XUState:
        return XUState(self.xmlui, copy.deepcopy(self.find_by_ID(id)._element))

# デバッグ用
class XMLUI_Debug:
    # デバッグ用フラグ
    DEBUG_LEVEL_LIB:int = 100  # ライブラリ作成用
    DEBUG_LEVEL_DEFAULT:int = 0

    def __init__(self, xmlui:"XMLUI"):
        self.xmlui = xmlui
        self.level = self.DEBUG_LEVEL_DEFAULT

    def update(self):
        if "DEBUG_PRINT_TREE" in self.xmlui.event.trg:
            print(self.xmlui.strtree())

    @property
    def is_lib_debug(self) -> bool:
        return self.level >= self.DEBUG_LEVEL_LIB

class XMLUI(XUState):
    # 初期化
    # *************************************************************************
    # 初期化。<xmlui>を持つXMLを突っ込む
    def __init__(self):
        # rootを作って自分自身に設定
        root = Element("root")
        root.attrib["id"] = "root"
        root.attrib["use_event"] = "True"
        super().__init__(self, root)

        # キャッシュ
        self._parent_cache:dict[Element, XUStateRO] = {}

        # デバッグ用
        self.debug = XMLUI_Debug(self)

        # 入力
        self.event = XUEvent(True)  # 唯一のactiveとする
        self._input_lists:dict[str, list[int]] = {}

        # 処理関数の登録
        self._update_funcs:dict[str,Callable[[XUState,XUEvent], None]] = {}
        self._draw_funcs:dict[str,Callable[[XUStateRO], None]] = {}

        # XMLテンプレート置き場
        self._templates:dict[str,XMLUI_Template] = {}

    # template操作
    # *************************************************************************
    def set_template(self, template:XMLUI_Template, template_name:str):
        self._templates[template_name] = template

    def template_fromfile(self, template_filename:str, template_name:str):
        self.set_template(XMLUI_Template._fromfile(self, template_filename), template_name)

    def template_fromstring(self, template_str:str, template_name:str):
        self.set_template(XMLUI_Template._fromstring(self, template_str), template_name)

    # 更新用
    # *************************************************************************
    def update(self):
        # (入力)イベントの更新
        self.event.update()

        # 更新対象を取得
        update_targets = [XUState(self, element) for element in self._element.iter() if bool(element.attrib.get("enable", "True"))]

        # ActiveStateの取得
        event_targets = [state for state in update_targets if state.use_event]
        self.active_state = event_targets[-1] if event_targets else self  # Active=最後

        # 更新処理
        self._update_cache()  # Update実行前にキャッシュの更新

        for state in update_targets:
            if state.enable:  # update中にdisable(remove)になる場合があるので毎回チェック
                # active/inactiveどちらのeventを使うか決定
                event = copy.copy(self.event) if state == self.active_state else XUEvent()

                # やっぱりinitialize情報がどこかに欲しい
                event.on_init = state.update_count == 0

                # 更新処理
                state.set_attr("update_count", state.update_count+1)  # 1スタート(0は初期化時)
                self.update_element(state.tag, state, event)

        self._update_cache()  # 更新処理で変更された可能性があるキャッシュの再更新

        # デバッグ
        if self.debug.is_lib_debug:
            self.debug.update()

    # キャッシュの更新
    def _update_cache(self):
        self._parent_cache = {c:XUStateRO(self, p) for p in self._element.iter() for c in p}

    # 描画用
    # *************************************************************************
    def draw(self):
        # 描画対象を取得。update_countが0の時は未Updateなのではじく
        draw_targets = list(filter(lambda state: state.enable and state.visible and state.update_count>0, [XUState(self, element) for element in self._element.iter()]))

        # 描画処理
        layer_cache = {state._element:state.layer for state in draw_targets}
        for state in sorted(draw_targets, key=lambda state: layer_cache[state._element]):
            self.draw_element(state.tag, state)

    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def update_element(self, tag_name:str, state:XUState, event:XUEvent):
        # 登録済みの関数だけ実行
        if tag_name in self._update_funcs:
            self._update_funcs[tag_name](state, event)

    def draw_element(self, tag_name:str, state:XUStateRO):
        # 登録済みの関数だけ実行
        if tag_name in self._draw_funcs:
            self._draw_funcs[tag_name](state)


    # 処理登録
    # *************************************************************************
    def set_updatefunc(self, tag_name:str, func:Callable[[XUState,XUEvent], None]):
        self._update_funcs[tag_name] = func

    def set_drawfunc(self, tag_name:str, func:Callable[[XUStateRO], None]):
        self._draw_funcs[tag_name] = func

    # デコレータを用意
    def update_bind(self, tag_name:str):
        def wrapper(update_func:Callable[[XUState,XUEvent], None]):
            self.set_updatefunc(tag_name, update_func)
        return wrapper

    def draw_bind(self, tag_name:str):
        def wrapper(draw_func:Callable[[XUStateRO], None]):
            self.set_drawfunc(tag_name, draw_func)
        return wrapper


    # 入力
    # *************************************************************************
    # イベント入力
    def on(self, input:str):
        self.event.on(input)

    # キー入力
    def set_inputlist(self, input_type:str, list:list[int]):
        self._input_lists[input_type] = list

    def _check_input(self, check:str, check_func:Callable[[int], bool]) -> bool:
        for button in self._input_lists[check]:
            if check_func(button):
                return True
        return False

    # 登録キー入力を全部調べて片っ端からイベントに登録
    def check_input_on(self, check_func:Callable[[int], bool]):
        for key in self._input_lists:
            if self._check_input(key, check_func):
                self.event.on(key)

    # イベントでopen
    def open_by_event(self, trg_event:str, template_name:str, id:str, id_alias:str|None=None):
        if trg_event in self.xmlui.event.trg:
            if not self.is_open(id if id_alias is None else id_alias):
                self.open(template_name, id, id_alias)

# ユーティリティークラス
# #############################################################################
# 基本は必要な情報をツリーでぶら下げる
# Treeが不要ならたぶんXUStateで事足りる
class _XUUtilBase(XUState):
    def __init__(self, state):
        super().__init__(state.xmlui, state._element)

    # すでに存在するElementを回収
    def find_child_root(self, state:XUStateRO, child_root_tag:str) -> XUState:
        return state.find_by_tag(child_root_tag).asRW()
 
    # findできなければ新規で作って追加する。新規作成時Trueを返す(is_created)
    def find_or_create_child_root(self, state:XUState, child_root_tag:str) -> tuple[XUState, bool]:
        try:
            # すでに存在するElementを回収
            return state.find_by_tag(child_root_tag).asRW(), False
        except Exception:
            # 新規作成
            created = XUState(state.xmlui, Element(child_root_tag))
            state.add_child(created)
            return created, True

# テキスト系
# ---------------------------------------------------------
# 半角を全角に変換
_from_hanakaku = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_to_zenkaku = "０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
_from_hanakaku += " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"  # 半角記号を追加
_to_zenkaku += "　！＂＃＄％＆＇（）＊＋，－．／：；＜＝＞？＠［￥］＾＿｀｛｜｝～"  # 全角記号を追加
_hankaku_zenkaku_dict = str.maketrans(_from_hanakaku, _to_zenkaku)

# まずは読み込み用
# *****************************************************************************
# テキスト基底
class XUPageBase(_XUUtilBase):
    # クラス定数
    ROOT_TAG= "_xmlui_page_root"
    PAGE_TAG ="_xmlui_page"
    SEPARATE_REGEXP = r"\\n"  # 改行に変換する正規表現

    PAGE_NO_ATTR = "page_no"  # ページ管理用

    # 文字列中の半角を全角に変換する
    @classmethod
    def convert_zenkaku(cls, hankaku:str) -> str:
        return unicodedata.normalize("NFKC", hankaku).translate(_hankaku_zenkaku_dict)

    # -----------------------------------------------------
    def __init__(self, state:XUStateRO, text:str, page_lins:int, wrap:int=4096):
        super().__init__(state)

        # パラメータの保存
        self._page_lines = page_lins
        self._wrap = max(wrap, 1)   # 0だと無限になってしまうので最低1を入れておく

        # ページルートの設定
        self.page_root, is_created = self.find_or_create_child_root(state.asRW(), self.ROOT_TAG)
        if is_created and text:
            self._setup(text)

    def _setup(self, text:str):
        # 改行を\nに統一して全角化
        tmp_text = self.convert_zenkaku(re.sub(self.SEPARATE_REGEXP, "\n", text).strip())

        # 各行に分解し、その行をさらにwrapで分解する
        lines =  sum([[line[i:i+self._wrap] for i in  range(0, len(line), self._wrap)] for line in tmp_text.splitlines()], [])

        # 再セットアップ用
        self.page_root.clear_children()
        self.reset_page()

        # ページごとにElementを追加
        for i in range(0, len(lines), self._page_lines):
            page_text = "\n".join(lines[i:i+self._page_lines])  # 改行を\nにして全部文字列に
            page = XUState(self.page_root.xmlui, Element(self.PAGE_TAG))
            page.set_text(page_text)
            self.page_root.add_child(page)

    def set_text(self, text:str) -> Self:
        self._setup(text)
        return self

    # ページ関係
    # -----------------------------------------------------
    # 現在ページ
    @property
    def page_no(self) -> int:
        return min(max(self.page_root.attr_int(self.PAGE_NO_ATTR, 0), 0), self.page_max)

    # ページの最大数
    @property
    def page_max(self) -> int:
        return len(self.page_root.find_by_tagall(self.PAGE_TAG))

    # ページ全部表示済みかどうか
    @property
    def is_end_page(self) -> bool:
        return self.page_no+1 >= self.page_max  # 1オリジンで数える

    # ページタグリスト
    @property
    def pages(self) -> list[XUStateRO]:
        return self.page_root.find_by_tagall(self.PAGE_TAG)

    # ページテキスト
    @property
    def page_text(self) -> str:
        return self._limitstr(self.pages[self.page_no].text, self.draw_count)

    # page_noの操作
    def next_page(self, add:int=1) -> Self:
        self.reset()  # ページが変わればまた最初から
        self.page_root.set_attr(self.PAGE_NO_ATTR, max(0, self.page_no+add))
        return self

    # ページを0に戻す
    def reset_page(self) -> Self:
        return self.next_page(-self.page_no)

    # アニメーション用
    # -----------------------------------------------------
    # draw_countまでの文字列を改行分割
    def _limitstr(self, tmp_text, draw_count:float) -> str:
        limit = math.ceil(draw_count)
        # まずlimitまで縮める
        for i,c in enumerate(tmp_text):
            if (limit := limit if c == "\n" else limit-1) < 0:  # 改行は数えない
                tmp_text = tmp_text[:i]
                break
        return tmp_text

    # 表示カウンタ取得
    @property
    def draw_count(self) -> float:
        return self.page_root.update_count * self.page_root.speed

    # 現在ページを表示しきったかどうか
    @property
    def is_finish(self) -> bool:
        # データ未設定時はいつでもfinish
        if not self.pages:
            return True
        return math.ceil(self.draw_count) >= len(self.pages[self.page_no].text.replace("\n", ""))

    # ページ送り待ち状態(ページ送りカーソルの表示が必要)
    @property
    def is_next_wait(self) -> bool:
        return self.is_finish and not self.is_end_page

    # 表示カウンタのリセット
    def reset(self) -> Self:
        self.page_root.set_attr("update_count", 0)
        return self

    # 一気に表示
    def finish(self) -> Self:
        return self

    # イベントアクション
    # -----------------------------------------------------
    # 状況に応じたactionを返す
    def check_action(self) -> str:
        # 表示しきっていたらメニューごと閉じる
        if self.is_end_page:
            return "close"
        # ページ中に残りがあるなら一気に表示
        if not self.is_finish:
            return "finish"
        # ページが残っていたら次のページへ
        elif not self.is_end_page:
            return "next_page"
        return ""


# メニュー系
# ---------------------------------------------------------
# グリッド情報
class XUSelectBase(_XUUtilBase):
    # クラス定数
    ROOT_TAG = "_xmlui_select_root"

    SELECTED_NO_ATTR = "_xmlui_selected"

    def __init__(self, state:XUStateRO, item_tag:str, rows_attr:str|None):
        super().__init__(state)
        try:
            self._select_root = state.find_by_tag(self.ROOT_TAG)
            self._items = self._select_root.find_by_tagall(item_tag)
        except:
            self._items: list[XUStateRO] = []
        self._rows = self.attr_int(rows_attr, 1) if rows_attr else 1

    @property
    def selected_no(self) -> int:
        return self.attr_int(self.SELECTED_NO_ATTR, 0)

    @property
    def selected_item(self) -> XUStateRO:
        return self._items[self.selected_no]

    @property
    def length(self) -> int:
        return len(self._items)

    # 値設定用
    # -----------------------------------------------------
    def select(self, no:int):
        self.set_attr(self.SELECTED_NO_ATTR, min(max(0, no), self.length))

    def next(self, add:int=1, x_wrap=False, y_wrap=False):
        # キャッシュ
        no = self.selected_no
        cols = self.length//self._rows

        x = no % self._rows
        y = no // self._rows
        sign = 1 if add >= 0 else -1
        add_x = abs(add) % self._rows * sign
        add_y = abs(add) // self._rows * sign

        # wrapモードとmin/maxモードそれぞれで設定
        x = (x + self._rows + add_x) % self._rows if x_wrap else min(max(x + add_x, 0), self._rows-1)
        y = (y + cols + add_y) % cols if y_wrap else min(max(y + add_y, 0), cols-1)

        self.select(y*self._rows + x)


# グリッド選択
class XUSelectGrid(XUSelectBase):
    def __init__(self, state:XUState, item_tag:str, rows_attr:str, item_w_attr:str, item_h_attr:str):
        super().__init__(state, item_tag, rows_attr)

        # グリッドルートの設定
        self._select_root, is_created = self.find_or_create_child_root(state, self.ROOT_TAG)
        if is_created:
            self._items = state.find_by_tagall(item_tag)
            item_w = state.attr_int(item_w_attr, 0)
            item_h = state.attr_int(item_h_attr, 0)

            # 選択用ルート下に接続しなおす
            for i,item in enumerate(self._items):
                # 座標設定
                item = item.asRW()
                item.set_attr("x", i % self._rows * item_w)
                item.set_attr("y", i // self._rows * item_h)

                # 登録しなおし
                self._select_root.add_child(item)

    # 入力に応じた挙動一括
    def _select_by_event(self, input:set[str], left_event:str, right_event:str, up_event:str, down_event:str, x_wrap:bool=False, y_wrap:bool=False) -> XUState:
        if left_event in input:
            self.next(-1, x_wrap, y_wrap)
        elif right_event in input:
            self.next(1, x_wrap, y_wrap)
        elif up_event in input:
            self.next(-self._rows, x_wrap, y_wrap)
        elif down_event in input:
            self.next(self._rows, x_wrap, y_wrap)
        return self.selected_item.asRW()

    def select_by_event(self, input:set[str], left_event:str, right_event:str, up_event:str, down_event:str) -> XUState:
        return self._select_by_event(input, left_event, right_event, up_event, down_event, False, False)

    def select_wrap_x(self, input:set[str], left_event:str, right_event:str, up_event:str, down_event:str) -> XUState:
        return self._select_by_event(input, left_event, right_event, up_event, down_event, True, False)

    def select_wrap_y(self, input:set[str], left_event:str, right_event:str, up_event:str, down_event:str) -> XUState:
        return self._select_by_event(input, left_event, right_event, up_event, down_event, False, True)


# リスト選択
class XUSelectList(XUSelectBase):
    def __init__(self, state:XUState, item_tag:str, item_h_attr:str):
        super().__init__(state, item_tag, None)

        # リストルートの設定
        self.select_root, is_created = self.find_or_create_child_root(state, self.ROOT_TAG)
        if is_created:
            self._items = state.find_by_tagall(item_tag)
            item_h = state.attr_int(item_h_attr, 0)

            # 選択用ルート下に接続しなおす
            for i,item in enumerate(self._items):
                # 座標設定
                item = item.asRW()
                item.set_attr("y", i * item_h)

                # 登録しなおし
                self.select_root.add_child(item)
  
    # 入力に応じた挙動一括。選択リストは通常上下ラップする
    def _select_by_event(self, input:set[str], up_event:str, down_event:str, y_wrap:bool=True) -> XUState:
        if up_event in input:
            self.next(-1, False, y_wrap)
        elif down_event in input:
            self.next(1, False, y_wrap)
        return self.selected_item.asRW()

    def select_by_event(self, input:set[str], up_event:str, down_event:str) -> XUState:
        return self._select_by_event(input, up_event, down_event, False)

    def select_wrap(self, input:set[str], up_event:str, down_event:str) -> XUState:
        return self._select_by_event(input, up_event, down_event, True)


# ダイアル
# ---------------------------------------------------------
# 情報管理のみ
class XUDialBase(XUState):
    ROOT_TAG = "_xmlui_dial_root"
    DIGIT_TAG = "_xmlui_dial_digit"

    EDIT_POS_ATTR = "edit_pos"  # 操作位置

    def __init__(self, state:XUState, digit_length:int, digit_list:str="0123456789"):
        super().__init__(state.xmlui, state._element)

        self._digit_list = digit_list
        for i in range(digit_length):
            digit = XUState(self.xmlui, Element(self.DIGIT_TAG))
            digit.set_text(digit_list[0])
            self.add_child(digit)


    @property
    def edit_pos(self) -> int:
        return self.attr_int(self.EDIT_POS_ATTR)

    @property
    def digits(self) -> list[str]:
        return [state.text for state in self.find_by_tagall(self.DIGIT_TAG)]

    @property
    def zenkaku_digits(self) -> list[str]:
        return [XUPageBase.convert_zenkaku(digit) for digit in self.digits]

    @property
    def number(self) -> int:
        return int("".join(reversed(self.digits)))

    # 回り込み付き操作位置の設定
    def set_editpos(self, edit_pos:int) -> Self:
        self.set_attr(self.EDIT_POS_ATTR, (edit_pos+len(self.digits))%len(self.digits))
        return self

    # 操作位置の移動
    def move_editpos(self, add:int) -> Self:
        return self.set_editpos(self.edit_pos+add)

    # 指定位置のdigitを変更する
    def set_digit(self, edit_pos:int, digit:str) -> Self:
        state = self.find_by_tagall(self.DIGIT_TAG)[edit_pos].asRW()
        state.set_text(digit)
        return self

    # 回り込み付きdigit増減
    def add_digit(self, edit_pos:int, add:int) -> Self:
        old_digit = self.digits[edit_pos]
        new_digit = self._digit_list[(self._digit_list.find(old_digit)+len(self._digit_list)+add) % len(self._digit_list)]
        return self.set_digit(edit_pos, new_digit)

    # 入力に応じた挙動一括
    def change_by_event(self, input:set[str], left_event:str, right_event:str, up_event:str, down_event:str) -> Self:
        if left_event in input:
            self.move_editpos(1)
        if right_event in input:
            self.move_editpos(-1)
        if up_event in input:
            self.add_digit(self.edit_pos, +1)  # digitを増やす
        if down_event in input:
            self.add_digit(self.edit_pos, -1)  # digitを減らす
        return self


# ウインドウサポート
# ---------------------------------------------------------
# 子ウインドウをopenするかもなのでROではいけない
class _XUWinFrameBase(XUStateRO):
    # 0 1 2
    # 3 4 5
    # 6 7 8
    def __init__(self, state:XUStateRO, pattern:list[int], screen_w:int, screen_h:int, pattern_index_func:Callable[[int,int,int,int], int]):
        super().__init__(state.xmlui, state._element)

        self._pattern = bytes(pattern)
        self._shadow_pattern = bytearray(pattern)
        self.pattern_size = len(pattern)  # 高速化のためここで変数に
        self.screen_w, self.screen_h = screen_w, screen_h
        self._get_patidx_func = pattern_index_func  # 枠外は-1を返す

        # クリッピングエリア
        self.clip = XURect(0, 0, screen_w, screen_h)

    # 1,3,5,7,4のエリア(カド以外)は特に計算が必要ない
    def _get13574index(self, x:int, y:int, w:int, h:int) -> int:
        return [-1, y, -1, x, self.pattern_size-1, w-1-x, -1, h-1-y][self.get_area(x, y, w, h)]

    # どのエリアに所属するかを返す
    def get_area(self, x:int, y:int, w:int, h:int) -> int:
        if x < self.pattern_size:
            if y < self.pattern_size:
                return 0
            return 3 if y < h-self.pattern_size else 6
        elif x < w-self.pattern_size:
            if y < self.pattern_size:
                return 1
            return 4 if y < h-self.pattern_size else 7
        else:
            if y < self.pattern_size:
                return 2
            return 5 if y < h-self.pattern_size else 8

    # シャドウ対応(0,1,3のパターン上書き)
    def set_shadow(self, index:int, color:int) -> Self:
        if self._shadow_pattern:
            self._shadow_pattern[index] = color
        return self

    # 中央部分をバッファに書き込む。
    # 環境依存の塗りつぶしが使えるならそちらを使った方が高速
    def _draw_center(self, screen_buf:bytearray):
        # self.areaは低速なので何度もアクセスするならローカル化
        area = self.area
        off_r, off_b = area.w, area.h  # オフセットなので0,0～w,h

        # 読みやすさのための展開(速度はほぼ変わらなかった)
        size = self.pattern_size
        clip_r,clip_b = self.clip.right(), self.clip.bottom()

        # 中央塗りつぶし
        w = min(clip_r, off_r) - size*2
        c_pat = self._pattern[-1:] * w
        for y_ in range(max(size, self.clip.y), min(clip_b, off_b-size)):
            offset = (area.y + y_)*self.screen_w + area.x + size
            if w > 0:
                screen_buf[offset:offset+w] = c_pat

    # フレームだけバッファに書き込む(高速化や半透明用)
    # 中央部分塗りつぶしは呼び出し側で行う
    def _draw_frame(self, screen_buf:bytearray):
        # self.areaは低速なので何度もアクセスするならローカル化
        area = self.area
        off_r, off_b = area.w, area.h  # オフセットなので0,0～w,h

        # 読みやすさのための展開(速度はほぼ変わらなかった)
        size = self.pattern_size
        clip_r,clip_b = self.clip.right(), self.clip.bottom()

        # 角の描画
        # ---------------------------------------------------------------------
        def _draw_shoulder(self, off_x:int, off_y:int, pattern:bytes|bytearray):
           # クリップチェック
            if self.clip.x <= off_x < clip_r and self.clip.y <= off_y < clip_b:
                index = self._get_patidx_func(off_x, off_y, off_r, off_b)
                if index >= 0:  # 枠外チェック
                    screen_buf[(area.y + off_y)*self.screen_w + (area.x + off_x)] = pattern[index]

        for y_ in range(size):
            for x_ in range(size):
                _draw_shoulder(self, x_, y_, self._shadow_pattern)  # 左上
                _draw_shoulder(self, off_r-1-x_, y_, self._shadow_pattern)  # 右上
                _draw_shoulder(self, x_, off_b-1-y_, self._shadow_pattern)  # 左下
                _draw_shoulder(self, off_r-1-x_, off_b-1-y_, self._pattern)  # 右下

        # bytearrayによる角以外の高速描画(patternキャッシュを作ればもっと速くなるかも)
        # ---------------------------------------------------------------------
        # 上下のライン
        w = min(clip_r, off_r) - max(0, self.clip.x) - size*2
        if w <= 0:
            return
        for y_ in range(size):
            if y_ >= self.clip.y:  # 上
                offset = (area.y + y_)*self.screen_w + area.x
                screen_buf[offset+max(0, self.clip.x)+size: offset+min(clip_r, off_r)-size] = self._shadow_pattern[y_:y_+1] * w
            if off_b-1-y_ < clip_b:  # 下
                offset = (area.y + off_b-1-y_)*self.screen_w + area.x
                screen_buf[offset+max(0, self.clip.x)+size: offset+min(clip_r, off_r)-size] = self._pattern[y_:y_+1] * w

        # 左右のライン
        r_pat = bytes(reversed(self._pattern))
        for y_ in range(max(size, self.clip.y), min(clip_b, off_b-size)):
            # 左
            offset = (area.y + y_)*self.screen_w + area.x
            w = size-max(0, self.clip.x)
            if w > 0:
                screen_buf[offset:offset+w] = self._shadow_pattern[:w]
            # 右
            offset = (area.y + y_)*self.screen_w + area.x + off_r - size
            w = min(clip_r-off_r, size)
            if w > 0:
                screen_buf[offset:offset+w] = r_pat[:w]

    # ウインドウ全体をバッファに書き込む
    def draw_buf(self, screen_buf:bytearray):
        self._draw_center(screen_buf)
        self._draw_frame(screen_buf)

class XUWinRoundFrame(_XUWinFrameBase):
    def __init__(self, state:XUStateRO, pattern:list[int], screen_w:int, screen_h:int):
        super().__init__(state, pattern, screen_w, screen_h, self._get_patternindex)

    def _get_veclen(self, x:int, y:int, org_x:int, org_y:int) -> int:
        return math.ceil(math.sqrt((x-org_x)**2 + (y-org_y)**2))

    def _get_patternindex(self, x:int, y:int, w:int, h:int) -> int:
        size = self.pattern_size
        match self.get_area(x, y, w, h):
            case 0:
                l = size-1-self._get_veclen(x, y, size-1, size-1)
                return l if l < size else -1
            case 2:
                l = size-1-self._get_veclen(x, y, w-size, size-1)
                return l if l < size else -1
            case 6:
                l = size-1-self._get_veclen(x, y, size-1, h-size)
                return l if l < size else -1
            case 8:
                l = size-1-self._get_veclen(x, y, w-size, h-size)
                return l if l < size else -1
        return self._get13574index(x, y, w, h)

class XUWinRectFrame(_XUWinFrameBase):
    def __init__(self, state:XUStateRO, pattern:list[int], screen_w:int, screen_h:int):
        super().__init__(state, pattern, screen_w, screen_h, self._get_pattern_index)

    def _get_pattern_index(self, x:int, y:int, w:int, h:int) -> int:
        match self.get_area(x, y, w, h):
            case 0:
                return y if x > y else x
            case 2:
                return y if w-1-x > y else w-1-x
            case 6:
                return h-1-y if x > h-1-y else x
            case 8:
                return h-1-y if w-1-x > h-1-y else w-1-x
        return self._get13574index(x, y, w, h)

