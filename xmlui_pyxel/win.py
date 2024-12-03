import pyxel

from xmlui_core import *
from . import text

# 角丸ウインドウ
# *****************************************************************************
class Round(XUWinRoundFrame):
    DEFAULT_PAT = [7,7,12]

    def __init__(self, state:XUState, speed:float):
        super().__init__(state, self.DEFAULT_PAT, pyxel.width, pyxel.height)
        self.set_attr("speed", speed)

    def anim_clip(self):
        self.clip.h = int(self.update_count*self.speed)
        self.clip = self.clip.intersect(XURect(0, 0, pyxel.width, pyxel.height))

# デコレータを用意
def round(xmlui:XMLUI, tag_name:str, speed:float=16):
    def wrapper(bind_func:Callable[[Round,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUState, event:XUEvent):
            bind_func(Round(state, speed), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper


# 四角ウインドウ
# *****************************************************************************
class Rect(XUWinRectFrame):
    DEFAULT_PAT = [7,7,12]

    def __init__(self, state:XUState, speed:float):
        super().__init__(state, self.DEFAULT_PAT, pyxel.width, pyxel.height)
        self.set_attr("speed", speed)

    def anim_clip(self):
        self.clip.h = int(self.update_count*self.speed)
        self.clip = self.clip.intersect(XURect(0, 0, pyxel.width, pyxel.height))

# デコレータを用意
def rect(xmlui:XMLUI, tag_name:str, speed:float=16):
    def wrapper(bind_func:Callable[[Rect,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUState, event:XUEvent):
            bind_func(Rect(state, speed), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper

