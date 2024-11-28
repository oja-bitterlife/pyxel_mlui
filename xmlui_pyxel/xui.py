import xmlui_core as core
from xmlui_core import XUEvent

from . import win

class Label(core.XUState):
    def __init__(self, state:core.XUState, text:str, pat:list[int]=[7,7,12]):
        super().__init__(state.xmlui, state._element)

