from xmlui_core import *

import pyxel
_WINDOW_SPEED = 16

# アクティブカラーにする
def _active_color(state:XUStateRO, color:int):
        return 10 if  state.xmlui.debug and state.xmlui.active_state == state and color == 7 else color

# ウインドウ基底
# *****************************************************************************
class _BaseRound(XUWinRound):
    DEFAULT_PAT = [7,7,12]

    def __init__(self, state:XUStateRO):
        pat = [_active_color(state, c)  for c in self.DEFAULT_PAT]  # アクティブカラーに
        super().__init__(state, pat, pyxel.width, pyxel.height)

    def draw_win(self):
        self.clip.h = self.update_count*_WINDOW_SPEED
        self.draw_buf(pyxel.screen.data_ptr())

class _BaseRect(XUWinRect):
    DEFAULT_PAT = [7,7,12]

    def __init__(self, state:XUStateRO):
        pat = [_active_color(state, c)  for c in self.DEFAULT_PAT]  # アクティブカラーに
        super().__init__(state, pat, pyxel.width, pyxel.height)

    def draw_win(self):
        self.clip.h = self.update_count*_WINDOW_SPEED
        self.draw_buf(pyxel.screen.data_ptr())


# グリッドメニュー付きウインドウ
# *****************************************************************************
class MenuRO(_BaseRound):
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


# メッセージウインドウ
# *****************************************************************************
class MsgRO(_BaseRound):
    def __init__(self, state:XUStateRO):
        super().__init__(state)
#        self._grid = XUSelectGrid(state, tag_group, tag_item)

class Msg(MsgRO):
    def __init__(self, state:XUState):
        super().__init__(state)


# デコレータを用意
def msg_update_bind(xmlui:XMLUI, tag_name:str):
    def wrapper(update_func:Callable[[Msg,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(Msg(state), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def msg_draw_bind(xmlui:XMLUI, tag_name:str):
    def wrapper(draw_func:Callable[[MsgRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(MsgRO(state), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper
