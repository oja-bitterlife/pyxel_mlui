# XMLを使うよ
import xml.etree.ElementTree
from xml.etree.ElementTree import Element

# 日本語対応
import unicodedata

# その他よく使う奴
import re
import math
import copy
from distutils.util import strtobool
from typing import Callable,Any,Self  # 型を使うよ


# 描画領域計算用
# #############################################################################
class XURect:
    ALIGN_CENTER = "center"
    ALIGN_LEFT = "left"
    ALIGN_RIGHT = "right"
    ALIGN_TOP = "top"
    ALIGN_BOTTOM = "bottom"

    def __init__(self, x:int, y:int, w:int, h:int):
        self.x = x
        self.y = y
        self.w = max(0, w)
        self.h = max(0, h)

    def copy(self) -> "XURect":
        return XURect(self.x, self.y, self.w, self.h)

    # 変換
    def intersect(self, other:"XURect") -> "XURect":
        right = min(self.x+self.w, other.x+other.w)
        left = max(self.x, other.x)
        bottom = min(self.y+self.h, other.y+other.h)
        top = max(self.y, other.y)
        return XURect(left, top, right-left, bottom-top)

    def inflate(self, w, h) -> "XURect":
        return XURect(self.x-w, self.y-h, self.w+w*2, self.h+h*2)

    # offset化
    def to_offset(self) -> "XURect":
        return XURect(0, 0, self.w, self.h)

    # 内包チェック
    def contains_x(self, x:int) -> bool:
        return self.x <= x < self.x+self.w

    def contains_y(self, y:int) -> bool:
        return self.y <= y < self.y+self.h

    def contains(self, x, y) -> bool:
        return self.x <= x < self.x+self.w and self.y <= y < self.y+self.h

    # 空チェック
    @property
    def is_empty(self) -> int:
        return self.w <= 0 or self.h <= 0

    # 座標取得
    def center_x(self, w:int=0) -> int:
        return self.x + (self.w-w)//2

    def center_y(self, h:int=0) -> int:
        return self.y + (self.h-h)//2

    def right(self, right_space:int=0) -> int:
        return self.x + self.w - right_space

    def bottom(self, bottom_space:int=0) -> int:
        return self.y + self.h - bottom_space

    # 座標取得
    def aligned_x(self, w:int=0, align=ALIGN_CENTER) -> int:
        match align:
            case self.ALIGN_LEFT:
                x =  self.x
            case self.ALIGN_CENTER:
                x = self.center_x(w)
            case self.ALIGN_RIGHT:
                x = self.right(w)
            case _:
                raise ValueError(f"align:{align} is not supported.")
        return x

    def aligned_y(self, h:int=0, valign=ALIGN_CENTER) -> int:
        match valign:
            case self.ALIGN_TOP:
                y =  self.y
            case self.ALIGN_CENTER:
                y = self.center_y(h)
            case self.ALIGN_BOTTOM:
                y = self.bottom(h)
            case _:
                raise ValueError(f"align:{valign} is not supported.")
        return y

    def __repr__(self) -> str:
        return f"RECT({self.x}, {self.y}, {self.w}, {self.h})"


# イベント管理用
class XUEvent:
    # 綴り間違いをしないようuse_eventをチェックする時は定数を使うようにする
    ABSORBER = "absorber"
    LISTENER = "listener"
    NONE = ""  # ifでチェックしやすいようemptyで

    def __init__(self, init_active=False):
        self.is_active = init_active  # アクティブなイベントかどうか
        self.on_init = False
        self.clear()

    def clear(self):
        self._receive:set[str] = set([])  # 次の状態受付

        self.now:set[str] = set([])
        self.trg:set[str] = set([])
        self._release:set[str] = set([])

    def clear_trg(self):
        self.trg:set[str] = set([])
        self._release:set[str] = set([])

    # 更新
    def update(self):
        # 状態更新
        self.trg = set([i for i in self._receive if i not in self.now])
        self._relase = set([i for i in self.now if i not in self._receive])
        self.now = self._receive

        # 取得し直す
        self._receive = set([])

    # 入力
    def _on(self, event_name:str):
        if event_name in self._receive:
            raise ValueError(f"event_name:{event_name} is already registered.")
        self._receive.add(event_name)

# UIパーツの状態取得
# #############################################################################
# XMLの状態管理ReadOnly
class XUState:
    def __init__(self, xmlui:'XMLUI', element:Element):
        self.xmlui = xmlui  # ライブラリへのIF
        self._element = element  # 自身のElement

    def ref(self) -> "XUState":
        return XUState(self.xmlui, self._element)

    # UI_Stateは都度使い捨てなので、対象となるElementで比較する
    def __eq__(self, other) -> bool:
        if isinstance(other, XUState):
            return other._element is self._element
        else:
            return super().__eq__(other)

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
        return default if attr is None else bool(strtobool(attr))

    def has_attr(self, key: str) -> bool:
        return key in self._element.attrib

    def set_attr(self, key:str|list[str], value: Any) -> Self:
        # attribはdict[str,str]なのでstrで保存する
        if isinstance(key, list):
            for i, k in enumerate(key):
                self._element.attrib[k] = str(value[i])
        else:
            self._element.attrib[key] = str(value)
        return self

    # tagアクセス用
    @property
    def tag(self) -> str:
        return self._element.tag

    # textアクセス用
    @property
    def text(self) -> str:
        return "\n".join([line.strip() for line in self._element.text.splitlines()]) if self._element.text else ""
    @text.setter
    def text(self, text_:str) -> str:
        self._element.text = text_
        return text_

    # その他
     # *************************************************************************
    @property
    def area(self) -> XURect:  # 親からの相対座標
        # areaは良く呼ばれるので、一回でもparent探しのdictアクセスを軽減する
        parent = self.parent
        parent_area = parent.area if parent else XURect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h)

        # x,yはアトリビュートなので何度もアクセスしないように
        offset_x, offset_y = self.x, self.y

        # absがあれば絶対座標、なければ親からのオフセット
        return XURect(
            self.abs_x if self.has_attr("abs_x") else offset_x + parent_area.x,
            self.abs_y if self.has_attr("abs_y") else offset_y + parent_area.y,
            self.attr_int("w", parent_area.w - offset_x),
            self.attr_int("h", parent_area.h - offset_y)
        )

    def set_pos(self, x:int, y:int) -> Self:
        return self.set_attr(["x", "y"], [x, y])

    def set_abspos(self, x:int, y:int) -> Self:
        return self.set_attr(["abs_x", "abs_y"], [x, y])

    def set_wh(self, w:int, h:int) -> Self:
        return self.set_attr(["w", "h"], [w, h])

    # ツリー操作用
    # *************************************************************************
    @property
    def parent(self) -> 'XUState|None':
        return self.xmlui._parent_cache.get(self._element, None)

    @property
    def children(self) -> list["XUState"]:
        return [XUState(self.xmlui, child) for child in self._element.iter()][1:]  # 最初は自分なので外す

    # 親以上祖先リスト
    @property
    def ancestors(self) -> 'list[XUState]':
        out:list[XUState] = []
        parent = self.parent
        while parent:
            out.append(parent)
            parent = parent.parent
        return out

    def find_by_id(self, id:str) -> 'XUState':
        for element in self._element.iter():
            if element.attrib.get("id") == id:
                return XUState(self.xmlui, element)
        raise Exception(f"{self.strtree()}\nID '{id}' not found in '{self.tag}' and children")

    def find_by_tagall(self, tag:str) -> list['XUState']:
        return [XUState(self.xmlui, element) for element in self._element.iter() if element.tag == tag]

    def find_by_tag(self, tag:str) -> 'XUState':
        elements:list[XUState] = self.find_by_tagall(tag)
        if elements:
            return elements[0]
        raise Exception(f"{self.strtree()}\nTag '{tag}' not found in '{self.tag}' and children")

    # ツリーを遡って親を探す
    def find_parent_by_id(self, id:str) -> 'XUState':
        parent = self.parent
        while parent:
            if parent.id == id:
                return parent
            parent = parent.parent
        raise Exception(f"{self.strtree()}\nParent '{id}' not found in '{self.tag}' parents")

    # openした親
    def find_owner(self) -> 'XUState':
        return self.find_parent_by_id(self.owner)

    # すでにツリーに存在するか
    def exists_id(self, id:str) -> bool:
        for element in self._element.iter():
            if element.attrib.get("id") == id:
                return True
        return False

    def exists_tag(self, tag:str) -> bool:
        elements:list[XUState] = self.find_by_tagall(tag)
        if elements:
            return True
        return False

    # 子を追加する
    def add_child(self, child:"XUState"):
        self._element.append(child._element)
        self.xmlui._parent_cache[child._element] = self

    # 子を全部削除する
    def clear_children(self):
        # clearでattribまで消えるので、attrに保存して戻す
        attr = self._element.attrib.copy()
        self._element.clear()
        self._element.attrib = attr

    # 自分を親から外す
    def remove(self):
        if self.parent is None:
            self.marker = "<--- can't remove"
            raise Exception(f"{self.strtree()}\nCan't remove {self.tag}")
        self.parent._element.remove(self._element)

    # open/close
    # *************************************************************************
    # 子に別Element一式を追加する
    def open(self, template_name:str, id:str, id_alias:str|None=None) -> "XUState":
        # idがかぶらないよう別名を付けられる
        id_alias = id if id_alias is None else id_alias

        # IDがかぶってはいけない
        if self.xmlui.exists_id(id_alias):
            return self.xmlui.find_by_id(id_alias)
            # raise Exception(f"ID '{id_alias}' already exists")

        # オープン
        opend = self.xmlui._templates[template_name].duplicate(id).set_attr("id", id_alias)
        self.add_child(opend)

        # ownerを設定しておく
        for child in opend.children:
            child.set_attr("owner", id_alias)

        # open/closeが連続しないようTrg入力を落としておく
        self.xmlui.event.clear_trg()
        return opend

    # すぐにclose
    def close(self):
        # open/closeが連続しないようTrg入力を落としておく
        self.xmlui.event.clear_trg()

        # ownerが設定されていればownerを、無ければ自身をremoveする
        if self.owner and self.xmlui.exists_id(self.owner):
            target = self.xmlui.find_by_id(self.owner)
        else:
            target = self

        target.remove()

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
    @value.setter
    def value(self, val:str):  # state間汎用値持ち運び用
        self.set_attr("value", val)

    @property
    def action(self) -> str:  # イベント情報取得
        return self.attr_str("action", "")
    @property
    def selected(self) -> bool:  # 選択アイテムの選択状態
        return self.attr_bool("selected", False)

    @property
    def owner(self) -> str:  # close時のidを設定
        return self.attr_str("owner", "")

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
        return self.attr_int("w", self.xmlui.screen_w)
    @property
    def h(self) -> int:  # elementの高さ
        return self.attr_int("h", self.xmlui.screen_h)

    @property
    def update_count(self) -> int:  # updateが行われた回数
        return self.attr_int("update_count", 0)

    @property
    def use_event(self) -> str:  # eventの検知方法, listener or absorber or ""
        return self.attr_str("use_event", XUEvent.NONE)

    @property
    def enable(self) -> bool:  # イベント有効フラグ(表示は使う側でどうするか決める)
        return self.attr_bool("enable", True)
    @enable.setter
    def enable(self, enable_:bool) -> bool:
        self.set_attr("enable", enable_)
        return enable_

    @property
    def marker(self) -> str:  # デバッグ用
        return self.attr_str("marker", "")
    @marker.setter
    def marker(self, marker_:str) -> str:
        self.set_attr("marker", marker_)
        return marker_


# XMLでUIライブラリ本体
# #############################################################################
# テンプレート用
class XMLUI_Template(XUState):
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

    def __init__(self, root:XUState):
        super().__init__(root.xmlui, root._element)

    # XML操作
    # *************************************************************************
    # Elmentを複製して取り出す
    def duplicate(self, id:str) -> XUState:
        return XUState(self.xmlui, copy.deepcopy(self.find_by_id(id)._element))

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
    def __init__(self, screen_w:int, screen_h:int):
        # rootを作って自分自身に設定
        root = Element("root")
        root.attrib["id"] = "root"
        super().__init__(self, root)

        # ウインドウサイズを記憶
        self.screen_w = screen_w
        self.screen_h = screen_h

        # キャッシュ
        self._parent_cache:dict[Element, XUState] = {}  # dict[child] = parent_state

        # 入力
        self.event = XUEvent(True)  # 唯一のactiveとする

        # 処理関数の登録(dict[グループ][タグ名]())
        self._draw_funcs:dict[str, dict[str, Callable[[XUState, XUEvent], str|None]]] = {}

        # XMLテンプレート置き場
        self._templates:dict[str, XMLUI_Template] = {}

        # デバッグ用
        self.debug = XMLUI_Debug(self)

        # root
        self.base = XUState(self, Element("base")).set_attr("id", "base")
        self.over = XUState(self, Element("oevr")).set_attr("id", "over")
        self.add_child(self.base)  # 普通に使うもの
        self.add_child(self.over)  # 上に強制で出す物

    # template操作
    # *************************************************************************
    def set_template(self, template:XMLUI_Template, template_name:str):
        self._templates[template_name] = template

    def template_fromfile(self, template_filename:str, template_name:str):
        self.set_template(XMLUI_Template._fromfile(self, template_filename), template_name)

    def template_fromstring(self, template_str:str, template_name:str):
        self.set_template(XMLUI_Template._fromstring(self, template_str), template_name)

    def remove_template(self, template_name:str):
        del self._templates[template_name]

    # 更新用
    # *************************************************************************
    # 兄弟を先に取得するイテレータ
    def _rec_get_draw_targets(self, element:Element):
        # 兄弟を先に取得する
        for child in element:
            yield XUState(self, child)
        # 兄弟の後に子
        for child in element:
            yield from self._rec_get_draw_targets(child)

    def draw(self, draw_group:str|list[str]=[]):
        # デフォルトグループを入れておく
        draw_group = [""] + ([draw_group] if isinstance(draw_group, str) else draw_group)

        # (入力)イベントの更新
        self.event.update()

        # 描画対象を取得(子を先に処理する)
        draw_targets:list[XUState] = list(self._rec_get_draw_targets(self._element))

        # ActiveStateの取得。Active=最後、なので最後から確認
        self.active_states:list[XUState] = []
        for event in reversed([state for state in draw_targets if state.use_event and state.enable]):
            self.active_states.append(event)  # イベントを使うstateを回収
            if event.use_event == XUEvent.ABSORBER:  # イベント通知終端
                break

        # 親情報の更新
        self._parent_cache = {c:XUState(self, p) for p in self._element.iter() for c in p}

        # 更新処理
        for state in draw_targets:
            # active/inactiveどちらのeventを使うか決定
            event = copy.copy(self.event) if state in self.active_states else XUEvent()

            # やっぱりinitialize情報がどこかに欲しい
            event.on_init = state.update_count == 0

            # 更新処理
            state.set_attr("update_count", state.update_count+1)  # 1スタート(0は初期化時)
            self.draw_element(draw_group, state.tag, state, event)

        # デバッグ
        if self.debug.is_lib_debug:
            self.debug.update()

    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def draw_element(self, draw_group:list[str], tag_name:str, state:XUState, event:XUEvent):
        # 登録済みの関数だけ実行
        for group_name in draw_group:  # 指定したグループのみ描画

            # 登録タグごとに関数呼び出し
            if tag_name in self._draw_funcs[group_name]:

                # 登録されている関数を実行。戻り値はイベント
                result = self._draw_funcs[group_name][tag_name](state, event)
                if result is not None:
                    self.on(result)

    # 処理登録
    # *************************************************************************
    def set_drawfunc(self, tag_name:str, func:Callable[[XUState,XUEvent], str|None], group_name:str=""):
        # 初回は辞書を作成
        if group_name not in self._draw_funcs:
            self._draw_funcs[group_name] = {}
        self._draw_funcs[group_name][tag_name] = func

    def remove_drawfunc(self, group_name:str):
        del self._draw_funcs[group_name]

    # イベント
    # *************************************************************************
    # イベントを記録する。Trg処理は内部で行っているので現在の状態を入れる
    def on(self, event_name:str):
        self.event._on(event_name)

    # イベントが発生していればopenする。すでに開いているチェック付き
    def open_by_event(self, event_names:list[str]|str, template_name:str, id:str, id_alias:str|None=None) -> XUState|None:
        if isinstance(event_names, str):
            event_names = [event_names]  # 配列で統一
        for event_name in event_names:
            if event_name in self.event.trg:
                return self.base.open(template_name, id, id_alias)
        return None

    # override
    def open(self, template_name:str, id:str, id_alias:str|None=None) -> XUState:
        return self.base.open(template_name, id, id_alias)

    # over側で開く
    def popup(self, template_name:str, id:str, id_alias:str|None=None) -> XUState:
        return self.over.open(template_name, id, id_alias)

# ユーティリティークラス
# #############################################################################
# 基本は必要な情報をツリーでぶら下げる
# Treeが不要ならたぶんXUStateで事足りる
class _XUUtilBase(XUState):
    def __init__(self, state, root_tag:str):
        super().__init__(state.xmlui, state._element)

        # 自前設定が無ければabsorberにしておく
        if self.use_event == XUEvent.NONE:
            self.set_attr("use_event", XUEvent.ABSORBER)

        # UtilBase用ルートの作成(状態保存先)
        if state.exists_tag(root_tag):
            self._util_root = state.find_by_tag(root_tag)
            self._util_root.clear_children()  # 綺麗にして構築し直す
        else:
            self._util_root = XUState(state.xmlui, Element(root_tag))
            state.add_child(self._util_root)


# テキスト系
# *****************************************************************************
# 半角を全角に変換
_from_hanakaku = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_to_zenkaku = "０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
_from_hanakaku += " !\"#$%&'()*+,-./:;<=>?@[]^_`{|}~"  # 半角記号を追加
_to_zenkaku += "　！＂＃＄％＆＇（）＊＋，－．／：；＜＝＞？＠［］＾＿｀｛｜｝～"  # 全角記号を追加
_hankaku_zenkaku_dict = str.maketrans(_from_hanakaku, _to_zenkaku)

# テキスト基底
class XUTextBase(str):
    SEPARATE_REGEXP = r"\\n"  # 改行に変換する正規表現

    # 文字列中の半角を全角に変換する
    @classmethod
    def convert_zenkaku(cls, hankaku:str) -> str:
        return unicodedata.normalize("NFKC", hankaku).translate(_hankaku_zenkaku_dict)

    # 初期化
    # -----------------------------------------------------
    def __new__(cls, text:str, wrap:int=4096) -> Self:
        wrap = max(wrap, 1)   # 0だと無限になってしまうので最低1を入れておく

        # 改行,wrap区切りにする(\n)
        # -----------------------------------------------------
        # 改行を\nに統一して全角化
        tmp_text = "\n".join([line for line in text.splitlines()])  # XMLの改行テキストを前後を削って結合
        tmp_text = re.sub(cls.SEPARATE_REGEXP, "\n", tmp_text)  # \nという文字列を改行コードに
        tmp_text = cls.convert_zenkaku(tmp_text)  # 全角化

        # 各行に分解し、その行をさらにwrapで分解する
        lines =  sum([[line[i:i+wrap] for i in  range(0, len(line), wrap)] for line in tmp_text.splitlines()], [])

        # 結合して保存
        return super().__new__(cls, "\n".join(lines))

    # 置き換えパラメータの抜き出し
    @classmethod
    def find_params(cls, text) -> set[str]:
        return set(re.findall(r"{(\S+?)}", text))

    @classmethod
    def mkdict_params(cls, text, all_params:dict[str,Any]) -> dict[str,Any]:
        out:dict[str,Any] = {}
        for param in set(re.findall(r"{(\S+?)}", text)):
            out[param] = all_params[param]
        return out

    @classmethod
    def format_dict(cls, text, all_params:dict[str,Any]) -> str:
        return text.format(**cls.mkdict_params(text, all_params))

# アニメーションテキスト
class XUTextAnim:
    TEXT_COUNT_ATTR="_xmlui_text_count"

    _state:XUState  # このテキストを管理するEelement

    def __init__(self, state:XUState, text_base:str):
        self._text_base = text_base
        self._state = state

    # 表示カウンタ操作
    # -----------------------------------------------------
    # 現在の表示文字数
    @property
    def draw_count(self) -> float:
        return float(self._state.attr_float(self.TEXT_COUNT_ATTR, 0))

    @draw_count.setter
    def draw_count(self, count:float) -> float:
        self._state.set_attr(self.TEXT_COUNT_ATTR, count)
        return count

    # アニメーション用
    # -----------------------------------------------------
    # draw_countまでの文字列を改行分割。スライスじゃないのは改行を数えないため
    @classmethod
    def _limitstr(cls, tmp_text, text_count:float) -> str:
        limit = math.ceil(text_count)
        # まずlimitまで縮める
        for i,c in enumerate(tmp_text):
            if (limit := limit if ord(c) < 0x20 else limit-1) < 0:  # 改行は数えない
                tmp_text = tmp_text[:i]
                break
        return tmp_text

    # 改行を抜いた文字数よりカウントが大きくなった
    @property
    def is_finish(self) -> bool:
        return self.draw_count >= self.length

    @property
    def text(self) -> str:
        return self._limitstr(self._text_base, self.draw_count)

    # 改行を抜いた文字数(＝アニメーション数)取得
    @property
    def length(self) -> int:
        return len(re.sub("\n|\0", "", self._text_base))

class XUTextPage(_XUUtilBase):
    PAGE_REGEXP = r"\\p"  # 改行に変換する正規表現

    ROOT_TAG= "_xmlui_text_root"
    PAGE_NO_ATTR="_xmlui_page_no"

    def __init__(self, state:XUState, page_line_num:int, wrap:int=4096):
        super().__init__(state, self.ROOT_TAG)
        self.page_line_num = page_line_num
        self.wrap = wrap

        self.pages:list[list[str]] = self.split_page_lines(state.text, page_line_num, wrap)

    # ページ分解。行ごと
    @classmethod
    def split_page_lines(cls, text, page_line_num:int, wrap:int) -> list[list[str]]:
        # 手動ページ分解。文字列中の\pをページ区切りとして扱う
        tmp_text = re.sub(cls.PAGE_REGEXP, "\0", text)  # \nという文字列をNullに
        manual_pages = [XUTextBase(page_text, wrap) for page_text in tmp_text.split("\0")]  # ページごとにXUTextBase

        # 行数で自動ページ分解
        out:list[list[str]] = []
        for text_base in manual_pages:
            lines:list[str] = []
            for line in text_base.splitlines():
                lines.append(line)
                if len(lines) >= page_line_num:
                    out.append(lines)
                    lines = []
            if lines:  # 最後の残り
                out.append(lines)
        return out

    # ページ分解。1ページ分のテキストごと
    @classmethod
    def split_page_texts(cls, text, page_line_num:int, wrap:int) -> list[str]:
        return ["\n".join(page_lines) for page_lines in cls.split_page_lines(text, page_line_num, wrap)]

    # ページ操作
    # -----------------------------------------------------
    # 現在ページ
    @property
    def page_no(self) -> int:
        return self._util_root.attr_int(self.PAGE_NO_ATTR, 0)

    # ページ設定
    @page_no.setter
    def page_no(self, no:int=0) -> Self:
        # ページを切り替えたときはカウンタをリセット
        if self.page_no != no:
            self.anim.draw_count = 0
        self._util_root.set_attr(self.PAGE_NO_ATTR, no)
        return self

    # ページテキスト
    # -----------------------------------------------------
    @property
    def anim(self):
        return XUTextAnim(self, self.page_text)

    @property
    def page_text(self) -> str:
        return "\n".join(self.pages[self.page_no])

    # 次ページがなくテキストは表示完了 = 完全に終了
    @property
    def is_finish(self):
        return not self.is_next_wait and self.anim.is_finish

    # 次ページあり
    @property
    def is_next_wait(self):
        return self.anim.is_finish and self.page_no < len(self.pages)-1

# メニュー系
# *****************************************************************************
# 選択クラス用アイテム
class XUSelectItem(XUState):
    # アイテム座標保存先
    ITEM_X_ATTR = "_xmlui_sel_item_x"
    ITEM_Y_ATTR = "_xmlui_sel_item_y"

    def __init__(self, xmlui:XMLUI, element:Element):
        super().__init__(xmlui, element)

    def set_pos(self, x:int, y:int) -> Self:
        self.set_attr([self.ITEM_X_ATTR, self.ITEM_Y_ATTR], [x, y])
        return self

    @property
    def area(self) -> XURect:
        area = super().area
        area.x += self.attr_int(self.ITEM_X_ATTR)
        area.y += self.attr_int(self.ITEM_Y_ATTR)
        return area

# グリッド情報
class XUSelectBase(_XUUtilBase):
    # クラス定数
    ROOT_TAG = "_xmlui_select_root"
    SELECTED_NO_ATTR = "_xmlui_selected_no"

    def __init__(self, state:XUState, items:list[XUSelectItem], rows:int, item_w:int, item_h:int):
        need_init = not state.exists_tag(self.ROOT_TAG)

        super().__init__(state, self.ROOT_TAG)
        self._rows = rows
        self._items = items

        # 最初だけの初期化
        if need_init:
            # タグに付いてるselected取得
            for i,item in enumerate(items):
                if item.selected:
                    self.selected_no = i
                    break

        # アイテム設定
        for i,item in enumerate(self._items):
            item.set_pos(i % rows * item_w, i // rows * item_h)
            item.set_attr("selected", i == self.selected_no)

    @property
    def selected_no(self) -> int:
        return self.attr_int(self.SELECTED_NO_ATTR, 0)
    @selected_no.setter
    def selected_no(self, no:int) -> int:
        self.set_attr(self.SELECTED_NO_ATTR, no)
        return no

    @property
    def selected_item(self) -> XUState:
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

    # __eq__だとpylanceの方認識がおかしくなるのでactionを使う
    @property
    def action(self) -> str:
        return self.selected_item.action

# グリッド選択
class XUSelectGrid(XUSelectBase):
    def __init__(self, state:XUState, item_tag:str, rows_attr:str, item_w_attr:str, item_h_attr:str):
        # 自分の直下のitemだけ回収する
        items = [XUSelectItem(state.xmlui, element) for element in state._element if element.tag == item_tag]
        item_w = state.attr_int(item_w_attr, 0)
        item_h = state.attr_int(item_h_attr, 0)
        super().__init__(state, items, state.attr_int(rows_attr, 1), item_w, item_h)

    # 入力に応じた挙動一括。変更があった場合はTrue
    def _select_by_event(self, input:set[str], left_event:str, right_event:str, up_event:str, down_event:str, x_wrap:bool, y_wrap:bool) -> bool:
        old_no = self.selected_no

        if left_event in input:
            self.next(-1, x_wrap, y_wrap)
        elif right_event in input:
            self.next(1, x_wrap, y_wrap)
        elif up_event in input:
            self.next(-self._rows, x_wrap, y_wrap)
        elif down_event in input:
            self.next(self._rows, x_wrap, y_wrap)

        return self.selected_no != old_no

    def select_by_event(self, input:set[str], left_event:str, right_event:str, up_event:str, down_event:str) -> bool:
        return self._select_by_event(input, left_event, right_event, up_event, down_event, True, True)

    def select_no_wrap(self, input:set[str], left_event:str, right_event:str, up_event:str, down_event:str) -> bool:
        return self._select_by_event(input, left_event, right_event, up_event, down_event, False, False)

# リスト選択
class XUSelectList(XUSelectBase):
    def __init__(self, state:XUState, item_tag:str, item_w_attr:str, item_h_attr:str):
        # 自分の直下のitemだけ回収する
        items = [XUSelectItem(state.xmlui, element) for element in state._element if element.tag == item_tag]
        item_w = state.attr_int(item_w_attr, 0)
        item_h = state.attr_int(item_h_attr, 0)
        rows = len(items) if item_w > item_h else 1
        super().__init__(state, items, rows, item_w, item_h)
  
    # 入力に応じた挙動一括。変更があった場合はTrue
    def _select_by_event(self, input:set[str], prev_event:str, next_event:str, wrap:bool) -> bool:
        old_no = self.selected_no

        if prev_event in input:
            self.next(-1, wrap, wrap)
        elif next_event in input:
            self.next(1, wrap, wrap)

        return self.selected_no != old_no

    def select_by_event(self, input:set[str], prev_event:str, next_event:str) -> bool:
        return self._select_by_event(input, prev_event, next_event, True)

    def select_no_wrap(self, input:set[str], prev_event:str, next_event:str) -> bool:
        return self._select_by_event(input, prev_event, next_event, False)


# ダイアル
# *****************************************************************************
# 情報管理のみ
class XUDial(_XUUtilBase):
    ROOT_TAG = "_xmlui_dial_root"
    EDIT_POS_ATTR = "edit_pos"  # 操作位置
    DIGIT_ATTR = "digits"  # 操作位置

    def __init__(self, state:XUState, digit_length:int, digit_list:str="0123456789"):
        super().__init__(state, self.ROOT_TAG)
        self.digit_length = digit_length
        self._digit_list = digit_list

        # Digitのデータを引き継ぐ
        old_digit = self._util_root.attr_str(self.DIGIT_ATTR)
        new_digit = [old_digit[i] if i < len(old_digit) else "0" for i in range(digit_length)]
        self._util_root.set_attr(self.DIGIT_ATTR, "".join(new_digit))


    @property
    def edit_pos_raw(self) -> int:
        return self._util_root.attr_int(self.EDIT_POS_ATTR)
    @property
    def edit_pos(self) -> int:
        return self.digit_length-1 - self._util_root.attr_int(self.EDIT_POS_ATTR)

    @property
    def digits(self) -> str:
        return "".join(list(reversed(self._util_root.attr_str(self.DIGIT_ATTR))))

    @property
    def zenkaku_digits(self) -> str:
        return "".join(list(reversed(XUTextBase.convert_zenkaku(self._util_root.attr_str(self.DIGIT_ATTR)))))

    # 回り込み付き操作位置の設定
    def set_editpos(self, edit_pos:int) -> Self:
        self._util_root.set_attr(self.EDIT_POS_ATTR, (edit_pos + self.digit_length) % self.digit_length)
        return self

    # 操作位置の移動
    def move_editpos(self, add:int) -> Self:
        return self.set_editpos(self.edit_pos_raw+add)

    # 指定位置のdigitを変更する
    def set_digit(self, edit_pos:int, digit:str) -> Self:
        digits = [c for c in self._util_root.attr_str(self.DIGIT_ATTR)]
        digits[edit_pos] = digit
        self._util_root.set_attr(self.DIGIT_ATTR, "".join(digits))
        return self

    # 回り込み付きdigit増減
    def add_digit(self, edit_pos:int, add:int) -> Self:
        old_digit = self._util_root.attr_str(self.DIGIT_ATTR)[edit_pos]
        new_digit = self._digit_list[(self._digit_list.find(old_digit) + len(self._digit_list) + add) % len(self._digit_list)]
        return self.set_digit(edit_pos, new_digit)

    # 入力に応じた挙動一括。変更があった場合はTrue
    def change_by_event(self, input:set[str], left_event:str, right_event:str, up_event:str, down_event:str) -> bool:
        old_digits = self.digits
        old_edit_pos = self.edit_pos_raw

        if left_event in input:
            self.move_editpos(1)
        if right_event in input:
            self.move_editpos(-1)
        if up_event in input:
            self.add_digit(self.edit_pos_raw, +1)  # digitを増やす
        if down_event in input:
            self.add_digit(self.edit_pos_raw, -1)  # digitを減らす

        return self.digits != old_digits or self.edit_pos_raw != old_edit_pos


# ウインドウサポート
# *****************************************************************************
class XUWinBase(XUState):
    # ウインドウの状態定義
    STATE_OPENING = "opening"
    STATE_OPENED = "opened"
    STATE_CLOSING = "closing"
    STATE_CLOSED = "closed"

    # 状態を保存するアトリビュート
    WIN_STATE_ATTR = "_xmlui_win_state"
    OPENING_COUNT_ATTR = "_xmlui_opening_count"
    CLOSING_COUNT_ATTR = "_xmlui_closing_count"

    # 状態管理
    # -----------------------------------------------------
    def __init__(self, state:XUState):
        super().__init__(state.xmlui, state._element)

        # ステートがなければ用意しておく
        if not self.has_attr(self.WIN_STATE_ATTR):
            self.win_state = self.STATE_OPENING

    # override。closeするときに状態をCLOSEDにする
    def close(self):
        self.win_state = self.STATE_CLOSED  # finish
        super().close()

    # XUWinBaseを使ったElementかどうか。attributeの有無でチェック
    @classmethod
    def is_win(cls, state:XUState) -> bool:
        return state.has_attr(cls.WIN_STATE_ATTR)

    # 一番近いXUWinBaseを持つ親を取得する
    @classmethod
    def find_win(cls, state:XUState) -> "XUWinBase":
        for parent in state.ancestors:
            if XUWinBase.is_win(parent):
                return XUWinBase(parent)
        raise Exception("no window found")

    # ウインドウの状態管理
    # -----------------------------------------------------
    # ウインドウの状態に応じてアニメーション用カウンタを更新する
    def update(self):
        win_state = self.attr_str(self.WIN_STATE_ATTR)
        match win_state:
            case self.STATE_OPENING:
                self.set_attr(self.OPENING_COUNT_ATTR, self.attr_int(self.OPENING_COUNT_ATTR) + 1)
            case self.STATE_CLOSING:
                self.set_attr(self.CLOSING_COUNT_ATTR, self.attr_int(self.CLOSING_COUNT_ATTR) + 1)

    # ウインドウの状態のset/get
    @property
    def win_state(self) -> str:
        return self.attr_str(self.WIN_STATE_ATTR)
    @win_state.setter
    def win_state(self, win_state:str) -> str:
        self.set_attr(self.WIN_STATE_ATTR, win_state)
        return win_state

    # opning/closingの状態管理
    # -----------------------------------------------------
    @property
    def is_opening(self):
        return self.win_state == XUWinRound.STATE_OPENING or self.win_state == XUWinRound.STATE_OPENED
    @property
    def is_closing(self):
        return self.win_state == XUWinRound.STATE_CLOSING or self.win_state == XUWinRound.STATE_CLOSED

    @property
    def opening_count(self) -> int:
        return self.attr_int(self.OPENING_COUNT_ATTR)
    @property
    def closing_count(self) -> int:
        return self.attr_int(self.CLOSING_COUNT_ATTR)

    # 子も含めてclosingにする
    def start_close(self):
        self.enable = False  # closingは実質closeなのでイベントは見ない
        self.win_state = self.STATE_CLOSING

        # 子も順次closing
        for child in self.children:
            child.enable = False  # 全ての子のイベント通知をoffに
            if XUWinBase.is_win(child):  # 子ウインドウも一緒にクローズ
                XUWinBase(child).win_state = self.STATE_CLOSING

class XUWinFrame(XUWinBase):
    # ウインドウ(ピクセル)描画
    # 0 1 2
    # 3 4 5
    # 6 7 8
    # -----------------------------------------------------
    # 枠外は-1を返す
    def _get_pattern_index(self, size:int, x:int, y:int, w:int, h:int) -> int:
        raise Exception("no implements")

    # 1,3,5,7,4のエリア(カド以外)は特に計算が必要ない
    def _get13574index(self, size:int, x:int, y:int, w:int, h:int) -> int:
        return [-1, y, -1, x, size-1, w-1-x, -1, h-1-y][self.get_area(size, x, y, w, h)]

    # どのエリアに所属するかを返す
    def get_area(self, size:int, x:int, y:int, w:int, h:int) -> int:
        if x < size:
            if y < size:
                return 0
            return 3 if y < h-size else 6
        elif x < w-size:
            if y < size:
                return 1
            return 4 if y < h-size else 7
        else:
            if y < size:
                return 2
            return 5 if y < h-size else 8

    # フレームだけバッファに書き込む。中央部分塗りつぶしは呼び出し側で行う
    def draw_frame(self, screen_buf:bytearray, pattern:list[int], screen_area:XURect, clip:XURect|None=None):
        screen_buf_w = self.xmlui.screen_w  # バッファサイズは画面幅で確定(繰り返し使うのでキャッシュ)

        # 画面外に描画しない
        screen_area = screen_area.intersect(XURect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h))

        # オフセットなので0,0～w,h
        area = screen_area.to_offset()
        clip = clip.intersect(area) if clip else area
        if clip.is_empty:
            return

        size = len(pattern)
        pat_bytes = bytes(pattern)
        rev_butes = bytes(reversed(pat_bytes))

        # 角の描画
        # ---------------------------------------------------------------------
        def _draw_shoulder(self, off_x:int, off_y:int, pattern:bytes):
           # クリップチェック
            if clip.contains(off_x, off_y):
                index = self._get_pattern_index(size, off_x, off_y, area.w, area.h)
                if index >= 0:  # 枠外チェック
                    screen_buf[(screen_area.y + off_y)*screen_buf_w + (screen_area.x + off_x)] = pattern[index]

        for y_ in range(size):
            for x_ in range(size):
                _draw_shoulder(self, x_, y_, pat_bytes)  # 左上
                _draw_shoulder(self, area.w-1-x_, y_, pat_bytes)  # 右上
                _draw_shoulder(self, x_, area.h-1-y_, rev_butes)  # 左下
                _draw_shoulder(self, area.w-1-x_, area.h-1-y_, rev_butes)  # 右下

        # bytearrayによる角以外の高速描画(patternキャッシュを作ればもっと速くなるかも)
        # ---------------------------------------------------------------------
        # 上下のライン
        line_clip = clip.inflate(-size, 0)
        if not line_clip.is_empty:
            for y_ in range(size):
                # 上
                if line_clip.contains_y(y_):
                    offset = (screen_area.y + y_)*screen_buf_w + screen_area.x
                    screen_buf[offset+line_clip.x: offset+line_clip.right()] = pat_bytes[y_:y_+1] * line_clip.w
                # 下
                if line_clip.contains_y(area.h-1-y_):
                    offset = (screen_area.bottom()-1-y_)*screen_buf_w + screen_area.x
                    screen_buf[offset+line_clip.x: offset+line_clip.right()] = rev_butes[y_:y_+1] * line_clip.w

        # 左
        left_clip = clip.intersect(XURect(0, 0, size, area.h).inflate(0, -size))
        if not left_clip.is_empty:
            for y_ in range(area.h):
                if left_clip.contains_y(y_):
                    offset = (screen_area.y + y_)*screen_buf_w + screen_area.x
                    screen_buf[offset:offset+left_clip.w] = pat_bytes[:left_clip.w]

        # 右
        right_clip = clip.intersect(XURect(area.w-size, 0, size, area.h).inflate(0, -size))
        if not right_clip.is_empty:
            for y_ in range(area.h):
                if right_clip.contains_y(y_):
                    offset = (screen_area.y + y_)*screen_buf_w + screen_area.x + area.w-size
                    screen_buf[offset:offset+right_clip.w] = rev_butes[:right_clip.w]

class XUWinRound(XUWinFrame):
    def _get_veclen(self, x:int, y:int, org_x:int, org_y:int) -> int:
        return math.ceil(math.sqrt((x-org_x)**2 + (y-org_y)**2))

    # override
    def _get_pattern_index(self, size:int, x:int, y:int, w:int, h:int) -> int:
        match self.get_area(size, x, y, w, h):
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
        return self._get13574index(size, x, y, w, h)

class XUWinRect(XUWinFrame):
    # override
    def _get_pattern_index(self, size:int, x:int, y:int, w:int, h:int) -> int:
        match self.get_area(size, x, y, w, h):
            case 0:
                return y if x > y else x
            case 2:
                return y if w-1-x > y else w-1-x
            case 6:
                y = h-1-y
                return y if x > y else size-1-x
            case 8:
                x = w-1-x
                y = h-1-y
                return y if x > y else size-1-x
        return self._get13574index(size, x, y, w, h)
