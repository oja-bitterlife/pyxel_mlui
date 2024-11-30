import pyxel

# ライブラリコア
import xmlui_core as xuc

class Label(xuc.XUState):
    def __init__(self, state:xuc.XUState, text:str, pat:list[int]=[7,7,12]):
        super().__init__(state.xmlui, state._element)

