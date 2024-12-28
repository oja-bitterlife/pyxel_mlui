import pyxel
from xmlui.ext.pyxel_util import PyxelFont,PyxelPalette

system_font = PyxelFont("assets/font/misaki_gothic_2nd.bdf")
system_palette = PyxelPalette()

# ハンドカーソル。システム全体で使い回そう
class HandCursor:
    def __init__(self) -> None:
        self.img = pyxel.Image.from_image(filename="assets/images/hand-cursor.png")
    def draw(self, x:int, y:int):
        pyxel.blt(x-16, y-5, self.img, 0, 0, 16, 16, system_palette.pal_magenta)
hand_cursor = HandCursor()

