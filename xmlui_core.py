# XMLを使うよ
import xml.etree.ElementTree
from xml.etree.ElementTree import Element

from typing import Callable,Any,Self  # 型を使うよ
import unicodedata  # 全角化用
import re, math, copy  # その他よく使う奴


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

    def center_x(self, width:int=0) -> int:
        return self.x + (self.w-width)//2

    def center_y(self, height:int=0) -> int:
        return self.y + (self.h-height)//2

    def __repr__(self) -> str:
        return f"RECT({self.x}, {self.y}, {self.w}, {self.h})"


# イベント管理用
class UI_EVENT:
    def __init__(self, init_active=False):
        self.active = init_active  # 現在アクティブかどうか
        self._receive:set[str] = set([])  # 次の状態受付
        self._input:set[str] = set([])
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


# UIパーツの状態管理ラッパー
class UI_STATE:
    def __init__(self, xmlui:'XMLUI', element:Element):
        self.xmlui = xmlui  # ライブラリへのIF
        self._element = element  # 自身のElement

    def disableEvent(self) -> Self:
        return self.setAttr("use_event", False)

    # UI_STATEは都度使い捨てなので、対象となるElementで比較する
    def __eq__(self, other) -> bool:
        return other._element is self._element if isinstance(other, UI_STATE) else False

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

    def setAttr(self, key:str|list[str], value: Any) -> Self:
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

    def setText(self, text:str) -> 'UI_STATE':
        self._element.text = text
        return self

    # その他
    # *************************************************************************
    @property
    def tag(self) -> str:
        return self._element.tag

    @property
    def area(self) -> UI_RECT:
        return UI_RECT(self.area_x, self.area_y, self.area_w, self.area_h)

    def setPos(self, x:int, y:int) -> Self:
        return self.setAttr(["x", "y"], [x, y])

    def setAbsPos(self, x:int, y:int) -> Self:
        return self.setAttr(["abs_x", "abs_y"], [x, y])

    def setEnable(self, enable:bool) -> Self:
        return self.setAttr("enable", enable)

    def setVisible(self, visible:bool) -> Self:
        return self.setAttr("visible", visible)

    # ツリー操作用
    # *************************************************************************
    def addChild(self, child:'UI_STATE'):  # selfとchildどっちが返るかややこしいのでNone
        self._element.append(child._element)

    def remove(self):  # removeの後なにかすることはないのでNone
        # 処理対象から外れるように
        self.setAttr("enable", False)
        if self.parent:  # 親から外す
            self.parent._element.remove(self._element)

    def findByID(self, id:str) -> 'UI_STATE':
        for element in self._element.iter():
            if element.attrib.get("id") == id:
                return UI_STATE(self.xmlui, element)
        raise Exception(f"ID '{id}' not found in '{self.tag}' and children")

    def findByTagAll(self, tag:str) -> list['UI_STATE']:
        return [UI_STATE(self.xmlui, element) for element in self._element.iter() if element.tag == tag]

    def findByTag(self, tag:str) -> 'UI_STATE':
        elements:list[UI_STATE] = self.findByTagAll(tag)
        if elements:
            return elements[0]
        raise Exception(f"Tag '{tag}' not found in '{self.tag}' and children")

    # 下階層ではなく、上(root)に向かって探索する
    def findByTagR(self, tag:str) -> 'UI_STATE':
        parent = self.parent
        while(parent):
            if parent.tag == tag:
                return parent
            parent = parent.parent
        raise Exception(f"Tag '{tag}' not found in parents")

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
    def open(self, template:'XMLUI|UI_STATE', id:str, alias:str|None=None) -> 'UI_STATE':
        src = template.root if isinstance(template, XMLUI) else template

        try:
            return self.findByID(id if alias is None else alias)  # すでにいたらなにもしない
        except:
            # eventを有効にして追加する
            opend  = self.xmlui.duplicate(src.findByID(id))
            # aliasでtagとidをリネーム
            if alias is not None:
                opend.setAttr("id", alias)
                opend._element.tag = alias
            self.addChild(opend.setAttr("use_event", True))
            return opend

    def close(self, id:str|None=None):  # closeの後なにもしないのでNone
        if id is not None:
            state = self.xmlui.root.findByID(id)
            state.remove()
        else:
            self.remove()

    # デバッグ用
    # *************************************************************************
    def strTree(self, indent:str="  ", pre:str="") -> str:
        out = pre + self.tag
        out += f": {self.id}" if self.id else ""
        out += f" {self.marker}"
        for element in self._element:
            out += "\n" + UI_STATE(self.xmlui, element).strTree(indent, pre+indent)
        return out

    # xmluiで特別な意味を持つアトリビュート一覧
    # わかりやすく全てプロパティを用意しておく(デフォルト値も省略せず書く)
    # 面倒でも頑張って書く
    # *************************************************************************
    @property
    def id(self) -> str:  # ID。xmlではかぶらないように(精神論)
        return self.attrStr("id", "")

    @property
    def value(self) -> str:  # 汎用値取得
        return self.attrStr("value", "")

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
    def update_count(self) -> int:  # updateが行われた回数
        return self.attrInt("update_count", 0)

    @property
    def use_event(self) -> bool:  # eventを使うかどうか
        return self.attrBool("use_event", False)

    @property
    def selected(self) -> int:  # 選択されている
        return self.attrBool("selected", False)

    @property
    def layer(self) -> int:  # 描画レイヤ
        return self.attrInt("layer", 0)

    @property
    def marker(self) -> str:  # デバッグ用
        return self.attrStr("marker", "")


# XMLでUIライブラリ本体
# #############################################################################
class XMLUI:
    # デバッグ用フラグ
    debug = True

    # 初期化
    # *************************************************************************
    # ファイルから読み込み
    @classmethod
    def createFromFile(cls, fileName:str, root_tag:str|None=None) -> 'XMLUI':
        with open(fileName, "r", encoding="utf8") as f:
            return cls.createFromString(f.read())

    # リソースから読み込み
    @classmethod
    def createFromString(cls, xml_data:str, root_tag:str|None=None) -> 'XMLUI':
        return XMLUI(xml.etree.ElementTree.fromstring(xml_data))

    # ワーカーの作成
    @classmethod
    def createWorker(cls, root_tag:str) -> 'XMLUI':
        return XMLUI(Element(root_tag))

    # 初期化。<xmlui>を持つXMLを突っ込む
    def __init__(self, dom:xml.etree.ElementTree.Element, root_tag:str|None=None):
        # 入力
        self._event = UI_EVENT(True)  # 唯一のactiveとする
        self._input_lists:dict[str, list[int]] = {}

        # 処理関数の登録
        self._update_funcs:dict[str,Callable[[UI_STATE,UI_EVENT], None]] = {}
        self._draw_funcs:dict[str,Callable[[UI_STATE,UI_EVENT], None]] = {}

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

    def close(self, id:str):
        self.root.findByID(id).close()


    # 更新用
    # *************************************************************************
    def _getUpdateTargets(self, state:UI_STATE):
        if state.enable:
            yield state
            # enableの子だけ回収(disableの子は削除)
            for child in state._element:
                yield from self._getUpdateTargets(UI_STATE(self, child))

    def update(self):
        # (入力)イベントの更新
        self._event.update()

        # 更新対象を取得
        update_targets = list(self._getUpdateTargets(self.root))

        # イベント発生対象は表示物のみ
        event_targets = [state for state in update_targets if state.visible and state.use_event]
        active_state = event_targets[-1] if event_targets else None  # Active=最後

        # 更新処理
        for state in update_targets:
            if state.enable:  # update中にdisable(remove)になる場合があるので毎回チェック
                state.setAttr("update_count", state.update_count+1)  # 1スタート(0は初期化時)
                self.updateElement(state.tag, state, self._event if state == active_state else UI_EVENT())

    # 描画用
    # *************************************************************************
    def _getDrawTargets(self, state:UI_STATE):
        if state.enable and state.visible and state.update_count>0:  # count==0はUpdateで追加されたばかりのもの(未Update)
            yield state
            # visibleの子だけ回収(invisibleの子は削除)
            for child in state._element:
                yield from self._getDrawTargets(UI_STATE(self, child))

    def draw(self):
        # 描画対象を取得
        draw_targets = list(self._getDrawTargets(self.root))

        # イベント発生対象は表示物のみ
        event_targets = [state for state in draw_targets if state.use_event]
        active_state = event_targets[-1] if event_targets else None  # Active=最後

        # 更新処理
        for state in draw_targets:
            # 親を持たないElementは更新不要
            if state.parent is None:
                continue

            # エリア更新。absがあれば絶対座標、なければ親からのオフセット
            state.setAttr("area_x", state.abs_x if state.hasAttr("abs_x") else state.x + state.parent.area_x)
            state.setAttr("area_y", state.abs_y if state.hasAttr("abs_y") else state.y + state.parent.area_y)
            state.setAttr("area_w", state.attrInt("w", state.parent.area_w))
            state.setAttr("area_h", state.attrInt("h", state.parent.area_h))

            if not state.hasAttr("layer") and state.parent:
                state.setAttr("layer", state.parent.layer)  # 自身がlayerを持っていなければ親から引き継ぐ

        # 描画処理
        for state in sorted(draw_targets, key=lambda state: state.layer):
            self.drawElement(state.tag, state, self._event if state == active_state else UI_EVENT())

    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def updateElement(self, tag_name:str, state:UI_STATE, event:UI_EVENT):
        # 登録済みの関数だけ実行
        if tag_name in self._update_funcs:
            self._update_funcs[tag_name](state, event)

    def drawElement(self, tag_name:str, state:UI_STATE, event:UI_EVENT):
        # 登録済みの関数だけ実行
        if tag_name in self._draw_funcs:
            self._draw_funcs[tag_name](state, event)


    # 処理登録
    # *************************************************************************
    def setUpdateFunc(self, tag_name:str, func:Callable[[UI_STATE,UI_EVENT], None]):
        self._update_funcs[tag_name] = func

    def setDrawFunc(self, tag_name:str, func:Callable[[UI_STATE,UI_EVENT], None]):
        self._draw_funcs[tag_name] = func

    # デコレータを用意
    def update_func(self, tag_name:str):
        def wrapper(update_func:Callable[[UI_STATE,UI_EVENT], None]):
            self.setUpdateFunc(tag_name, update_func)
        return wrapper

    def draw_func(self, tag_name:str):
        def wrapper(draw_func:Callable[[UI_STATE,UI_EVENT], None]):
            self.setDrawFunc(tag_name, draw_func)
        return wrapper


    # 入力
    # *************************************************************************
    # イベント入力
    def on(self, input:str):
        self._event.on(input)

    # キー入力
    def setInputList(self, input_type:str, list:list[int]):
        self._input_lists[input_type] = list

    def checkInput(self, check:str, check_func:Callable[[int], bool]) -> bool:
        for button in self._input_lists[check]:
            if check_func(button):
                return True
        return False

    # 登録キー入力を全部調べて片っ端からイベントに登録
    def checkInputAndOn(self, check_func:Callable[[int], bool]):
        for key in self._input_lists:
            if self.checkInput(key, check_func):
                self._event.on(key)


# ユーティリティークラス
# #############################################################################
# StateベースのUtility用基底クラス
# ---------------------------------------------------------
# ツリーでぶら下げる(rootの追加)
class _UI_UTIL_TREE(UI_STATE):
    # 親になければ新規で作って追加する。あればそれを利用する
    # 新規作成時Trueを返す
    def __init__(self, parent:UI_STATE, child_root_tag:str, allow_create:bool=True):
        try:
            # すでに存在するElementを回収
            exists = parent.findByTag(child_root_tag)
            super().__init__(parent.xmlui, exists._element)
            self._need_init = False  # 初期化は不要
        except Exception as e:
            # 作成が許可されていないときは例外
            if not allow_create:
                raise e

            # 新規作成
            super().__init__(parent.xmlui, Element(child_root_tag))
            parent.addChild(self)
            self._need_init = True  # 初期化が必要

# Stateをそのまま利用する(attribute中心操作)
class _UI_UTIL(UI_STATE):
    def __init__(self, state:UI_STATE):
        super().__init__(state.xmlui, state._element)

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
class UI_PAGE_RO(_UI_UTIL_TREE):
    # クラス定数
    PAGE_TAG ="_xmlui_page"
    SEPARATE_REGEXP = r"\\n"  # 改行に変換する正規表現

    DRAW_COUNT_ATTR = "draw_count"  # 文字アニメ用
    PAGE_NO_ATTR = "page_no"  # ページ管理用

    def __init__(self, parent: UI_STATE, allow_create:bool=False):
        super().__init__(parent, "_xmlui_page_root", allow_create)

    # ページ関係
    # -----------------------------------------------------
   # 現在ページ
    @property
    def page_no(self) -> int:
        return min(max(self.attrInt(self.PAGE_NO_ATTR, 0), 0), self.page_max)

    # ページの最大数
    @property
    def page_max(self) -> int:
        return len(self.findByTagAll(self.PAGE_TAG))

    # ページ全部表示済みかどうか
    @property
    def is_end_page(self) -> bool:
        return self.page_no+1 >= self.page_max  # 1オリジンで数える

    # ページタグリスト
    @property
    def pages(self) -> list[UI_STATE]:
        return self.findByTagAll(self.PAGE_TAG)

    # ページテキスト
    @property
    def page_text(self) -> str:
        return self._limitStr(self.pages[self.page_no].text, self.draw_count)

    # アニメーション用
    # -----------------------------------------------------
    # draw_countまでの文字列を改行分割
    def _limitStr(self, tmp_text, draw_count:float) -> str:
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
        return self.attrFloat(self.DRAW_COUNT_ATTR)

    # 現在ページを表示しきったかどうか
    @property
    def is_finish(self) -> bool:
        return math.ceil(self.draw_count) >= len(self.page_text.replace("\n", ""))

    # ユーティリティ
    # -----------------------------------------------------
    # 文字列中の半角を全角に変換する
    @classmethod
    def convertZenkaku(cls, hankaku:str) -> str:
        return unicodedata.normalize("NFKC", hankaku).translate(_hankaku_zenkaku_dict)

# アニメーションテキストページ管理
class UI_PAGE(UI_PAGE_RO):
    def __init__(self, parent:UI_STATE, text:str, page_line_num:int, wrap:int=4096):
        super().__init__(parent, True)
        if self._need_init:
            # 改行を\nに統一して全角化
            tmp_text = self.convertZenkaku(re.sub(self.SEPARATE_REGEXP, "\n", text).strip())

            # 各行に分解し、その行をさらにwrapで分解する
            wrap = max(1, wrap)  # 0だと無限になってしまうので最低1を入れておく
            lines =  sum([[line[i:i+wrap] for i in  range(0, len(line), wrap)] for line in tmp_text.splitlines()], [])

            # ページごとにElementを追加
            for i in range(0, len(lines), page_line_num):
                page_text = "\n".join(lines[i:i+page_line_num])  # 改行を\nにして全部文字列に
                page = UI_STATE(self.xmlui, Element(self.PAGE_TAG))
                page.setText(page_text)
                self.addChild(page)

    # ページ関係
    # -----------------------------------------------------
    # page_noの操作
    def nextPage(self, add:int=1) -> Self:
        self.reset()  # ページが変わればまた最初から
        self.setAttr(self.PAGE_NO_ATTR, self.page_no+1)
        return self

    # アニメーション用
    # -----------------------------------------------------
    # 表示カウンタを進める
    def next(self, add:float=1) -> Self:
        self.setAttr(self.DRAW_COUNT_ATTR, self.draw_count+add)
        return self

    # 表示カウンタのリセット
    def reset(self) -> Self:
        self.setAttr(self.DRAW_COUNT_ATTR, 0)
        return self

    # 一気に表示
    def finish(self) -> Self:
        self.setAttr(self.DRAW_COUNT_ATTR, len(self.page_text))
        return self

    # イベントアクション
    # -----------------------------------------------------
    # 状況に応じた決定ボタン操作を行う
    def action(self):
        # ページ中に残りがあるなら一気に表示
        if not self.is_finish:
            self.finish()
        # ページが残っていたら次のページへ
        elif not self.is_end_page:
            self.nextPage()


# メニュー系
# ---------------------------------------------------------
# グリッド情報
class _UI_SELECT_BASE(_UI_UTIL):
    def __init__(self, state:UI_STATE, grid:list[list[UI_STATE]]):
        super().__init__(state)
        self._grid = grid

        # タグにselected=Trueがあればそれを使う。無ければgrid[0][0]を選択
        try:
            self.selected_item
        except:
            self.select(0, 0)  # 最初の選択

    # GRID用
    @classmethod
    def findGridByTag(cls, state:UI_STATE, tag_group:str, tag_item:str) -> list[list['UI_STATE']]:
        return [group.findByTagAll(tag_item) for group in state.findByTagAll(tag_group)]

    # 転置(Transpose)GRID
    @classmethod
    def findGridByTagT(cls, state:UI_STATE, tag_group:str, tag_item:str) -> list[list['UI_STATE']]:
        grid = cls.findGridByTag(state, tag_group, tag_item)
        grid = [[grid[y][x] for y in range(len(grid))] for x in range(len(grid[0]))]  # 転置
        return grid

    # グリッド各アイテムの座標設定
    def arrangeItems(self, w:int, h:int) -> Self:
        for y,group in enumerate(self._grid):
            for x,item in enumerate(group):
                item.setAttr(["x", "y"], (x*w, y*h))
        return self


    # 範囲限定付き座標設定
    def select(self, x:int, y:int, x_wrap:bool=False, y_wrap:bool=False) -> Self:
        cur_x = (x + self.grid_w) % self.grid_w if x_wrap else max(min(x, self.grid_w-1), 0)
        cur_y = (y + self.grid_h) % self.grid_h if y_wrap else max(min(y, self.grid_h-1), 0)
        for y, group in enumerate(self._grid):
            for x, item in enumerate(group):
                item.setAttr("selected", x == cur_x and y == cur_y)
        return self

    @property
    def selected_item(self) -> UI_STATE:
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
class UI_SELECT_GRID(_UI_SELECT_BASE):
    def __init__(self, state:UI_STATE, tag_group:str, tag_item:str):
        super().__init__(state, self.findGridByTag(state, tag_group, tag_item))

    # 入力に応じた挙動一括
    def selectByEvent(self, input:set[str], leftEvent:str, rightEvent:str, upEvent:str, downEvent:str, x_wrap:bool=False, y_wrap:bool=False) -> Self:
        if leftEvent in input:
            self.select(self.cur_x-1, self.cur_y, x_wrap)
        elif rightEvent in input:
            self.select(self.cur_x+1, self.cur_y, x_wrap)
        elif upEvent in input:
            self.select(self.cur_x, self.cur_y-1, False, y_wrap)
        elif downEvent in input:
            self.select(self.cur_x, self.cur_y+1, False, y_wrap)
        return self

# リスト選択
class UI_SELECT_LIST(_UI_SELECT_BASE):
    # 縦に入れる
    def __init__(self, state:UI_STATE, tag_item:str):
        super().__init__(state, self.findGridByTagT(state, state.tag, tag_item))

    # 入力に応じた挙動一括。選択リストは通常上下ラップする
    def selectByEvent(self, input:set[str], upEvent:str, downEvent:str, y_wrap:bool=True) -> Self:
        if upEvent in input:
            self.select(0, self.cur_y-1, False, y_wrap)
        elif downEvent in input:
            self.select(0, self.cur_y+1, False, y_wrap)
        return self


# ダイアル
# ---------------------------------------------------------
# 情報管理のみ
class UI_DIAL_RO(_UI_UTIL_TREE):
    DIGIT_TAG = "_xmlui_dial_digit"

    EDIT_POS_ATTR = "edit_pos"  # 操作位置

    def __init__(self, parent:UI_STATE, allow_create:bool=False):
        super().__init__(parent, "_xmlui_dial_root", allow_create)

    @property
    def edit_pos(self) -> int:
        return self.attrInt(self.EDIT_POS_ATTR)

    @property
    def digits(self) -> list[str]:
        return [state.text for state in self.findByTagAll(self.DIGIT_TAG)]

    @property
    def zenkakuDigits(self) -> list[str]:
        return [UI_PAGE_RO.convertZenkaku(digit) for digit in self.digits]

    @property
    def number(self) -> int:
        return int("".join(reversed(self.digits)))

# ダイアル操作
class UI_DIAL(UI_DIAL_RO):
    def __init__(self, parent:UI_STATE, digit_length:int, digit_list:str="0123456789"):
        super().__init__(parent, True)
        if self._need_init:
            # 初期値は最小埋め
            for i in range(digit_length):
                digit = UI_STATE(self.xmlui, Element(self.DIGIT_TAG))
                digit.setText(digit_list[0])
                self.addChild(digit)

        self._digit_list = digit_list

    # 回り込み付き操作位置の設定
    def setEditPos(self, edit_pos:int) -> Self:
        self.setAttr(self.EDIT_POS_ATTR, (edit_pos+len(self.digits))%len(self.digits))
        return self

    # 操作位置の移動
    def moveEditPos(self, add:int) -> Self:
        return self.setEditPos(self.edit_pos+add)

    # 指定位置のdigitを変更する
    def setDigit(self, edit_pos:int, digit:str) -> Self:
        state = self.findByTagAll(self.DIGIT_TAG)[edit_pos]
        state.setText(digit)
        return self

    # 回り込み付きdigit増減
    def addDigit(self, edit_pos:int, add:int) -> Self:
        old_digit = self.digits[edit_pos]
        new_digit = self._digit_list[(self._digit_list.find(old_digit)+len(self._digit_list)+add) % len(self._digit_list)]
        return self.setDigit(edit_pos, new_digit)

    # 入力に応じた挙動一括
    def changeByEvent(self, input:set[str], leftEvent:str, rightEvent:str, upEvent:str, downEvent:str) -> Self:
        if leftEvent in input:
            self.moveEditPos(1)
        if rightEvent in input:
            self.moveEditPos(-1)
        if upEvent in input:
            self.addDigit(self.edit_pos, +1)  # digitを増やす
        if downEvent in input:
            self.addDigit(self.edit_pos, -1)  # digitを減らす
        return self


# ウインドウサポート
# ---------------------------------------------------------
class UI_WIN_BASE:
    # 0 1 2
    # 3 4 5
    # 6 7 8
    def __init__(self, pattern:list[int], screen_w:int, screen_h:int, getPatternIndexFunc:Callable[[int,int,int,int], int]):
        self._patterns = [pattern.copy() for i in range(9)]
        self.screen_w, self.screen_h = screen_w, screen_h
        self._getPatIdxFunc = getPatternIndexFunc  # 枠外は-1を返す

        # クリッピングエリア
        self.clip = UI_RECT(0, 0, screen_w, screen_h)

    # 1,3,5,7,4のエリア(カド以外)は特に計算が必要ない
    def _get13574Index(self, x:int, y:int, w:int, h:int) -> int:
        return [-1, y, -1, x, self.pattern_size-1, w-1-x, -1, h-1-y][self.getArea(x, y, w, h)]

    # どのエリアに所属するかを返す
    def getArea(self, x:int, y:int, w:int, h:int) -> int:
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
    def setShadow(self, index:int, shadow:list[int]) -> Self:
        for i,color in enumerate(shadow):
            self._patterns[0][index+i] = color
            self._patterns[1][index+i] = color
            self._patterns[3][index+i] = color
        return self

    # バッファに書き込む
    def drawBuf(self, x:int, y:int, w:int, h:int, screen_buf):
        for y_ in range(self.clip.y, min(self.clip.h, h)):
            for x_ in range(self.clip.x, min(self.clip.w, w)):
                index = self._getPatIdxFunc(x_, y_, w, h)
                if index >= 0:  # 枠外チェック
                    color = self._patterns[self.getArea(x_, y_, w, h)][index]
                    if color == -1:  # 透明チェック
                        continue
                    screen_buf[(y+y_)*self.screen_w + (x+x_)] = color

    # パターン長
    @property
    def pattern_size(self) -> int:
        return len(self._patterns[0])

class UI_WIN_ROUND(UI_WIN_BASE):
    def __init__(self, pattern:list[int], screen_w:int, screen_h:int):
        super().__init__(pattern, screen_w, screen_h, self._getPatternIndex)

    def _getVecLen(self, x:int, y:int, org_x:int, org_y:int) -> int:
        return math.ceil(math.sqrt((x-org_x)**2 + (y-org_y)**2))

    def _getPatternIndex(self, x:int, y:int, w:int, h:int) -> int:
        size = self.pattern_size
        area = self.getArea(x, y, w, h)
        if area == 0:
            l = size-1-self._getVecLen(x, y, size-1, size-1)
            return l if l < size else -1
        elif area == 2:
            l = size-1-self._getVecLen(x, y, w-size, size-1)
            return l if l < size else -1
        elif area == 6:
            l = size-1-self._getVecLen(x, y, size-1, h-size)
            return l if l < size else -1
        elif area == 8:
            l = size-1-self._getVecLen(x, y, w-size, h-size)
            return l if l < size else -1
        return self._get13574Index(x, y, w, h)

class UI_WIN_RECT(UI_WIN_BASE):
    def __init__(self, pattern:list[int], screen_w:int, screen_h:int):
        super().__init__(pattern, screen_w, screen_h, self._getPatternIndex)

    def _getPatternIndex(self, x:int, y:int, w:int, h:int) -> int:
        area = self.getArea(x, y, w, h)
        if area == 0:
            return y if x > y else x
        elif area == 2:
            return y if w-1-x > y else w-1-x
        elif area == 6:
            return h-1-y if x > h-1-y else x
        elif area == 8:
            return h-1-y if w-1-x > h-1-y else w-1-x
        return self._get13574Index(x, y, w, h)

