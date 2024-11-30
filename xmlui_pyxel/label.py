import pyxel

from xmlui_core import *
from . import win,font

# ラベル
# *****************************************************************************
class LabelRO(win._BaseRound):
    LABEL_OFFSET_ATTR:str = "label_offset"

    def __init__(self, state:XUStateRO, align:str="center"):
        super().__init__(state)
        self._align = align

    def draw(self):
        super().draw()  # ウインドウ描画

        text_w = font.data.text_width(self.text)
        match self.align:
            case "left":
                x =  self.area.x + self.offset
            case "center":
                x = self.area.center_x(text_w)
            case "right":
                x = self.area.right() - text_w - self.offset
            case _:
                raise ValueError(f"align:{self.align} is not supported.")

        # ラベルテキスト描画
        pyxel.text(x, self.area.center_y(font.size), self.text, 7, font.data)

    @property
    def align(self) -> str:
        return self._align

    @property
    def offset(self) -> int:
        return self.attr_int(self.LABEL_OFFSET_ATTR, 0)

class Label(LabelRO):
    def __init__(self, state:XUState, align:str="center"):
        super().__init__(state, align)

    def set_offset(self, x:int):
        self.set_attr(self.LABEL_OFFSET_ATTR, x)

# デコレータを用意
def label_update_bind(xmlui:XMLUI, tag_name:str):
    def wrapper(update_func:Callable[[Label,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(Label(state), event)
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


# *****************************************************************************
class NFLabelRO(win.XUWinRectFrame):
    LABEL_OFFSET_ATTR:str = "label_offset"

    def __init__(self, state:XUStateRO, align:str="center"):
        super().__init__(state, [12], pyxel.width, pyxel.height)
        self._align = align

    def draw(self):
        self.draw_buf(pyxel.screen.data_ptr())

        text_w = font.data.text_width(self.text)
        match self.align:
            case "left":
                x =  self.area.x + self.offset
            case "center":
                x = self.area.center_x(text_w)
            case "right":
                x = self.area.right() - text_w - self.offset
            case _:
                raise ValueError(f"align:{self.align} is not supported.")

        # ラベルテキスト描画
        pyxel.text(x, self.area.center_y(font.size), self.text, 7, font.data)

    @property
    def align(self) -> str:
        return self._align

    @property
    def offset(self) -> int:
        return self.attr_int(self.LABEL_OFFSET_ATTR, 0)

class NFLabel(NFLabelRO):
    def __init__(self, state:XUState, align:str="center"):
        super().__init__(state, align)

    def set_offset(self, x:int):
        self.set_attr(self.LABEL_OFFSET_ATTR, x)

# デコレータを用意
def nflabel_update_bind(xmlui:XMLUI, tag_name:str):
    def wrapper(update_func:Callable[[NFLabel,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(NFLabel(state), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def nflabel_draw_bind(xmlui:XMLUI, tag_name:str, align:str="center"):
    def wrapper(draw_func:Callable[[NFLabelRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(NFLabelRO(state, align), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper
