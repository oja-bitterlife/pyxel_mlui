from xmlui_core import *

from . import win

class Label(XUState):
    def __init__(self, state:XUState, text:str, pat:list[int]=[7,7,12]):
        super().__init__(state.xmlui, state._element)

