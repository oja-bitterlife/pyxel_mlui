from xmlui.core import *
from xmlui.lib.decorator import DefaultDecorator

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
class Label(XUState):
    def __init__(self, state:XUState, align_attr:str, valign_attr:str):
        super().__init__(state.xmlui, state._element)
        self._align = state.attr_str(align_attr, "left")
        self._valign = state.attr_str(valign_attr, "top")

    def aligned_pos(self, font:FontBase, w:int=0, h:int=0) -> tuple[int, int]:
        area = self.area  # 低速なので使うときは必ず一旦ローカルに
        x = area.aligned_x(font.text_width(self.text)+w, self._align)
        y = area.aligned_y(font.size, self._valign)
        return x, y

    def aligned_area(self, font:FontBase, w:int=0, h:int=0) -> XURect:
        area = self.area  # 低速なので使うときは必ず一旦ローカルに
        area.x = area.aligned_x(font.text_width(self.text)+w, self._align)
        area.y = area.aligned_y(font.size, self._valign)
        return area

# メッセージ
class Msg(XUTextPage):
    # タグのテキストを処理する
    def __init__(self, state:XUState, page_line_num_attr:str, wrap_attr:str):
        page_line_num = state.attr_int(page_line_num_attr, 1)
        wrap = state.attr_int(wrap_attr, 4096)
        super().__init__(state, page_line_num, wrap)

class MsgScr(Msg):
    # タグのテキストを処理する
    def __init__(self, state:XUState, page_line_num_attr:str, wrap_attr:str):
        super().__init__(state, page_line_num_attr, wrap_attr)

    def scroll_buf(self:"MsgScr", scroll_line_num:int) -> list[str]:
        # 現在ページの挿入
        buf = self.anim.text.splitlines()

        # 行が足りるまでページを巻き戻して挿入
        for page_no in range(self.page_no-1, -1, -1):
            if len(buf) >= scroll_line_num:
                break
            buf = self.pages[page_no] + buf

        # 最大行数に絞る。アニメーション中だけ最下行が使える。
        max_line = scroll_line_num if not self.anim.is_finish else scroll_line_num-1
        buf = list(reversed(list(reversed(buf))[:max_line]))

        return buf

# おまけ
class MsgDQ(MsgScr):
    TALK_MARK = "＊「"
    IS_TALK_ATTR = "_xmlui_talk_mark"

    # タグのテキストを処理する
    def __init__(self, state:XUState, page_line_num_attr:str, wrap_attr:str):
        super().__init__(state, page_line_num_attr, wrap_attr)

    # 各行に会話用インデントが必要かを返す
    def scroll_indents(self, scroll_line_num:int) -> list[bool]:
        # 現在ページの挿入
        anim_line_num = len(self.anim.text.splitlines())
        indents = [True if not self.pages[self.page_no][i].startswith(self.TALK_MARK) else False for i in range(anim_line_num)]

        # 行が足りるまでページを巻き戻して挿入
        for page_no in range(self.page_no-1, -1, -1):
            if len(indents) >= scroll_line_num:
                break
            indents =  [True if not line.startswith(self.TALK_MARK) else False for line in self.pages[page_no]] + indents

        # 最大行数に絞る。アニメーション中だけ最下行が使える。
        max_line = scroll_line_num if not self.anim.is_finish else scroll_line_num-1
        indents = list(reversed(list(reversed(indents))[:max_line]))

        return indents

    # テキストの先頭に会話マークを付ける
    @classmethod
    def convert_talk(cls, text:str) -> str:
        return cls.TALK_MARK + text

    @classmethod
    def start_talk(cls, state:XUState, text:str):
        state.text = text
        state.set_attr(cls.IS_TALK_ATTR, True)

    @classmethod
    def start_system(cls, state:XUState, text:str):
        state.text = text
        state.set_attr(cls.IS_TALK_ATTR, False)

    @property
    def is_talk(self):
        return self.attr_bool(self.IS_TALK_ATTR, False)

# デコレータを用意
# *****************************************************************************
class Decorator(DefaultDecorator):
    def __init__(self, xmlui:XMLUI, group:str|None=None):
        super().__init__(xmlui, group)

    def label(self, tag_name:str, align_attr:str="align", valign_attr:str="valign"):
        def wrapper(bind_func:Callable[[Label,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                return bind_func(Label(state, align_attr, valign_attr), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw, self.group)
        return wrapper

    def msg(self, tag_name:str, page_line_num_attr:str="page_line_num", wrap_attr:str="wrap"):
        def wrapper(bind_func:Callable[[Msg,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                return bind_func(Msg(state, page_line_num_attr, wrap_attr), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw, self.group)
        return wrapper

    def msg_scr(self, tag_name:str, page_line_num_attr:str="page_line_num", wrap_attr:str="wrap"):
        def wrapper(bind_func:Callable[[MsgScr,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                return bind_func(MsgScr(state, page_line_num_attr, wrap_attr), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw, self.group)
        return wrapper

    def msg_dq(self, tag_name:str, page_line_num_attr:str="page_line_num", wrap_attr:str="wrap"):
        def wrapper(bind_func:Callable[[MsgDQ,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                return bind_func(MsgDQ(state, page_line_num_attr, wrap_attr), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw, self.group)
        return wrapper
