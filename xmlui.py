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
    def __init__(self, xmlui:'XMLUI', element:Element):
        self.xmlui = xmlui  # ライブラリへのIF
        self._element = element  # 自身のElement

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

    # その他
    # *************************************************************************
    @property
    def tag(self) -> str:
        return self._element.tag

    @property
    def area(self) -> UI_RECT:
        return UI_RECT(self.area_x, self.area_y, self.area_w, self.area_h)

    def setPos(self, x:int, y:int) -> 'UI_STATE':
        return self.setAttr(["x", "y"], [x, y])

    def setAbsPos(self, x:int, y:int) -> 'UI_STATE':
        return self.setAttr(["abs_x", "abs_y"], [x, y])

    def setEnable(self, enable:bool) -> 'UI_STATE':
        return self.setAttr("enable", enable)

    def setVisible(self, visible:bool) -> 'UI_STATE':
        return self.setAttr("visible", visible)

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
        elements:list[UI_STATE] = self.findByTagAll(tag)
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

    # GRID用
    def findGridByTag(self, tag_outside:str, tag_inside:str) -> list[list['UI_STATE']]:
        return [outside.findByTagAll(tag_inside) for outside in self.findByTagAll(tag_outside)]

    # 転置(Transpose)GRID
    def findGridByTagT(self, tag_outside:str, tag_inside:str) -> list[list['UI_STATE']]:
        grid = self.findGridByTag(tag_outside, tag_inside)
        grid = [[grid[y][x] for y in range(len(grid))] for x in range(len(grid[0]))]  # 転置
        return grid

    # グリッド各アイテムの座標設定
    def _arrangeGrid(self, grid:list[list['UI_STATE']], w:int, h:int):
        for y,cols in enumerate(grid):
            for x,rows in enumerate(cols):
                rows.setAttr(["x", "y"], (x*w, y*h))
        return grid

    # 横並びグリッド
    def arrangeGridByTag(self, tag_outside:str, tag_inside:str, w:int, h:int) -> list[list['UI_STATE']]:
        return self._arrangeGrid(self.findGridByTag(tag_outside, tag_inside), w, h)

    # 転置縦並びグリッド
    def arrangeGridByTagT(self, tag_outside:str, tag_inside:str, w:int, h:int) -> list[list['UI_STATE']]:
        return self._arrangeGrid(self.findGridByTagT(tag_outside, tag_inside), w, h)

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

    def close(self, id:str|None=None):
        try:
            state = self.xmlui.root.findByID(id if id else self.id)
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
    # わかりやすく全てプロパティを用意しておく(デフォルト値も省略せず書く)
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
    def update_count(self) -> int:  # テキスト自動改行文字数
        return self.attrInt("update_count", 0)

    @property
    def use_event(self) -> bool:  # eventを使うかどうか
        return self.attrBool("use_event", False)

    @property
    def cur_x(self) -> int:  # 選択グリッドx
        return self.attrInt("cur_x", 0)
    @property
    def cur_y(self) -> int:  # 選択グリッドy
        return self.attrInt("cur_y", 0)


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

        # 表示対象Elementを格納(update/draw連携用)
        self._draw_targets:list[UI_STATE] = []
        self._active_state:UI_STATE|None = None

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
        self._event.update()

        # 更新対象(enable)Elementを取得
        updates = [UI_STATE(self, element) for element in self.root._element.iter() if element.attrib.get("enable", True)]
        self._draw_targets = [state for state in updates if state.visible]

        # use_eventがTrueなstateだけ抜き出す
        use_event_states = list(filter(lambda state: state.use_event, self._draw_targets))
        self._active_state = use_event_states[-1] if use_event_states else None  # 最後=Active

        # 更新処理
        for state in self._draw_targets:
            self.updateElement(state.tag, state, self._event if state == self._active_state else UI_EVENT())
            state.setAttr("update_count", state.update_count + 1)

    # 描画用
    # *************************************************************************
    def draw(self):
        # 更新対象(visible)を取得(Updateされたもののみ対象)
        self._draw_targets = [state for state in self._draw_targets if state.visible]

        # エリア更新
        for state in self._draw_targets:
            if state.parent:  # rootは親を持たないので更新不要
                # absがあれば絶対座標、なければ親からのオフセット
                state.setAttr("area_x", state.abs_x if state.hasAttr("abs_x") else state.x + state.parent.area_x)
                state.setAttr("area_y", state.abs_y if state.hasAttr("abs_y") else state.y + state.parent.area_y)
                state.setAttr("area_w", state.attrInt("w", state.parent.area_w))
                state.setAttr("area_h", state.attrInt("h", state.parent.area_h))

        # 描画処理
        for state in self._draw_targets:
            self.drawElement(state.tag, state, self._event if state == self._active_state else UI_EVENT())

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
class _UI_TEXT_BASE(UI_STATE):
    # クラス定数
    ROOT_TAG ="xmlui_text_root"
    PAGE_TAG ="xmlui_page"

    SEPARATE_REGEXP = r"\\n"

    DRAW_COUNT_ATTR = "draw_count"
    PAGE_NO_ATTR = "page_no"

    # ページ関係
    # -----------------------------------------------------
   # 現在ページ
    @property
    def page_no(self) -> int:
        return self.attrInt(self.PAGE_NO_ATTR, 0)

    # ページの最大数
    @property
    def page_max(self) -> int:
        return len(self.findByTagAll(self.PAGE_TAG))

    # ページ全部表示済みかどうか
    @property
    def is_end_page(self) -> bool:
        return self.page_no >= self.page_max

    # ページテキスト
    @property
    def page_text(self) -> str:
        return self._limitStr(self.findByTagAll(self.PAGE_TAG)[self.page_no].text if not self.is_end_page else "", self.draw_count)

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

# 読み込み専用
class UI_TEXT_RO(_UI_TEXT_BASE):
    def __init__(self, find_root:UI_STATE):
        super().__init__(find_root.xmlui, find_root._element)

# アニメーションテキストページ管理
class UI_TEXT(_UI_TEXT_BASE):
    def __init__(self, xmlui:XMLUI, text:str, page_line_num:int, wrap:int=4096):
        super().__init__(xmlui, Element(self.ROOT_TAG))
        self.setAttr(self.DRAW_COUNT_ATTR, 0)
        self.setAttr(self.PAGE_NO_ATTR, 0)

        # 改行を\nに統一して全角化
        tmp_text = self.convertZenkaku(re.sub(self.SEPARATE_REGEXP, "\n", text).strip())

        # 各行に分解し、その行をさらにwrapで分解する
        wrap = max(1, wrap)  # 0だと無限になってしまうので最低1を入れておく
        lines =  sum([[line[i:i+wrap] for i in  range(0, len(line), wrap)] for line in tmp_text.splitlines()], [])

        # ページごとにElementを追加
        for i in range(0, len(lines), page_line_num):
            page_text = "\n".join(lines[i:i+page_line_num])  # 改行を\nにして全部文字列に
            page = UI_STATE(xmlui, Element(self.PAGE_TAG))
            page._element.text = page_text
            self.addChild(page)

    # ページ関係
    # -----------------------------------------------------
    # page_noの操作
    def nextPage(self, add:int=1) -> 'UI_TEXT':
        self.reset()  # ページが変わればまた最初から
        self.setAttr(self.PAGE_NO_ATTR, self.page_no+1)
        return self

    # アニメーション用
    # -----------------------------------------------------
    # 表示カウンタのリセット
    def reset(self):
        self.setAttr(self.DRAW_COUNT_ATTR, 0)

    # 一気に表示
    def finish(self):
        self.setAttr(self.DRAW_COUNT_ATTR, len(self.page_text))

    # イベントアクション
    # -----------------------------------------------------
    # 状況に応じた決定ボタン操作を行う
    def action(self):  # 結果が一意でないのでselfは返さない
        # ページ中に残りがあるなら一気に表示
        if not self.is_finish:
            self.finish()
        # ページが残っていたら次のページへ
        elif not self.is_end_page:
            self.nextPage()


# メニュー系
# ---------------------------------------------------------
# グリッド情報
class _UI_GRID_CURSOR_BASE:
    def __init__(self, state:'UI_STATE'):
        self._state = state  # カーソル位置保存用

    @property
    def cur_x(self) -> int:
        return self._state.cur_x
    @property
    def cur_y(self) -> int:
        return self._state.cur_y

class UI_GRID_CURSOR_RO(_UI_GRID_CURSOR_BASE):
    pass

# グリッド選択
class UI_GRID_CURSOR(_UI_GRID_CURSOR_BASE):
    def __init__(self, state:'UI_STATE', grid:list[list['UI_STATE']]):
        super().__init__(state)
        self._grid = grid  # グリッド保存

    # 範囲限定付き座標設定
    def setCurPos(self, x:int, y:int, wrap:bool=False) -> 'UI_GRID_CURSOR':
        self._state.setAttr("cur_x", (x + self.grid_w) % self.grid_w if wrap else max(min(x, self.grid_w-1), 0))
        self._state.setAttr("cur_y", (y + self.grid_h) % self.grid_h if wrap else max(min(y, self.grid_h-1), 0))
        self._state.setPos(self.selected.x, self.selected.y)
        return self

    # それぞれの移動
    def moveLeft(self, wrap:bool=False) -> 'UI_GRID_CURSOR':
        return self.setCurPos(self._state.cur_x-1, self._state.cur_y, wrap)
    def moveRight(self, wrap:bool=False) -> 'UI_GRID_CURSOR':
        return self.setCurPos(self._state.cur_x+1, self._state.cur_y, wrap)
    def moveUp(self, wrap:bool=False) -> 'UI_GRID_CURSOR':
        return self.setCurPos(self._state.cur_x, self._state.cur_y-1, wrap)
    def moveDown(self, wrap:bool=False) -> 'UI_GRID_CURSOR':
        return self.setCurPos(self._state.cur_x, self._state.cur_y+1, wrap)

    # 入力に応じた挙動一括
    def moveByEvent(self, input:set[str], leftEvent:str, rightEvent:str, upEvent:str, downEvent:str, x_wrap:bool=False, y_wrap:bool=False) -> 'UI_GRID_CURSOR':
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
    def selected(self) -> 'UI_STATE':
        return self._grid[self.cur_y][self.cur_x]


# ダイアル
# ---------------------------------------------------------
# 情報管理のみ
class _UI_DIAL_BASE:
    def __init__(self, state:'UI_STATE', digits_attr:str, digit_pos_attr:str):
        self._state = state  # 記憶場所Element
        self._digits_attr = digits_attr  # 数字リスト(文字列)
        self._digit_pos_attr = digit_pos_attr  # 操作桁位置

    @property
    def digit_pos(self) -> int:
        return self._state.attrInt(self._digit_pos_attr)

    @property
    def digits(self) -> str:
        return self._state.attrStr(self._digits_attr)

    @property
    def zenkakuDigits(self) -> str:
        return _UI_TEXT_BASE.convertZenkaku(self.digits)

    @property
    def number(self) -> int:
        return int("".join(reversed([d for d in self.digits])))

class UI_DIAL_RO(_UI_DIAL_BASE):
    pass

# ダイアル操作
class UI_DIAL(_UI_DIAL_BASE):
    def __init__(self, state:'UI_STATE', digits_attr:str, digit_pos_attr:str, digit_num:int, digit_list:str="0123456789"):
        super().__init__(state, digits_attr, digit_pos_attr)
        self._digit_list = digit_list  # 数字リスト。基本は数字だけどどんな文字でもいける

        # 初期化
        if not state.hasAttr(digits_attr):
            state.setAttr(digits_attr, digit_list[0]*digit_num)

    # 移動しすぎ禁止付きdigit_pos設定
    def setDigitPos(self, digit_pos) -> 'UI_DIAL':
        self._state.setAttr(self._digit_pos_attr, max(0, min(len(self.digits), digit_pos)))
        return self

    # 回り込み付きdigit増減
    def _addDigit(self, digit:str, add:int) -> str:
        return self._digit_list[(self._digit_list.find(digit)+len(self._digit_list)+add) % len(self._digit_list)]

    # 指定位置のdigitを変更する
    def changeDigit(self, digit_pos:int, digit:str) -> 'UI_DIAL':
        self._state.setAttr(self._digits_attr, "".join([digit if i == digit_pos else d for i,d in enumerate(self._state.attrStr(self._digits_attr))]))
        return self

    # 入力に応じた挙動一括
    def changeByEvent(self, input:set[str], leftEvent:str, rightEvent:str, upEvent:str, downEvent:str) -> 'UI_DIAL':
        if leftEvent in input:
            self.setDigitPos(self.digit_pos+1)  # 左移動
        if rightEvent in input:
            self.setDigitPos(self.digit_pos-1)  # 右移動
        if upEvent in input:
            self.changeDigit(self.digit_pos, self._addDigit(self.digits[self.digit_pos], +1))  # digitを増やす
        if downEvent in input:
            self.changeDigit(self.digit_pos, self._addDigit(self.digits[self.digit_pos], -1))  # digitを減らす
        return self
