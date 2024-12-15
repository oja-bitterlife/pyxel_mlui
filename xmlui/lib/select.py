from xmlui.core import *

# セレクトアイテム
class Item(XUSelectItem):
    def __init__(self, state:XUElement):
        super().__init__(state)

# グリッドメニュー付きウインドウ
class Grid(XUSelectGrid):
    ROWS_ATTR = 'rows'
    ITEM_W_ATTR = 'item_w'
    ITEM_H_ATTR = 'item_h'

    def __init__(self, state:XUElement, item_tag:str):
        super().__init__(state, item_tag, self.ROWS_ATTR, self.ITEM_W_ATTR, self.ITEM_H_ATTR)

# リストウインドウ
class List(XUSelectList):
    ITEM_W_ATTR = 'item_w'
    ITEM_H_ATTR = 'item_h'

    def __init__(self, state:XUElement, item_tag:str):
        super().__init__(state, item_tag, self.ITEM_W_ATTR, self.ITEM_H_ATTR)


# デコレータを用意
# *****************************************************************************
class Decorator(XUTemplate.HasRef):
    def item(self, item_tag:str):
        def wrapper(bind_func:Callable[[Item,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(state:XUElement, event:XUEvent):
                return bind_func(Item(state), event)
            # 関数登録
            self.template.set_drawfunc(item_tag, draw)
        return wrapper

    def grid(self, tag_name:str, item_tag:str):
        def wrapper(bind_func:Callable[[Grid,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(state:XUElement, event:XUEvent):
                return bind_func(Grid(state, item_tag), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper

    def list(self, tag_name:str, item_tag:str):
        def wrapper(bind_func:Callable[[List,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(state:XUElement, event:XUEvent):
                return bind_func(List(state, item_tag), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper

