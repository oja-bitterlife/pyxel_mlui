import pyxel

from xmlui_core import *
from . import text


# グリッドメニュー付きウインドウ
# *****************************************************************************
class MenuRO(_BaseRound):
    def __init__(self, state:XUStateRO, tag_group:str, tag_item:str):
        super().__init__(state)
        self._grid_root = XUSelectGrid(state, tag_group, tag_item)

    def draw(self):
        super().draw()  # ウインドウ描画

        area = self.area  # areaを扱うときは必ず一旦ローカル化する
        for group in self._grid_root._grid:
            for item in group:
                print(item.area)

                item_area = item.area  # areaを扱うときは必ず一旦ローカル化する
                if self.clip.h >= item_area.y-area.y + text.default.size:  # ウインドウが表示されるまで表示しない
                    pyxel.text(item_area.x+6, item_area.y, item.text, 7, text.default.data)

    @property
    def selected_item(self) -> XUStateRO:
        return self._grid_root.selected_item

class Menu(MenuRO):
    def __init__(self, state:XUState, tag_group:str, tag_item:str):
        super().__init__(state, tag_group, tag_item)

    def arrange_items(self, w:int, h:int):
        self._grid_root.arrange_items(w, h)

    def select_by_event(self, left:str, right:str, up:str, down:str) -> XUState:
        if self.xmlui.active_state == self:
            self._grid_root.select_by_event(self.xmlui.event.trg, left, right, up, down)
        return self.selected_item

    @property
    def selected_item(self) -> XUState:
        return self._grid_root.selected_item

# デコレータを用意
def menu_update_bind(xmlui:XMLUI, tag_name:str, tag_group:str, tag_item:str):
    def wrapper(update_func:Callable[[Menu,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(Menu(state, tag_group, tag_item), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def menu_draw_bind(xmlui:XMLUI, tag_name:str, tag_group:str, tag_item:str):
    def wrapper(draw_func:Callable[[MenuRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(MenuRO(state, tag_group, tag_item), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper


# リストウインドウ
# *****************************************************************************
class ListRO(_BaseRound):
    def __init__(self, state:XUStateRO, tag_item:str):
        super().__init__(state)
        self._grid_root = XUSelectList(state, tag_item)

    def draw(self):
        super().draw()  # ウインドウ描画

        area = self.area  # areaを扱うときは必ず一旦ローカル化する
        for group in self._grid_root._grid:
            item = group[0]
            item_area = item.area  # areaを扱うときは必ず一旦ローカル化する
            if self.clip.h >= item_area.y-area.y + text.default.size:  # ウインドウが表示されるまで表示しない
                pyxel.text(item_area.x+6, item_area.y, item.text, 7, text.default.data)

    @property
    def selected_item(self) -> XUStateRO:
        return self._grid_root.selected_item

class List(ListRO):
    def __init__(self, state:XUState, tag_item:str):
        super().__init__(state, tag_item)

    def arrange_items(self, w:int, h:int):
        self._grid_root.arrange_items(w, h)

    def select_by_event(self, up:str, down:str) -> XUState:
        if self.xmlui.active_state == self:
            self._grid_root.select_by_event(self.xmlui.event.trg, up, down)
        return self.selected_item

    @property
    def selected_item(self) -> XUState:
        return self._grid_root.selected_item

# デコレータを用意
def list_update_bind(xmlui:XMLUI, tag_name:str, tag_item:str):
    def wrapper(update_func:Callable[[List,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(List(state, tag_item), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def list_draw_bind(xmlui:XMLUI, tag_name:str, tag_item:str):
    def wrapper(draw_func:Callable[[ListRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(ListRO(state, tag_item), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper
