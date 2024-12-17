import pyxel

from xmlui.lib.text import FontBase

# Pyxelのフォントを使う
# #############################################################################
class PyxelFont(FontBase):
    def __init__(self, font_path:str):
        self.font_path = font_path
        super().__init__(pyxel.Font(font_path), FontBase.get_bdf_size(font_path))
 
    def text_width(self, text:str) -> int:
        return self.font.text_width(text)

# Pyxelの255パレットを最大まで使う
# #############################################################################
def set_ex_palette():
    # 16 デフォルトパレット
    palette = pyxel.colors.to_list()[:16]

    # 15 デジタルパレット(16階調の0抜き)
    palette += [0x800000, 0x008000, 0x808000, 0x000080, 0x800080, 0x008080, 0xc0c0c0, 0x808080, 0xff0000, 0x00ff00, 0xffff00, 0x0000ff, 0xff00ff, 0x00ffff, 0xffffff]

    # 15 セピア
    palette += list(map(lambda v: int(v*0.93)<<16 | int(v*0.69)<<8 | int(v*0.4), [(v+1)*16 for v in range(15)]))

    # 210-1=209 人の色覚は緑が強い云々
    for r in [0, 61, 122, 183, 244]:  # 5
        for g in [0, 41, 82, 123, 164, 205, 246]:  # 7
            for b in [0, 49, 98, 147, 196, 245]:  # 6
                # 黒は0が持ってるのでナシで
                if r == g == b == 0:
                    continue
                palette.append(r<<16 | g<<8 | b)

    # 16+15+15+209 = 255
    pyxel.colors.from_list(palette)
