import pyxel

from xmlui_core import *

# 角丸ウインドウ
class Round(XUWinRoundFrame):
    def __init__(self, state:XUState, speed:float):
        super().__init__(state, pyxel.width, pyxel.height)
        self.set_attr("speed", speed)

# 四角ウインドウ
class Rect(XUWinRectFrame):
    def __init__(self, state:XUState, speed:float):
        super().__init__(state, pyxel.width, pyxel.height)
        self.set_attr("speed", speed)


# デコレータを用意
# *****************************************************************************
class Decorators:
    def __init__(self, xmlui:XMLUI, group:str):
        self.xmlui = xmlui
        self.group = group

    def round(self, tag_name:str, speed:float=16):
        def wrapper(bind_func:Callable[[Round,XUEvent], None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                bind_func(Round(state, speed), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw)
        return wrapper

    def rect(self, tag_name:str, speed:float=16):
        def wrapper(bind_func:Callable[[Rect,XUEvent], None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                bind_func(Rect(state, speed), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw)
        return wrapper
