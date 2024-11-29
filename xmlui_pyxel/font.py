import pyxel

font = None
font_size = 0

def set_font(font_path:str, font_size_:int):
    global font
    global font_size
    font = pyxel.Font(font_path)
    font_size = font_size_
