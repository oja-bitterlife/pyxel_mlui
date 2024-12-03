import pyxel

from xmlui_core import *

# フォントを扱う
# #############################################################################
default:"Font" = None # type: ignore

class Font:
    def __init__(self, font_path:str):
        # フォントデータ読み込み
        self.font = pyxel.Font(font_path)

        # フォントサイズ算出
        self.size = 0
        with open(font_path, "r") as f:
            for i, line in enumerate(f.readlines()):
                if i > 100:  # 100行も見りゃええじゃろ...
                    raise Exception(f"{font_path} has not PIXEL_SIZE")
                if line.startswith("PIXEL_SIZE"):
                    self.size = int(line.split()[-1])
                    break
 
    def text_width(self, text:str) -> int:
        return self.font.text_width(text)


# ラベルを扱う
# #############################################################################
class Label(XUState):
    def __init__(self, state:XUState, align:str="center"):
        super().__init__(state.xmlui, state._element)
        self._align = align

    def aligned_pos(self, font:Font, w:int=0) -> tuple[int, int]:
        area = self.area  # 低速なので使うときは必ず一旦ローカルに
        return area.aligned_x(font.text_width(self.text)+w, self._align), area.center_y(font.size)

# デコレータを用意
def label(xmlui:XMLUI, tag_name:str):
    def wrapper(bind_func:Callable[[Label,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUState, event:XUEvent):
            bind_func(Label(state), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper


# メッセージ
# *****************************************************************************
class Msg(XUPageBase):
    PAGE_LINES_ATTR = "page_lines"  # ページの行数
    WRAP_ATTR = "wrap"  # ワードラップ文字数

    # タグのテキストを処理する
    def __init__(self, state:XUState):
        page_lines = state.attr_int(self.PAGE_LINES_ATTR, 1)
        wrap = state.attr_int(self.WRAP_ATTR, 4096)
        super().__init__(state, page_lines, wrap)

# デコレータを用意
def msg(xmlui:XMLUI, tag_name:str):
    def wrapper(bind_func:Callable[[Msg,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUState, event:XUEvent):
            bind_func(Msg(state), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper
