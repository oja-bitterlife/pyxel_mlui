from xmlui_core import *

# セレクトアイテム
class Item(XUSelectItem):
    def __init__(self, state:XUState):
        super().__init__(state.xmlui, state._element)

# グリッドメニュー付きウインドウ
class Grid(XUSelectGrid):
    def __init__(self, state:XUState, item_tag:str, rows_attr:str, item_w_attr:str, item_h_attr:str):
        super().__init__(state, item_tag, rows_attr, item_w_attr, item_h_attr)

# リストウインドウ
class List(XUSelectList):
    def __init__(self, state:XUState, item_tag:str, item_w_attr:str, item_h_attr:str):
        super().__init__(state, item_tag, item_w_attr, item_h_attr)


# デコレータを用意
# *****************************************************************************
class Decorators:
    def __init__(self, xmlui:XMLUI, group:str):
        self.xmlui = xmlui
        self.group = group

    def item(self, item_tag:str):
        def wrapper(bind_func:Callable[[Item,XUEvent], None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                bind_func(Item(state), event)
            # 関数登録
            self.xmlui.set_drawfunc(self.group, item_tag, draw)
        return wrapper

    def grid(self, tag_name:str, item_tag:str, rows_attr:str, item_w_attr:str, item_h_attr:str):
        def wrapper(bind_func:Callable[[Grid,XUEvent], None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                bind_func(Grid(state, item_tag, rows_attr, item_w_attr, item_h_attr), event)
            # 関数登録
            self.xmlui.set_drawfunc(self.group, tag_name, draw)
        return wrapper

    def list(self, tag_name:str, tag_item:str, item_w_attr:str, item_h_attr:str):
        def wrapper(bind_func:Callable[[List,XUEvent], None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                bind_func(List(state, tag_item, item_w_attr, item_h_attr), event)
            # 関数登録
            self.xmlui.set_drawfunc(self.group, tag_name, draw)
        return wrapper

