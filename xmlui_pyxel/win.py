from xmlui_core import *

import pyxel
_WINDOW_SPEED = 16

# アクティブカラーにする
def _active_color(state:XUStateRO, color:int):
        return 10 if  state.xmlui.debug and state.xmlui.active_state == state and color == 7 else color

class _Base(XUWinRound):
    DEFAULT_PAT = [7,7,12]

    def __init__(self, state:XUStateRO):
        pat = [_active_color(state, c)  for c in self.DEFAULT_PAT]  # アクティブカラーに
        super().__init__(state, pat, pyxel.width, pyxel.height)

    def draw_win(self):
        self.clip.h = self.update_count*_WINDOW_SPEED
        self.draw_buf(pyxel.screen.data_ptr())

class MenuRO(_Base):
    def __init__(self, state:XUStateRO, tag_group:str, tag_item:str):
        super().__init__(state)
        self._grid = XUSelectGrid(state, tag_group, tag_item)

class Menu(MenuRO):
    def __init__(self, state:XUState, tag_group:str, tag_item:str):
        super().__init__(state, tag_group, tag_item)

    def select_by_event(self, left:str, right:str, up:str, down:str):
        if self.xmlui.active_state == self:
            self._grid.select_by_event(self.xmlui._event.trg, left, right, up, down)

    def arrange_items(self, w:int, h:int):
        self._grid.arrange_items(w, h)

    @property
    def selected_item(self):
        return self._grid.selected_item





# XMLUIへのタグ登録のための、登録関数ジェネレーター
def gen_menu_update(func, tag_group:str, tag_item:str):
    def update(state:XUState,event:XUEvent):
        func(Menu(state, tag_group, tag_item), event)
    return update

def gen_menu_draw(func, tag_group:str, tag_item:str):
    def draw(state:XUStateRO,event:XUEvent):
        func(Menu(state.asRW(), tag_group, tag_item), event)
    return draw

# デコレータを用意
def menu_update_func(xmlui:XMLUI, tag_name:str, tag_group:str, tag_item:str):
    def wrapper(update_func:Callable[[Menu,XUEvent], None]):
        xmlui.set_updatefunc(tag_name, gen_menu_update(update_func, tag_group, tag_item))
    return wrapper

def menu_draw_func(xmlui:XMLUI, tag_name:str, tag_group:str, tag_item:str):
    def wrapper(draw_func:Callable[[Menu,XUEvent], None]):
        xmlui.set_drawfunc(tag_name, gen_menu_draw(draw_func, tag_group, tag_item))
    return wrapper
