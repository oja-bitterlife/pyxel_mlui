from typing import Callable
from xmlui.core import XMLUI,XUState,XUEvent

class DefaultDecorator:
    DEFAULT_GROUP = ""

    def __init__(self, xmlui:XMLUI, group:str|None=None):
        self.xmlui = xmlui
        self.group = group if group is not None else self.DEFAULT_GROUP

    def tag_draw(self, tag_name:str):
        def wrapper(bind_func:Callable[[XUState,XUEvent], None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                bind_func(state, event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw, self.group)
        return wrapper
