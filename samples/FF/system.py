import pyxel
from xmlui.ext.pyxel_util import PyxelFont,PyxelPalette

system_font = PyxelFont("assets/font/misaki_gothic_2nd.bdf")
system_palette = PyxelPalette()

# ハンドカーソル。システム全体で使い回そう
hand_cursor = pyxel.Image.from_image(filename="assets/images/hand-cursor.png")
def draw_hand_cursor(x:int, y:int):
    pyxel.blt(x-16, y-5, hand_cursor, 0, 0, 16, 16, system_palette.pal_magenta)
