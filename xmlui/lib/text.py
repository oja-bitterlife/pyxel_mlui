from xmlui.core import *
from xmlui.core import XUPageItem

# フォントを扱う
# #############################################################################
class FontBase:
    def __init__(self, font:Any, size:int):
        self.font = font
        self.size = size

    # フォントサイズ算出
    @classmethod
    def get_bdf_size(cls, bdf_font_path):
        with open(bdf_font_path, "r") as f:
            for i, line in enumerate(f.readlines()):
                if i > 100:  # 100行も見りゃええじゃろ...
                    raise Exception(f"{bdf_font_path} has not PIXEL_SIZE")
                if line.startswith("PIXEL_SIZE"):
                    return int(line.split()[-1])
        raise Exception(f"{bdf_font_path} has not PIXEL_SIZE")

    def text_width(self, text:str) -> int:
        return len(text) * self.size

    def text_height(self, text:str) -> int:
        return len(text.splitlines()) * self.size


# テキストを扱う
# #############################################################################
# ラベル
class Label(XUElem):
    ALIGN_ATTR = 'align'  # horizonアライメント
    VALIGN_ATTR = 'valign'  # verticalアライメント

    def __init__(self, elem:XUElem):
        super().__init__(elem.xmlui, elem._element)
        self.align = elem.attr_str(self.ALIGN_ATTR, XURect.ALIGN_LEFT)
        self.valign = elem.attr_str(self.VALIGN_ATTR, XURect.ALIGN_TOP)

    def aligned_pos(self, font:FontBase) -> tuple[int, int]:
        area = self.area
        return area.aligned_pos(font.text_width(self.text), font.size, self.align, self.valign)

# メッセージ(ページつきアニメテキスト)
class Msg(XUPageText):
    PAGE_LINE_NUM_ATTR = 'page_line_num'  # 1ページに含まれる行数
    WRAP_ATTR = 'wrap'  # 1行の最大長(折り返し位置)

    # タグのテキストを処理する
    def __init__(self, elem:XUElem):
        # パラメータはXMLから取得
        page_line_num = elem.attr_int(self.PAGE_LINE_NUM_ATTR, 1024)
        wrap = elem.attr_int(self.WRAP_ATTR, 4096)

        super().__init__(elem, page_line_num, wrap)

    # 全角にして登録
    def append_msg(self, text:str, all_params:dict[str,Any]={}) -> list[XUPageItem]:
        return self.add_pages(XUTextUtil.format_zenkaku(text, all_params), self.page_line_num, self.wrap)

# スクロールメッセージ
class MsgScr(Msg):
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
        def from_page(cls, page:XUPageItem, total_line_no:int, page_text:str) -> list["MsgScr.LineInfo"]:
            out:list[MsgScr.LineInfo] = []
            for i,line in enumerate(page_text.splitlines()):
                out.append(MsgScr.LineInfo(page, total_line_no + i, i, line))
            return out

    # スクロールバッファを行単位で返す
    def get_scroll_lines(self, scroll_line_num:int) -> list[LineInfo]:
        # テキストがない
        if not self.pages or scroll_line_num == 0:
            return []

        # 各ページの全体行中の位置を記録
        total_line_no = {0: 0}
        for page_no in range(self.current_page_no):
            total_line_no[page_no+1] = total_line_no[page_no] + len(self.pages[page_no].all_text.splitlines())

        # 現在ページを表示位置まで登録
        out = self.LineInfo.from_page(self.current_page, total_line_no[self.current_page_no], self.current_page.text)
    
        # 前ページを巻き戻しながら保存
        for page_no in range(self.current_page_no-1, -1, -1):
            out = self.LineInfo.from_page(self.pages[page_no], total_line_no[page_no], self.pages[page_no].all_text) + out
            # バッファを満たした
            if len(out) >= scroll_line_num:
                break

        # オーバー分切り捨て
        over = max(0, len(out) - scroll_line_num)
        return out[over:]


# デコレータを用意
# *****************************************************************************
class Decorator(XUTemplate.HasRef):
    def label(self, tag_name:str):
        def wrapper(bind_func:Callable[[Label,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(Label(elem), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper

    def msg(self, tag_name:str):
        def wrapper(bind_func:Callable[[Msg,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(Msg(elem), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper

    def msg_scr(self, tag_name:str):
        def wrapper(bind_func:Callable[[MsgScr,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(MsgScr(elem), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper
