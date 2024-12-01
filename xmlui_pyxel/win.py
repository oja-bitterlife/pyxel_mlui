import pyxel

from xmlui_core import *
from . import text

# ウインドウ基底
# *****************************************************************************
# アクティブカラーにする
def _active_color(state:XUStateRO, color:int):
        return 10 if  state.xmlui.debug.is_lib_debug and state.xmlui.active_state == state and color == 7 else color

class _BaseRound(XUWinRoundFrame):
    DEFAULT_PAT = [7,7,12]

    def __init__(self, state:XUStateRO, speed:float=16):
        pat = [_active_color(state, c)  for c in self.DEFAULT_PAT]  # アクティブカラーに
        super().__init__(state, pat, pyxel.width, pyxel.height)

        self.set_attr("speed", speed)

    def draw(self):
        self.clip.h = int(self.update_count*self.speed)
        self.draw_buf(pyxel.screen.data_ptr())

class _BaseRect(XUWinRectFrame):
    DEFAULT_PAT = [7,7,12]

    def __init__(self, state:XUStateRO, speed:float=16):
        pat = [_active_color(state, c)  for c in self.DEFAULT_PAT]  # アクティブカラーに
        super().__init__(state, pat, pyxel.width, pyxel.height)

        self.set_attr("speed", speed)

    def draw(self):
        self.clip.h = int(self.update_count*self.speed)
        self.draw_buf(pyxel.screen.data_ptr())
