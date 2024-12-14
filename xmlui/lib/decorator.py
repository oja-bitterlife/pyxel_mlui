from typing import Callable
from xmlui.core import XUTemplate,XUState,XUEvent

class DefaultDecorator:
    DEFAULT_GROUP = ""

    def __init__(self, template:XUTemplate):
        self.template = template

    def tag_draw(self, tag_name:str):
        def wrapper(bind_func:Callable[[XUState,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                return bind_func(state, event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper
