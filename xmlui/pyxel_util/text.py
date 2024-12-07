import pyxel

from lib.text import FontBase

# Pyxelのフォントを使う
# #############################################################################
class PyxelFont(FontBase):
    def __init__(self, font_path:str):
        super().__init__(pyxel.Font(font_path), FontBase.get_bdf_size(font_path))
 
    def text_width(self, text:str) -> int:
        return self.font.text_width(text)
