import pyxel

from xmlui_core import *
from . import text

# アクティブカラーにする
def _active_color(state:XUStateRO, color:int):
        return 10 if  state.xmlui.debug.is_lib_debug and state.xmlui.active_state == state and color == 7 else color

# 角丸ウインドウ
# *****************************************************************************
class RoundRO(XUWinRoundFrame):
    DEFAULT_PAT = [7,7,12]

    def __init__(self, state:XUStateRO):
        pat = [_active_color(state, c)  for c in self.DEFAULT_PAT]  # アクティブカラーに
        super().__init__(state, pat, pyxel.width, pyxel.height)


    def draw(self):
        self.clip.h = int(self.update_count*self.speed)
        self.clip = self.clip.intersect(XURect(0, 0, pyxel.width, pyxel.height))
        self.draw_buf(pyxel.screen.data_ptr())

class Round(RoundRO, XUState):
    def __init__(self, state:XUStateRO, speed:float):
        super().__init__(state)
        self.set_attr("speed", speed)

# デコレータを用意
def round_update_bind(xmlui:XMLUI, tag_name:str, speed:float=16):
    def wrapper(update_func:Callable[[Round,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(Round(state, speed), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def round_draw_bind(xmlui:XMLUI, tag_name:str):
    def wrapper(draw_func:Callable[[RoundRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(RoundRO(state), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper


# 四角ウインドウ
# *****************************************************************************
class RectRO(XUWinRectFrame):
    DEFAULT_PAT = [7,7,12]

    def __init__(self, state:XUStateRO):
        pat = [_active_color(state, c)  for c in self.DEFAULT_PAT]  # アクティブカラーに
        super().__init__(state, pat, pyxel.width, pyxel.height)

    def draw(self):
        self.clip.h = int(self.update_count*self.speed)
        self.clip = self.clip.intersect(XURect(0, 0, pyxel.width, pyxel.height))
        self.draw_buf(pyxel.screen.data_ptr())

class Rect(RectRO, XUState):
    def __init__(self, state:XUStateRO, speed:float):
        super().__init__(state)
        self.set_attr("speed", speed)

# デコレータを用意
def rect_update_bind(xmlui:XMLUI, tag_name:str, speed:float=16):
    def wrapper(update_func:Callable[[Rect,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(Rect(state, speed), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def rect_draw_bind(xmlui:XMLUI, tag_name:str):
    def wrapper(draw_func:Callable[[RectRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(RectRO(state), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper
