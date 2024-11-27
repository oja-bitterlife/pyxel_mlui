from xmlui_core import *

import pyxel
_WINDOW_SPEED = 16

class Window(XUState):
    def __init__(self, state:XUState, pat:list[int]=[7,7,12]):
        super().__init__(state.xmlui, state._element)
        self.win = XUWinRound(pat, pyxel.width, pyxel.height)

    def draw_win(self):
        screen_buf = pyxel.screen.data_ptr()

        self.win.clip.h = self.update_count*_WINDOW_SPEED
        area = self.area
        self.win.draw_buf(area.x, area.y, area.w, area.h, screen_buf)

class Label(XUState):
    def __init__(self, state:XUState, text:str, pat:list[int]=[7,7,12]):
        super().__init__(state.xmlui, state._element)

