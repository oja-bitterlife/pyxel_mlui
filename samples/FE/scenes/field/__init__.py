import pyxel

from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUEFadeScene

class Field(XUEFadeScene):
    def __init__(self):
        super().__init__(DebugXMLUI(pyxel.width, pyxel.height))

