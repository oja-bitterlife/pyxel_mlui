from xmlui.core import *
from xmlui.lib.decorator import DefaultDecorator

# 角丸ウインドウ
class Round(XUWinRound):
    def __init__(self, state:XUState):
        super().__init__(state)

# 四角ウインドウ
class Rect(XUWinRect):
    def __init__(self, state:XUState):
        super().__init__(state)

# アニメ付き角丸ウインドウ
class RoundAnim(XUWinRound):
    def __init__(self, state:XUState):
        super().__init__(state)
        self.update()

# アニメ付き四角ウインドウ
class RectAnim(XUWinRect):
    def __init__(self, state:XUState):
        super().__init__(state)
        self.update()


# デコレータを用意
# *****************************************************************************
class Decorator(DefaultDecorator):
    def __init__(self, xmlui:XMLUI, group:str|None=None):
        super().__init__(xmlui, group)

    def round(self, tag_name:str):
        def wrapper(bind_func:Callable[[Round,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                return bind_func(Round(state), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw, self.group)
        return wrapper

    def rect(self, tag_name:str):
        def wrapper(bind_func:Callable[[Rect,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                return bind_func(Rect(state), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw, self.group)
        return wrapper

    def round_anim(self, tag_name:str):
        def wrapper(bind_func:Callable[[RoundAnim,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                return bind_func(RoundAnim(state), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw, self.group)
        return wrapper

    def rect_anim(self, tag_name:str):
        def wrapper(bind_func:Callable[[RectAnim,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                return bind_func(RectAnim(state), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw, self.group)
        return wrapper
