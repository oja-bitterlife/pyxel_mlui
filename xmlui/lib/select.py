from xmlui.core import *

# グリッドメニュー付きウインドウ
class Grid(XUSelectGrid):
    ROWS_ATTR = 'rows'
    ITEM_W_ATTR = 'item_w'
    ITEM_H_ATTR = 'item_h'

    def __init__(self, elem:XUElem, item_tag:str):
        rows = elem.attr_int(self.ROWS_ATTR, 1)
        item_w = elem.attr_int(self.ITEM_W_ATTR, 0)
        item_h = elem.attr_int(self.ITEM_H_ATTR, 0)
        super().__init__(elem, item_tag, rows, item_w, item_h)

# リストウインドウ
class List(XUSelectList):
    ITEM_W_ATTR = 'item_w'
    ITEM_H_ATTR = 'item_h'

    def __init__(self, elem:XUElem, item_tag:str):
        item_w = elem.attr_int(self.ITEM_W_ATTR, 0)
        item_h = elem.attr_int(self.ITEM_H_ATTR, 0)
        super().__init__(elem, item_tag, item_w, item_h)


# デコレータを用意
# *****************************************************************************
class Decorator(XUTemplate.HasRef):
    def grid(self, tag_name:str, item_tag:str):
        def wrapper(bind_func:Callable[[Grid,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(Grid(elem, item_tag), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper

    def list(self, tag_name:str, item_tag:str):
        def wrapper(bind_func:Callable[[List,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(List(elem, item_tag), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper

