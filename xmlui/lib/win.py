from xmlui.xmlui_core import *

# 角丸ウインドウ
class Round(XUWinRoundFrame):
    def __init__(self, state:XUState):
        super().__init__(state)

# 四角ウインドウ
class Rect(XUWinRectFrame):
    def __init__(self, state:XUState):
        super().__init__(state)


# デコレータを用意
# *****************************************************************************
class Decorators:
    def __init__(self, xmlui:XMLUI, group:str):
        self.xmlui = xmlui
        self.group = group

    def __del__(self):
        self.xmlui.remove_drawfunc(self.group)

    def round(self, tag_name:str):
        def wrapper(bind_func:Callable[[Round,XUEvent], None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                bind_func(Round(state), event)
            # 関数登録
            self.xmlui.set_drawfunc(self.group, tag_name, draw)
        return wrapper

    def rect(self, tag_name:str):
        def wrapper(bind_func:Callable[[Rect,XUEvent], None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                bind_func(Rect(state), event)
            # 関数登録
            self.xmlui.set_drawfunc(self.group, tag_name, draw)
        return wrapper
