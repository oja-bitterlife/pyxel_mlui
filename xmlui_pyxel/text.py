import pyxel

from xmlui_core import *
from . import win

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
# フレーム無しラベル
class LabelRO(XUStateRO):
    TEXT_OFFSET_X_ATTR:str = "text_x"
    TEXT_OFFSET_Y_ATTR:str = "text_y"

    def __init__(self, state:XUStateRO, align:str="center"):
        super().__init__(state.xmlui, state._element)
        self._align = align

    def draw(self):
        pyxel.rect(self._area.x, self._area.y, self._area.w, self._area.h, 12)

        text_w = default.text_width(self.text)
        match self.align:
            case "left":
                x =  self._area.x + self.offset_x
            case "center":
                x = self._area.center_x(text_w) + self.offset_x
            case "right":
                x = self._area.right() - text_w - self.offset_x
            case _:
                raise ValueError(f"align:{self.align} is not supported.")

        # ラベルテキスト描画
        default.draw(x, self._area.center_y(default.size) + self.offset_y, self.text, 7)

    @property
    def align(self) -> str:
        return self._align

    @property
    def offset_x(self) -> int:
        return self.attr_int(self.TEXT_OFFSET_X_ATTR, 0)

    @property
    def offset_y(self) -> int:
        return self.attr_int(self.TEXT_OFFSET_Y_ATTR, 0)

class NFLabel(LabelRO):
    def __init__(self, state:XUState, align:str="center"):
        super().__init__(state, align)

    def set_offset(self, x:int, y:int):
        rw = self.asRW()
        rw.set_attr(self.TEXT_OFFSET_X_ATTR, x)
        rw.set_attr(self.TEXT_OFFSET_Y_ATTR, y)

# デコレータを用意
def label_update_bind(xmlui:XMLUI, tag_name:str):
    def wrapper(update_func:Callable[[NFLabel,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(NFLabel(state), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def label_draw_bind(xmlui:XMLUI, tag_name:str, align:str="center"):
    def wrapper(draw_func:Callable[[LabelRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(LabelRO(state, align), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper
