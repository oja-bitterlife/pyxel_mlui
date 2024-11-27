from xmlui_core import *

import pyxel
_WINDOW_SPEED = 16

# アクティブカラーにする
def _active_color(state:XUState, color:int):
        return 10 if  state.xmlui.debug and state.xmlui.active_state == state and color == 7 else color

class Window(XUState):
    def __init__(self, state:XUState, pat:list[int]=[7,7,12]):
        super().__init__(state.xmlui, state._element)

        pat = [_active_color(state, c)  for c in pat]  # アクティブカラーに
        self.win = XUWinRound(pat, pyxel.width, pyxel.height)

    def draw_win(self):
        screen_buf = pyxel.screen.data_ptr()

        self.win.clip.h = self.update_count*_WINDOW_SPEED
        area = self.area
        self.win.draw_buf(area.x, area.y, area.w, area.h, screen_buf)

class MenuWindow(Window):
    def __init__(self, state:XUState, tag_group:str, tag_item:str, item_w:int, item_h:int, pat:list[int]=[7,7,12]):
        super().__init__(state, pat)
        self.grid = XUSelectGrid(state, tag_group, tag_item)
        self.grid.arrange_items(item_w, item_h)

    def select_by_event(self, left:str, right:str, up:str, down:str):
        if self.xmlui.active_state == self:
            self.grid.select_by_event(self.xmlui._event.trg, left, right, up, down)

    @property
    def selected_item(self):
        return self.grid.selected_item

    # 文字列との比較はイベントチェックに使う
    def __eq__(self, obj):
        if isinstance(obj, str):
            return self.selected_item.value == obj
        else:
            return super().__eq__(obj)

class Label(XUState):
    def __init__(self, state:XUState, text:str, pat:list[int]=[7,7,12]):
        super().__init__(state.xmlui, state._element)

