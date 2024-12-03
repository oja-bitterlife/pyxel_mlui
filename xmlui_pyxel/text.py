import pyxel

from xmlui_core import *
from . import text

# フォントを扱う
# #############################################################################
default:"FONT" = None # type: ignore

class FONT:
    def __init__(self, font_path:str):
        # フォントデータ読み込み
        self.data = pyxel.Font(font_path)

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
        return self.data.text_width(text)

    def draw(self, x:int, y:int, text:str, color:int):
        pyxel.text(x, y, text, color, self.data)


# ラベルを扱う
# #############################################################################
class Label(XUState):
    def __init__(self, state:XUState, align:str="center"):
        super().__init__(state.xmlui, state._element)
        self._align = align

    def draw(self):
        area = self.area  # 低速なので使うときは必ず一旦ローカルに

        text_w = default.text_width(self.text)
        match self.align:
            case "left":
                x =  area.x
            case "center":
                x = area.center_x(text_w)
            case "right":
                x = area.right() - text_w
            case _:
                raise ValueError(f"align:{self.align} is not supported.")

        # ラベルテキスト描画
        default.draw(x, area.center_y(default.size), self.text, 7)

    @property
    def align(self) -> str:
        return self._align

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

    def draw(self):
        # テキスト描画
        for i,page in enumerate(self.page_text.split()):
            area = self.area  # areaは重いので必ずキャッシュ
            text.default.draw(area.x, area.y+i*text.default.size, page, 7)

# デコレータを用意
def msg(xmlui:XMLUI, tag_name:str):
    def wrapper(bind_func:Callable[[Msg,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUState, event:XUEvent):
            bind_func(Msg(state), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper
