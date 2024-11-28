import pyxel

from xmlui_core import *
from . import xui

# ウインドウ基底
# *****************************************************************************
_WINDOW_SPEED = 16

# アクティブカラーにする
def _active_color(state:XUStateRO, color:int):
        return 10 if  state.xmlui.debug and state.xmlui.active_state == state and color == 7 else color

class _BaseRound(XUWinRound):
    DEFAULT_PAT = [7,7,12]

    def __init__(self, state:XUStateRO):
        pat = [_active_color(state, c)  for c in self.DEFAULT_PAT]  # アクティブカラーに
        super().__init__(state, pat, pyxel.width, pyxel.height)

    def draw(self):
        self.clip.h = self.update_count*_WINDOW_SPEED
        self.draw_buf(pyxel.screen.data_ptr())

class _BaseRect(XUWinRect):
    DEFAULT_PAT = [7,7,12]

    def __init__(self, state:XUStateRO):
        pat = [_active_color(state, c)  for c in self.DEFAULT_PAT]  # アクティブカラーに
        super().__init__(state, pat, pyxel.width, pyxel.height)

    def draw(self):
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
    LINE_NUM_ATTR = "lines"
    WRAP_ATTR = "wrap"

    def __init__(self, state:XUStateRO, tag_text:str):
        super().__init__(state)

        page_root = state.find_by_tag(tag_text)
        self.page = XUPageRO(page_root)  # ROにして保存し直す

    def draw(self):
        super().draw()
        for i,page in enumerate(self.page.page_text.split()):
            area = self.page.state.area
            pyxel.text(area.x, area.y+i*xui.FONT_SIZE, page, 7, xui.font)

class Msg(MsgRO):
    def __init__(self, state:XUState, tag_text:str):
        # PAGEがなければ新規作成。あればそれを使う
        page_root = state.find_by_tag(tag_text)
        page = XUPage(page_root, page_root.text, page_root.attr_int(self.LINE_NUM_ATTR, 1), page_root.attr_int("wrap"))

        super().__init__(state, tag_text)

        # 親でself.pageが上書きされるので、あとからself.pageに突っ込む
        self.page = page.nextcount()

# デコレータを用意
def msg_update_bind(xmlui:XMLUI, tag_name:str, tag_text:str):
    def wrapper(update_func:Callable[[Msg,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(Msg(state, tag_text), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def msg_draw_bind(xmlui:XMLUI, tag_name:str, tag_text:str):
    def wrapper(draw_func:Callable[[MsgRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(MsgRO(state, tag_text), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper
