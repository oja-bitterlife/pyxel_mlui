import pyxel

from xmlui_core import *
from . import text


# セレクトアイテム
# *****************************************************************************
class Item(XUState):
    def __init__(self, state:XUState):
        super().__init__(state.xmlui, state._element)

# デコレータを用意
def item(xmlui:XMLUI, tag_name:str):
    def wrapper(bind_func:Callable[[Item,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUState, event:XUEvent):
            bind_func(Item(state), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
        xmlui.set_drawfunc(XUSelectBase.copyed_tagname(tag_name), draw)  # コピー名も一緒に登録
    return wrapper


# グリッドメニュー付きウインドウ
# *****************************************************************************
class Grid(XUSelectGrid):
    def __init__(self, state:XUState, item_tag:str, rows_attr:str, item_w_attr:str, item_h_attr:str):
        super().__init__(state, item_tag, rows_attr, item_w_attr, item_h_attr)

# デコレータを用意
def grid(xmlui:XMLUI, tag_name:str, item_tag:str, rows_attr:str, item_w_attr:str, item_h_attr:str):
    def wrapper(bind_func:Callable[[Grid,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUState, event:XUEvent):
            bind_func(Grid(state, item_tag, rows_attr, item_w_attr, item_h_attr), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper


# リストウインドウ
# *****************************************************************************
class List(XUSelectList):
    def __init__(self, state:XUState, item_tag:str, item_h_attr:str):
        super().__init__(state, item_tag, item_h_attr)

    def draw(self):
        # area = self.area  # areaを扱うときは必ず一旦ローカル化する
        for item in self._items:
            item_area = item.area  # areaを扱うときは必ず一旦ローカル化する
            # if self.clip.h >= item_area.y-area.y + text.default.size:  # ウインドウが表示されるまで表示しない
            pyxel.text(item_area.x+6, item_area.y, item.text, 7, text.default.font)

# デコレータを用意
def list(xmlui:XMLUI, tag_name:str, tag_item:str, item_h_attr:str):
    def wrapper(bind_func:Callable[[List,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUState, event:XUEvent):
            bind_func(List(state, tag_item, item_h_attr), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper
