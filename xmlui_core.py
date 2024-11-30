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


# 描画領域計算用
# #############################################################################
class XURect:
    def __init__(self, x:int, y:int, w:int, h:int):
        self.x = x
        self.y = y
        self.w = max(0, w)
        self.h = max(0, h)

    def intersect(self, other) -> "XURect":
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
        self.clear()
        self._wait_update = 0

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
    def tag(self) -> str:
        return self._element.tag

    @property
    def area(self) -> XURect:
        return XURect(self.area_x, self.area_y, self.area_w, self.area_h)

    def asRW(self) -> 'XUState':
        return XUState(self.xmlui, self._element)

    def asRO(self) -> 'XUStateRO':
        return XUStateRO(self.xmlui, self._element)

    @property
    def valid(self) -> bool:
        return self.update_count > 0  # 初期化済み

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

    # 下階層ではなく、上(root)に向かって探索する
    def find_by_tagR(self, tag:str) -> 'XUStateRO':
        parent = self.parent
        while(parent):
            if parent.tag == tag:
                return parent
            parent = parent.parent
        raise Exception(f"Tag '{tag}' not found in parents")

    def is_open(self, id:str) -> bool:
        try:
            self.find_by_ID(id)
            return True
        except:
            return False

    @property
    def parent(self) -> 'XUState|None':
        def _rec_parent_search(element:Element, me:Element) -> Element|None:
            if me in element:
                return element
            for child in element:
                result = _rec_parent_search(child, me)
                if result:
                    return result
            return None
        parent = _rec_parent_search(self.xmlui._element, self._element)
        return XUState(self.xmlui, parent) if parent else None
 
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
    def area_x(self) -> int:  # 表示最終座標x
        return self.attr_int("area_x", 0)
    @property
    def area_y(self) -> int:  # 表示最終座標y
        return self.attr_int("area_y", 0)
    @property
    def area_w(self) -> int:  #  表示最終幅
        return self.attr_int("area_w", 4096)
    @property
    def area_h(self) -> int:  #  表示最終高さ
        return self.attr_int("area_h", 4096)

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
    def selected(self) -> int:  # 選択されている
        return self.attr_bool("selected", False)

    @property
    def layer(self) -> int:  # 描画レイヤ
        return self.attr_int("layer", 0)

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
    def add_child(self, child:XUStateRO):  # selfとchildどっちが返るかややこしいのでNone
        self._element.append(child._element)

    def clear_children(self) -> Self:
        self._element.clear()
        return self

    def remove(self):  # removeの後なにかすることはないのでNone
        # 処理対象から外れるように
        self.set_attr("enable", False)
        if self.parent:  # 親から外す
            self.parent._element.remove(self._element)

    # 子に別Element一式を追加する
    def open(self, template_name:str, id:str, id_alias:str|None=None) -> 'XUState':
        # Trg入力を落とす(open/closeが連続しないよう)
        self.xmlui.event.clearTrg()

        # idがかぶらないよう別名を付けられる
        id_alias = id if id_alias is None else id_alias
        try:
            # すでに存在するかチェック
            self.xmlui.find_by_ID(id_alias)
        except:
            # 見つからず例外がでればOK
            opend = self.xmlui._templates[template_name].duplicate(id).set_attr("id", id_alias)
            opend.set_attr("use_event", True)  # openで追加するときはeventを有効に
            self.add_child(opend)
            return opend

        # IDがかぶってはいけない
        raise Exception(f"ID '{id_alias}' already exists")
 
    def close(self, id:str|None=None):  # closeの後なにもしないのでNone
        # Trg入力を落とす(open/closeが連続しないよう)
        self.xmlui.event.clearTrg()

        if id is not None:
            self.xmlui.find_by_ID(id).asRW().remove()
        else:
            self.remove()


# XMLでUIライブラリ本体
# #############################################################################
# テンプレート用
class XMLUI_Template(XUStateRO):
    # 初期化
    # *************************************************************************
    # ファイルから読み込み
    @classmethod
    def _fromfile(cls, xmlui:'XMLUI', fileName:str, root_tag:str|None=None) -> 'XMLUI_Template':
        with open(fileName, "r", encoding="utf8") as f:
            return cls._fromstring(xmlui, f.read())

    # リソースから読み込み
    @classmethod
    def _fromstring(cls, xmlui:'XMLUI', xml_data:str) -> 'XMLUI_Template':
        return XMLUI_Template(XUState(xmlui, xml.etree.ElementTree.fromstring(xml_data)))

    def __init__(self, root:XUStateRO):
        super().__init__(root.xmlui, root._element)

    # XML操作
    # *************************************************************************
    # Elmentを複製して取り出す
    def duplicate(self, id:str) -> XUState:
        return XUState(self.xmlui, copy.deepcopy(self.find_by_ID(id)._element))

# デバッグ用
class XMLUI_Debug(XUState):
    # デバッグ用フラグ
    DEBUG_LEVEL_LIB:int = 100  # ライブラリ作成用
    DEBUG_LEVEL_DEFAULT:int = 0

    def __init__(self):
        self.level = self.DEBUG_LEVEL_DEFAULT

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

        # デバッグ用
        self.debug = XMLUI_Debug()

        # 入力
        self.event = XUEvent(True)  # 唯一のactiveとする
        self._input_lists:dict[str, list[int]] = {}

        # 処理関数の登録
        self._update_funcs:dict[str,Callable[[XUState,XUEvent], None]] = {}
        self._draw_funcs:dict[str,Callable[[XUStateRO,XUEvent], None]] = {}

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
    def _get_updatetargets(self, state:XUState) -> Generator[XUState, None, None]:
        if state.enable:
            yield state
            # enableの子だけ回収(disableの子は削除)
            for child in state._element:
                yield from self._get_updatetargets(XUState(self, child))

    def update(self):
        # (入力)イベントの更新
        self.event.update()

        # 更新対象を取得
        update_targets = list(self._get_updatetargets(self))

        # イベント発生対象は表示物のみ
        event_targets = [state for state in update_targets if state.visible and state.use_event]
        self.active_state = event_targets[-1] if event_targets else self  # Active=最後

        # 更新処理
        for state in update_targets:
            if state.enable:  # update中にdisable(remove)になる場合があるので毎回チェック
                state.set_attr("update_count", state.update_count+1)  # 1スタート(0は初期化時)
                self.update_element(state.tag, state, self.event if state == self.active_state else XUEvent())

    # 描画用
    # *************************************************************************
    def _get_drawtargets(self, state:XUState) -> Generator[XUState, None, None]:
        if state.enable and state.visible and state.valid:  # not valied(update_count==0)はUpdateで追加されたばかりのもの(未Update)
            yield state
            # visibleの子だけ回収(invisibleの子は削除)
            for child in state._element:
                yield from self._get_drawtargets(XUState(self, child))

    def draw(self):
        # 描画対象を取得
        draw_targets = list(self._get_drawtargets(self))

        # イベント発生対象は表示物のみ
        event_targets = [state for state in draw_targets if state.use_event]
        active_state = event_targets[-1] if event_targets else None  # Active=最後

        # 更新処理
        for state in draw_targets:
            # 親を持たないElementは更新不要
            if state.parent is None:
                continue

            # エリア更新。absがあれば絶対座標、なければ親からのオフセット
            state.set_attr("area_x", state.abs_x if state.has_attr("abs_x") else state.x + state.parent.area_x)
            state.set_attr("area_y", state.abs_y if state.has_attr("abs_y") else state.y + state.parent.area_y)
            state.set_attr("area_w", state.attr_int("w", state.parent.area_w))
            state.set_attr("area_h", state.attr_int("h", state.parent.area_h))

            if not state.has_attr("layer") and state.parent:
                state.set_attr("layer", state.parent.layer)  # 自身がlayerを持っていなければ親から引き継ぐ

        # 描画処理
        for state in sorted(draw_targets, key=lambda state: state.layer):
            self.draw_element(state.tag, state, self.event if state == active_state else XUEvent())

    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def update_element(self, tag_name:str, state:XUState, event:XUEvent):
        # 登録済みの関数だけ実行
        if tag_name in self._update_funcs:
            self._update_funcs[tag_name](state, event)

    def draw_element(self, tag_name:str, state:XUStateRO, event:XUEvent):
        # 登録済みの関数だけ実行
        if tag_name in self._draw_funcs:
            self._draw_funcs[tag_name](state, event)


    # 処理登録
    # *************************************************************************
    def set_updatefunc(self, tag_name:str, func:Callable[[XUState,XUEvent], None]):
        self._update_funcs[tag_name] = func

    def set_drawfunc(self, tag_name:str, func:Callable[[XUStateRO,XUEvent], None]):
        self._draw_funcs[tag_name] = func

    # デコレータを用意
    def update_bind(self, tag_name:str):
        def wrapper(update_func:Callable[[XUState,XUEvent], None]):
            self.set_updatefunc(tag_name, update_func)
        return wrapper

    def draw_bind(self, tag_name:str):
        def wrapper(draw_func:Callable[[XUStateRO,XUEvent], None]):
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

    def check_input(self, check:str, check_func:Callable[[int], bool]) -> bool:
        for button in self._input_lists[check]:
            if check_func(button):
                return True
        return False

    # 登録キー入力を全部調べて片っ端からイベントに登録
    def check_input_on(self, check_func:Callable[[int], bool]):
        for key in self._input_lists:
            if self.check_input(key, check_func):
                self.event.on(key)


# ユーティリティークラス
# #############################################################################
# 基本は必要な情報をツリーでぶら下げる
# Treeが不要ならたぶんXUStateで事足りる
class _XUUtil:
    # すでに存在するElementを回収
    def find_state(self, parent:XUStateRO, child_root_tag:str) -> XUStateRO:
        return parent.find_by_tag(child_root_tag).asRO()
 
    # findできなければ新規で作って追加する
    # 新規作成時Trueを返す(is_created)
    def find_or_create_state(self, parent:XUState, child_root_tag:str) -> tuple[XUState, bool]:
        try:
            return parent.find_by_tag(child_root_tag).asRW(), False
        except Exception:
            # 新規作成
            state = XUState(parent.xmlui, Element(child_root_tag))
            parent.add_child(state)
            return state,True

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
class XUPageRO(_XUUtil):
    # クラス定数
    ROOT_TAG= "_xmlui_page_root"
    PAGE_TAG ="_xmlui_page"
    SEPARATE_REGEXP = r"\\n"  # 改行に変換する正規表現

    PAGE_NO_ATTR = "page_no"  # ページ管理用

    def __init__(self, parent: XUStateRO):
        self.page_root = self.find_state(parent, self.ROOT_TAG)

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
        # ページオーバーチェック
        if self.is_end_page:
            return ""
        return self._limitstr(self.pages[self.page_no].text, self.draw_count)

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

    @property
    def is_next_wait(self) -> bool:
        return self.is_finish and not self.is_end_page

    # ユーティリティ
    # -----------------------------------------------------
    # 文字列中の半角を全角に変換する
    @classmethod
    def convert_zenkaku(cls, hankaku:str) -> str:
        return unicodedata.normalize("NFKC", hankaku).translate(_hankaku_zenkaku_dict)

# アニメーションテキストページ管理
class XUPage(XUPageRO):
    def __init__(self, parent:XUState, text:str, page_line_num:int, wrap:int=4096):
        # パラメータの保存
        self._page_line_num = page_line_num
        self._wrap = max(wrap, 1)   # 0だと無限になってしまうので最低1を入れておく

        # ページタグの作成
        self.page_root, is_created = self.find_or_create_state(parent, self.ROOT_TAG)
        if is_created:
            self.setup(text)

    # PAGE_ROOT_TAG以下(ページテキスト)の設定
    # Update中にテキストを再設定するのにも使える
    def setup(self, text:str):
        # 改行を\nに統一して全角化
        tmp_text = self.convert_zenkaku(re.sub(self.SEPARATE_REGEXP, "\n", text).strip())

        # 各行に分解し、その行をさらにwrapで分解する
        lines =  sum([[line[i:i+self._wrap] for i in  range(0, len(line), self._wrap)] for line in tmp_text.splitlines()], [])

        # 再セットアップ用
        self.page_root.clear_children()
        self.reset_page()

        # ページごとにElementを追加
        for i in range(0, len(lines), self._page_line_num):
            page_text = "\n".join(lines[i:i+self._page_line_num])  # 改行を\nにして全部文字列に
            page = XUState(self.page_root.xmlui, Element(self.PAGE_TAG))
            page.set_text(page_text)
            self.page_root.add_child(page)


    # ページ関係
    # -----------------------------------------------------
    # page_noの操作
    def next_page(self, add:int=1) -> Self:
        self.reset()  # ページが変わればまた最初から
        self.page_root.set_attr(self.PAGE_NO_ATTR, self.page_no+1)
        return self

    def reset_page(self) -> Self:
        self.page_root.set_attr(self.PAGE_NO_ATTR, 0)
        self.reset()  # ページが変わればまた最初から
        return self

    # アニメーション用
    # -----------------------------------------------------
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
class _XUSelectBase(XUStateRO):
    def __init__(self, state:XUStateRO, grid:list[list[XUState]]):
        super().__init__(state.xmlui, state._element)
        self._grid = grid

        # タグにselected=Trueがあればそれを使う。無ければgrid[0][0]を選択
        try:
            self.selected_item  # プロパティによる検索
        except:
            self.select(0, 0)  # 最初の選択

    # GRID用
    @classmethod
    def find_grid(cls, state:XUStateRO, tag_group:str, tag_item:str) -> list[list[XUState]]:
        return [[ro.asRW() for ro in group.find_by_tagall(tag_item)] for group in state.find_by_tagall(tag_group)]

    # 転置(Transpose)GRID
    @classmethod
    def find_gridT(cls, state:XUStateRO, tag_group:str, tag_item:str) -> list[list[XUState]]:
        grid = cls.find_grid(state, tag_group, tag_item)
        grid = [[grid[y][x] for y in range(len(grid))] for x in range(len(grid[0]))]  # 転置
        return grid

    # グリッド各アイテムの座標設定
    def arrange_items(self, w:int, h:int) -> Self:
        for y,group in enumerate(self._grid):
            for x,item in enumerate(group):
                item.set_attr(["x", "y"], (x*w, y*h))
        return self


    # 範囲限定付き座標設定
    def select(self, x:int, y:int, x_wrap:bool=False, y_wrap:bool=False) -> Self:
        cur_x = (x + self.grid_w) % self.grid_w if x_wrap else max(min(x, self.grid_w-1), 0)
        cur_y = (y + self.grid_h) % self.grid_h if y_wrap else max(min(y, self.grid_h-1), 0)
        for y,group in enumerate(self._grid):
            for x,item in enumerate(group):
                item.set_attr("selected", x == cur_x and y == cur_y)
        return self

    @property
    def selected_item(self) -> XUState:
        for group in self._grid:
            for item in group:
                if item.selected:
                    return item
        raise Exception("selected item not found")

    @property
    def cur_x(self) -> int:
        for group in self._grid:
            for x,item in enumerate(group):
                if item.selected:
                    return x
        return 0

    @property
    def cur_y(self) -> int:
        for y,group in enumerate(self._grid):
            for item in group:
                if item.selected:
                    return y
        return 0

    @property
    def grid_w(self) -> int:
        return len(self._grid[0])

    @property
    def grid_h(self) -> int:
        return len(self._grid)


# グリッド選択
class XUSelectGrid(_XUSelectBase):
    def __init__(self, state:XUStateRO, tag_group:str, tag_item:str):
        super().__init__(state, self.find_grid(state, tag_group, tag_item))

    # 入力に応じた挙動一括
    def select_by_event(self, input:set[str], left_event:str, right_event:str, up_event:str, down_event:str, x_wrap:bool=False, y_wrap:bool=False) -> Self:
        if left_event in input:
            self.select(self.cur_x-1, self.cur_y, x_wrap)
        elif right_event in input:
            self.select(self.cur_x+1, self.cur_y, x_wrap)
        elif up_event in input:
            self.select(self.cur_x, self.cur_y-1, False, y_wrap)
        elif down_event in input:
            self.select(self.cur_x, self.cur_y+1, False, y_wrap)
        return self

# リスト選択
class XUSelectList(_XUSelectBase):
    # 縦に入れる
    def __init__(self, state:XUStateRO, tag_item:str):
        super().__init__(state, self.find_gridT(state, state.tag, tag_item))

    # 入力に応じた挙動一括。選択リストは通常上下ラップする
    def select_by_event(self, input:set[str], up_event:str, down_event:str, y_wrap:bool=True) -> Self:
        if up_event in input:
            self.select(0, self.cur_y-1, False, y_wrap)
        elif down_event in input:
            self.select(0, self.cur_y+1, False, y_wrap)
        return self

    # グリッド各アイテムの座標設定
    def arrange_items(self, w:int, h:int) -> Self:
        for y,group in enumerate(self._grid):
            item = group[0]  # Listはxで並ばない
            item.set_attr(["x", "y"], (y*w, y*h))  # 両方ともYを使って横に並べられるように
        return self


# ダイアル
# ---------------------------------------------------------
# 情報管理のみ
class XUDialRO(_XUUtil):
    ROOT_TAG = "_xmlui_dial_root"
    DIGIT_TAG = "_xmlui_dial_digit"

    EDIT_POS_ATTR = "edit_pos"  # 操作位置

    def __init__(self, parent:XUStateRO, allow_create:bool=False):
        self.state = self.find_state(parent, self.ROOT_TAG).asRW()

    @property
    def edit_pos(self) -> int:
        return self.state.attr_int(self.EDIT_POS_ATTR)

    @property
    def digits(self) -> list[str]:
        return [state.text for state in self.state.find_by_tagall(self.DIGIT_TAG)]

    @property
    def zenkaku_digits(self) -> list[str]:
        return [XUPageRO.convert_zenkaku(digit) for digit in self.digits]

    @property
    def number(self) -> int:
        return int("".join(reversed(self.digits)))

# ダイアル操作
class XUDial(XUDialRO):
    def __init__(self, parent:XUState, digit_length:int, digit_list:str="0123456789"):
        self.state, is_created = self.find_or_create_state(parent, self.ROOT_TAG)
        if is_created:
            # 初期値は最小埋め
            for i in range(digit_length):
                digit = XUState(self.state.xmlui, Element(self.DIGIT_TAG))
                digit.set_text(digit_list[0])
                self.state.add_child(digit)

        self._digit_list = digit_list

    # 回り込み付き操作位置の設定
    def set_editpos(self, edit_pos:int) -> Self:
        self.state.set_attr(self.EDIT_POS_ATTR, (edit_pos+len(self.digits))%len(self.digits))
        return self

    # 操作位置の移動
    def move_editpos(self, add:int) -> Self:
        return self.set_editpos(self.edit_pos+add)

    # 指定位置のdigitを変更する
    def set_digit(self, edit_pos:int, digit:str) -> Self:
        state = self.state.find_by_tagall(self.DIGIT_TAG)[edit_pos].asRW()
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
class _XUWinFrameBase(XUState):
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
        # areaはアトリビュートなのでばらすとかなり高速化
        area_x, area_y = self.area.x, self.area.y
        off_r, off_b = self.area.w, self.area.h  # オフセットなので0,0～w,h

        # 読みやすさのための展開(速度はほぼ変わらなかった)
        size = self.pattern_size
        clip_r,clip_b = self.clip.right(), self.clip.bottom()

        # 中央塗りつぶし
        w = min(clip_r, off_r) - size*2
        c_pat = self._pattern[-1:] * w
        for y_ in range(max(size, self.clip.y), min(clip_b, off_b-size)):
            offset = (area_y + y_)*self.screen_w + area_x + size
            if w > 0:
                screen_buf[offset:offset+w] = c_pat

    # フレームだけバッファに書き込む(高速化や半透明用)
    # 中央部分塗りつぶしは呼び出し側で行う
    def _draw_frame(self, screen_buf:bytearray):
        # areaはアトリビュートなのでばらすとかなり高速化
        area_x, area_y = self.area.x, self.area.y
        off_r, off_b = self.area.w, self.area.h  # オフセットなので0,0～w,h

        # 読みやすさのための展開(速度はほぼ変わらなかった)
        size = self.pattern_size
        clip_r,clip_b = self.clip.right(), self.clip.bottom()

        # 角の描画
        # ---------------------------------------------------------------------
        def _draw_shoulder(self, off_x:int, off_y:int, pattern:bytes|bytearray):
            # クリップチェック
            if self.clip.x < off_x < clip_r and self.clip.y < off_y < clip_b:
                index = self._get_patidx_func(off_x, off_y, off_r, off_b)
                if index >= 0:  # 枠外チェック
                    if pattern[index] >= 0:  # 透明チェック
                        screen_buf[(area_y + off_y)*self.screen_w + (area_x + off_x)] = pattern[index]

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
        for y_ in range(size):
            if y_ >= self.clip.y:  # 上
                offset = (area_y + y_)*self.screen_w + area_x
                screen_buf[offset+max(0, self.clip.x)+size: offset+min(clip_r, off_r)-size] = self._shadow_pattern[y_:y_+1] * w
            if off_b-1-y_ < clip_b:  # 下
                offset = (area_y + off_b-1-y_)*self.screen_w + area_x
                screen_buf[offset+max(0, self.clip.x)+size: offset+min(clip_r, off_r)-size] = self._pattern[y_:y_+1] * w

        # 左右のライン
        r_pat = bytes(reversed(self._pattern))
        for y_ in range(max(size, self.clip.y), min(clip_b, off_b-size)):
            # 左
            offset = (area_y + y_)*self.screen_w + area_x
            w = size-max(0, self.clip.x)
            if w > 0:
                screen_buf[offset:offset+w] = self._shadow_pattern[:w]
            # 右
            offset = (area_y + y_)*self.screen_w + area_x + off_r - size
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

