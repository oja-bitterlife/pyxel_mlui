from xmlui.core import *

# グリッドメニュー付きウインドウ
class Grid(XUSelectGrid):
    ROWS_ATTR = 'rows'
    ITEM_W_ATTR = 'item_w'
    ITEM_H_ATTR = 'item_h'

    def __init__(self, elem:XUElem, init_item_tag:str):
        rows = elem.attr_int(self.ROWS_ATTR, 1)
        item_w = elem.attr_int(self.ITEM_W_ATTR, 0)
        item_h = elem.attr_int(self.ITEM_H_ATTR, 0)
        super().__init__(elem, init_item_tag, rows, item_w, item_h)

# リストウインドウ
class List(XUSelectList):
    ITEM_H_ATTR = 'item_h'

    def __init__(self, elem:XUElem, init_item_tag:str):
        item_h = elem.attr_int(self.ITEM_H_ATTR, 0)
        super().__init__(elem, init_item_tag, item_h)

# リストウインドウ
class RowList(XUSelectRowList):
    ITEM_W_ATTR = 'item_w'

    def __init__(self, elem:XUElem, init_item_tag:str):
        item_w = elem.attr_int(self.ITEM_W_ATTR, 0)
        super().__init__(elem, init_item_tag, item_w)


# デコレータを用意
# *****************************************************************************
class Decorator(XUTemplate.HasRef):
    def grid(self, tag_name:str, init_item_tag:str):
        def wrapper(bind_func:Callable[[Grid,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(Grid(elem, init_item_tag), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper

    def list(self, tag_name:str, init_item_tag:str):
        def wrapper(bind_func:Callable[[List,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(List(elem, init_item_tag), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper

    def row_list(self, tag_name:str, init_item_tag:str):
        def wrapper(bind_func:Callable[[RowList,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(RowList(elem, init_item_tag), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper

