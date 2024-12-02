import pyxel

from xmlui_core import *
from . import text


# グリッドメニュー付きウインドウ
# *****************************************************************************
class GridRO(XUSelectBase):
    def __init__(self, state:XUStateRO, item_tag:str, rows_attr:str):
        super().__init__(state, item_tag, self.attr_int(rows_attr, 1))

    def draw(self):
        area = self.area  # areaを扱うときは必ず一旦ローカル化する
        for item in self._items:
            item_area = item.area  # areaを扱うときは必ず一旦ローカル化する
            # if self.clip.h >= item_area.y-area.y + text.default.size:  # ウインドウが表示されるまで表示しない
            pyxel.text(item_area.x+6, item_area.y, item.text, 7, text.default.data)

class Grid(XUSelectGrid):
    def __init__(self, state:XUStateRO, item_tag:str, rows_attr:str, item_w_attr:str, item_h_attr:str):
        super().__init__(state, item_tag, rows_attr, item_w_attr, item_h_attr)

# デコレータを用意
def grid_update_bind(xmlui:XMLUI, tag_name:str, item_tag:str, rows_attr:str, item_w_attr:str, item_h_attr:str):
    def wrapper(update_func:Callable[[Grid,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(Grid(state, item_tag, rows_attr, item_w_attr, item_h_attr), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def grid_draw_bind(xmlui:XMLUI, tag_name:str, item_tag:str, rows_attr:str):
    def wrapper(draw_func:Callable[[GridRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(GridRO(state, item_tag, rows_attr), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper


# リストウインドウ
# *****************************************************************************
class ListRO(XUSelectBase):
    def __init__(self, state:XUStateRO, item_tag:str, rows_attr:str):
        super().__init__(state, item_tag, self.attr_int(rows_attr, 1))

    def draw(self):
        area = self.area  # areaを扱うときは必ず一旦ローカル化する
        for item in self._items:
            item_area = item.area  # areaを扱うときは必ず一旦ローカル化する
            # if self.clip.h >= item_area.y-area.y + text.default.size:  # ウインドウが表示されるまで表示しない
            pyxel.text(item_area.x+6, item_area.y, item.text, 7, text.default.data)

class List(XUSelectList):
    def __init__(self, state:XUStateRO, item_tag:str, item_h_attr:str):
        super().__init__(state, item_tag, item_h_attr)

# デコレータを用意
def list_update_bind(xmlui:XMLUI, tag_name:str, tag_item:str, item_h_attr:str):
    def wrapper(update_func:Callable[[List,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(List(state, tag_item, item_h_attr), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def list_draw_bind(xmlui:XMLUI, tag_name:str, tag_item:str, item_h_attr:str):
    def wrapper(draw_func:Callable[[ListRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(ListRO(state, tag_item, item_h_attr), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper
