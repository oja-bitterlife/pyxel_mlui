import math
from typing import Any,Callable,Self

from xmlui.core import XURect,XMLUI,XUElem,XUEvent,XUSelectItem,_XUSelectBase,XUTextUtil

# フォントを扱う
# #############################################################################
class _XUFontBase:
    def __init__(self, font:Any, size:int):
        self.font = font
        self.size = size

    def text_width(self, text:str) -> int:
        return len(text) * self.size

    def text_height(self, text:str) -> int:
        return len(text.splitlines()) * self.size


# テキストを扱う
# #############################################################################
# ラベル
class XULabel(XUElem):
    ALIGN_ATTR = 'align'  # horizonアライメント
    VALIGN_ATTR = 'valign'  # verticalアライメント

    def __init__(self, elem:XUElem):
        super().__init__(elem.xmlui, elem._element)
        self.align = XURect.Align.from_str(elem.attr_str(self.ALIGN_ATTR, XURect.Align.LEFT))
        self.valign = XURect.Align.from_str(elem.attr_str(self.VALIGN_ATTR, XURect.Align.TOP))

    def aligned_pos(self, font:_XUFontBase, text:str|None=None) -> tuple[int, int]:
        # 引数があればそちらを(置換文字列対応)
        if text is None:
            text = self.text
        area = self.area
        return area.aligned_pos(font.text_width(text), font.size, self.align, self.valign)


# アニメーションテキスト
# *****************************************************************************
# 1ページ分のテキストをアニメーション表示する
class XUPageItem(XUSelectItem):
    DRAW_COUNT_ATTR = "_xmlui_text_count"

    # 初期化
    # -----------------------------------------------------
    def __init__(self, elem:XUElem):
        super().__init__(elem.xmlui, elem._element)

    # 表示カウンタ操作
    # -----------------------------------------------------
    # 現在の表示文字数
    @property
    def draw_count(self) -> float:
        return float(self.attr_float(self.DRAW_COUNT_ATTR, 0))

    @draw_count.setter
    def draw_count(self, count:float) -> float:
        self.set_attr(self.DRAW_COUNT_ATTR, count)
        return count

    # アニメーション用
    # -----------------------------------------------------
    # draw_countまでの文字列を改行分割。スライスじゃないのは改行を数えないため
    @classmethod
    def _limitstr(cls, tmp_text:str, text_count:float) -> str:
        limit = math.ceil(text_count)

        # limitまで縮める
        for i,c in enumerate(tmp_text):
            if (limit := limit if ord(c) < 0x20 else limit-1) < 0:  # 改行は数えない
                return tmp_text[:i]
        return tmp_text

    # 改行を抜いた文字数よりカウントが大きくなった
    @property
    def is_finish(self) -> bool:
        return self.draw_count >= self.length

    # 一気に表示
    @property
    def finish(self) -> Self:
        self.draw_count = self.length
        return self

    # draw_countまでのテキストを受け取る
    @property
    def text(self) -> str:
        return self._limitstr(super().text, self.draw_count)

    # draw_countまでのテキストを全角で受け取る
    @property
    def zenkaku(self) -> str:
        return XUTextUtil.format_zenkaku(self.text)

    # テキスト全体
    # -----------------------------------------------------
    # 全体テキストを受け取る
    @property
    def all_text(self) -> str:
        return super().text

    # テキスト全体の長さ(\n\0抜き)
    @property
    def length(self) -> int:
        return XUTextUtil.length(super().text)

    # 行
    # -----------------------------------------------------
    # 現在の行番号
    @property
    def current_line_no(self) -> int:
        return max(0, len(self.text.splitlines())-1)

    # 現在の行テキスト
    @property
    def current_line(self) -> str:
        lines = self.text.splitlines()
        return lines[self.current_line_no] if lines else ""

    # 現在の行の全体の長さ
    @property
    def current_line_length(self):
        return len(self.all_text.splitlines()[self.current_line_no])


# 複数ページをセレクトアイテムで管理
class XUPageList(_XUSelectBase):
    def __init__(self, elem:XUElem, page_line_num:int=1024, wrap:int=4096):
        super().__init__(elem, "", 1, 0, 0)
        self.page_line_num = page_line_num
        self.wrap = wrap

        # ページ未登録なら登録しておく
        if not self.pages and self.text.strip():
            self.add_pages(self.text, page_line_num, wrap)

    # ページ操作
    # -----------------------------------------------------
    @property
    def page_no(self) -> int:
        return self.selected_no
    @page_no.setter
    def page_no(self, no:int=0) -> Self:
        # ページを切り替えたときはカウンタをリセット
        if self.page_no != no:
            self.current_page.draw_count = 0
        self.select(no)
        return self

    # 次のページへ
    def next_page(self):
        self.page_no += 1

    # ページテキスト
    # -----------------------------------------------------
    # 現在ページのアニメーション情報アクセス
    @property
    def current_page(self):
        return XUPageItem(self.items[self.page_no])

    # ただの型キャスト。中身はitems
    @property
    def pages(self) -> list[XUPageItem]:
        return [XUPageItem(item) for item in self.items]

    # 次ページがなくテキストは表示完了 = 完全に終了
    @property
    def is_all_finish(self):
        if not self.items:  # テキストがない
            return True
        return not self.is_next_wait and self.current_page.is_finish

    # 次ページあり待機中
    @property
    def is_next_wait(self):
        if not self.items:  # テキストがない
            return False
        return self.current_page.is_finish and self.page_no < self.item_num-1

    # ツリー操作
    # -----------------------------------------------------
    # テキストをページ分解してツリーにぶら下げる。作ったページを返す
    def add_pages(self, text:str, page_line_num:int, wrap:int):
        pages:list[XUPageItem] = []
        for page_text in XUTextUtil.split_page_texts(text, page_line_num, wrap):
            page_item = XUPageItem(XUElem.new(self.xmlui, self.ITEM_TAG))

            # ページテキストを登録
            self._util_info.add_child(page_item.set_text(page_text))
            pages.append(page_item)  # return用
        return pages

    def clear_pages(self):
        for child in self._util_info.find_by_tagall(self.ITEM_TAG):
            child.remove()


# メッセージ(ページつきアニメテキスト)
class XUMsg(XUPageList):
    PAGE_LINE_NUM_ATTR = 'page_line_num'  # 1ページに含まれる行数
    WRAP_ATTR = 'wrap'  # 1行の最大長(折り返し位置)

    # タグのテキストを処理する
    def __init__(self, elem:XUElem):
        # パラメータはXMLから取得
        page_line_num = elem.attr_int(self.PAGE_LINE_NUM_ATTR, 1024)
        wrap = elem.attr_int(self.WRAP_ATTR, 4096)

        super().__init__(elem, page_line_num, wrap)

    # 半角のまま登録
    def append_msg(self, text:str, all_params:dict[str,Any]={}) -> list[XUPageItem]:
        return self.add_pages(XUTextUtil.format_dict(text, all_params), self.page_line_num, self.wrap)

    # 全角にして登録
    def append_zenkaku(self, text:str, all_params:dict[str,Any]={}) -> list[XUPageItem]:
        return self.add_pages(XUTextUtil.format_zenkaku(text, all_params), self.page_line_num, self.wrap)

# スクロールメッセージ
class XUMsgScr(XUMsg):
    # 現在ページはアニメ対応。前ページは常に全体
    class LineInfo(XUElem):
        def __init__(self, page:XUPageItem, total_line_no:int, page_line_no:int, text:str):
            super().__init__(page.xmlui, page._element)
            self.total_line_no = total_line_no  #  全体行中のページ開始行番号
            self.page_line_no = page_line_no  # ページ中の行番号
            self._text = text  # テキスト

        # override
        @property
        def text(self) -> str:
            return self._text

        # ページ内の各行を分解してLineInfoを作ってリストで返す
        @classmethod
        def from_page(cls, page:XUPageItem, total_line_no:int, page_text:str) -> list[Self]:
            out:list[Self] = []
            for i,line in enumerate(page_text.splitlines()):
                out.append(cls(page, total_line_no + i, i, line))
            return out

    # スクロールバッファを行単位で返す
    def get_scroll_lines(self, scroll_line_num:int) -> list[LineInfo]:
        # テキストがない
        if not self.pages or scroll_line_num <= 0:
            return []

        # 各ページの全体行中の位置を記録
        total_line_no = {0: 0}
        for page_no in range(self.page_no):
            total_line_no[page_no+1] = total_line_no[page_no] + len(self.pages[page_no].all_text.splitlines())

        # 現在ページを表示位置まで登録
        out = self.LineInfo.from_page(self.current_page, total_line_no[self.page_no], self.current_page.text)
    
        # 前ページを巻き戻しながら保存
        for page_no in range(self.page_no-1, -1, -1):
            out = self.LineInfo.from_page(self.pages[page_no], total_line_no[page_no], self.pages[page_no].all_text) + out
            # バッファを満たした
            if len(out) >= scroll_line_num:
                break

        # オーバー分切り捨て
        over = max(0, len(out) - scroll_line_num)
        return out[over:]


# デコレータを用意
# *****************************************************************************
class Decorator(XMLUI.HasRef):
    def label(self, tag_name:str):
        def wrapper(bind_func:Callable[[XULabel,XUEvent], None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(XULabel(elem), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw)
        return wrapper

    def msg(self, tag_name:str, speed_attr:str|None=None):
        def wrapper(bind_func:Callable[[XUMsg,XUEvent], None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                msg = XUMsg(elem)
                if speed_attr and msg.pages:
                    msg.current_page.draw_count += msg.attr_float(speed_attr, 0)
                return bind_func(msg, event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw)
        return wrapper

    def msg_scr(self, tag_name:str, speed_attr:str|None=None):
        def wrapper(bind_func:Callable[[XUMsgScr,XUEvent], None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                msg = XUMsgScr(elem)
                if speed_attr and msg.pages:
                    msg.current_page.draw_count += msg.attr_float(speed_attr, 0)
                return bind_func(XUMsgScr(elem), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw)
        return wrapper
