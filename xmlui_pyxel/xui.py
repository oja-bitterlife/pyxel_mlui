import pyxel

# ライブラリコア
import xmlui_core as core
from xmlui_core import XUEvent

# パッケージ一覧
from . import win

font = pyxel.Font("assets/font/b12.bdf")
FONT_SIZE = 12

class Label(core.XUState):
    def __init__(self, state:core.XUState, text:str, pat:list[int]=[7,7,12]):
        super().__init__(state.xmlui, state._element)

