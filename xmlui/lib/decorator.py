from typing import Callable
from core import XMLUI,XUState,XUEvent

class DefaultDecorator:
    DEFAULT_GROUP = "default"

    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui
        self.group = self.DEFAULT_GROUP

    def tag_draw(self, tag_name:str):
        def wrapper(bind_func:Callable[[XUState,XUEvent], None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                bind_func(state, event)
            # 関数登録
            self.xmlui.set_drawfunc(self.group, tag_name, draw)
        return wrapper
