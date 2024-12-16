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
    def __init__(self, elem:XUElem, align_attr:str, valign_attr:str):
        super().__init__(elem.xmlui, elem._element)
        self.align = elem.attr_str(align_attr, "left")
        self.valign = elem.attr_str(valign_attr, "top")

    def aligned_pos(self, font:FontBase) -> tuple[int, int]:
        area = self.area
        return area.aligned_pos(font.text_width(self.text), font.size, self.align, self.valign)

# メッセージ
class Msg(XUPageText):
    PAGE_LINE_NUM_ATTR = 'page_line_num'
    WRAP_ATTR = 'wrap'

    # タグのテキストを処理する
    def __init__(self, elem:XUElem):
        page_line_num = elem.attr_int(self.PAGE_LINE_NUM_ATTR, 1024)
        wrap = elem.attr_int(self.WRAP_ATTR, 4096)
        super().__init__(elem, page_line_num, wrap)

    # 全角にして登録
    def append_msg(self, text:str, all_params:dict[str,Any]={}) -> list[XUPageItem]:
        return self.add_pages(XUTextUtil.format_zenkaku(text, all_params), self.page_line_num, self.wrap)

# おまけ
class MsgDQ(Msg):
    TALK_START = "＊「"
    MARK_ATTR = "_xmlui_talk_mark"

    MARK_TALK = "talk"
    MARK_ENEMY = "enemy"

    # インデント用
    # -----------------------------------------------------
    class MsgDQItem(XUPageItem):
        def __init__(self, page_item:XUElem):
            super().__init__(page_item)

        def is_mark(self, mark:str) -> bool:
            return self.attr_str(MsgDQ.MARK_ATTR) == mark

        def set_mark(self, mark:str) -> Self:
            self.set_attr(MsgDQ.MARK_ATTR, mark)
            return self

        def get_lines_indent(self) -> list[bool]:
            out = []
            for line in self.all_text.splitlines():
                match self.attr_str(MsgDQ.MARK_ATTR):
                    case MsgDQ.MARK_TALK:
                        out.append(not line.startswith(MsgDQ.TALK_START))
                    case MsgDQ.MARK_ENEMY:
                        out.append(True)
                    case _:
                        out.append(False)
            return out

    # スクロール用
    # -----------------------------------------------------
    class DQScrollInfo:
        def __init__(self, line_text:str, need_indent:bool):
            self.line_text = line_text
            self.need_indent = need_indent

    # 必要な行だけ返す(アニメーション対応)
    def get_scroll_lines(self, scroll_size:int) -> list[DQScrollInfo]:
        # スクロール枠の中に収まる前のページを取得する
        all_lines = []
        need_indent = []
        for i in range(self.page_no-1, -1, -1):  # 現在より前へ戻りながら追加
            page_item = self.MsgDQItem(self.pages[i])

            all_lines = page_item.all_text.splitlines() + all_lines
            need_indent = page_item.get_lines_indent() + need_indent

            if len(all_lines) >= scroll_size:
                break

        # 現在のページの情報を追加
        page_item = self.MsgDQItem(self.current_page)
        all_lines += page_item.text.splitlines()
        need_indent += page_item.get_lines_indent()

        # オーバーした行を削除
        over_line = max(0, len(all_lines) - scroll_size)
        all_lines = all_lines[over_line:]
        need_indent = need_indent[over_line:]

        # scroll枠に収まるlineリストを返す
        return [self.DQScrollInfo(line, need_indent[i]) for i,line in enumerate(all_lines)]

    # ページ登録
    # -----------------------------------------------------
    # 会話マークを追加して格納
    def append_talk(self, text:str, all_params:dict[str,Any]={}):
        for page in self.append_msg(text, all_params):
            # 追加されたページにTALKをマーキング
            page_item = self.MsgDQItem(page).set_mark(self.MARK_TALK)
            page._element.text = self.TALK_START + page_item.all_text

    # Enemyマークを追加して格納
    def append_enemy(self, text:str, all_params:dict[str,Any]={}):
        for page in self.append_msg(text, all_params):
            # 追加されたページにTALKをマーキング
            page_item = self.MsgDQItem(page).set_mark(self.MARK_ENEMY)
            page._element.text = self.TALK_START + page_item.all_text


# デコレータを用意
# *****************************************************************************
class Decorator(XUTemplate.HasRef):
    def label(self, tag_name:str, align_attr:str="align", valign_attr:str="valign"):
        def wrapper(bind_func:Callable[[Label,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(Label(elem, align_attr, valign_attr), event)
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

    def msg_dq(self, tag_name:str):
        def wrapper(bind_func:Callable[[MsgDQ,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(MsgDQ(elem), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper
