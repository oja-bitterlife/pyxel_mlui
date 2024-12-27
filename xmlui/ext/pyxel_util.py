from typing import Self

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
class PyxelPalette:
    # ojaパレット
    def __init__(self):
        # 16 デフォルトパレット
        self.palette = pyxel.colors.to_list()[:16]

        # 13 白黒。14番(238,238,238)は7番とかぶるのでナシで
        self.gray_offset = len(self.palette)
        self.palette += [c<<16|c<<8|c for c in [17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 187, 204, 221]]

        # 216-1
        self.colors_offset = len(self.palette)
        for r in [0, 48, 96, 128, 192, 255]:  # 6
            for g in [0, 48, 96, 128, 192, 255]:  # 6
                for b in [0, 48, 96, 128, 192, 255]:  # 6
                    # 黒は0が持ってるのでナシで
                    if r == g == b == 0:
                        continue
                    self.palette.append(r<<16 | g<<8 | b)

        # 16+13+215 = 244
        self.free_offset = len(self.palette)
        self.reset()

        # # チェック
        # for i in range(8):
        #     print(format(self.palette[self.pal_digital8[i]], "08x"))

    # システムにパレットを設定する
    def reset(self) -> Self:
        pyxel.colors.from_list(self.palette)
        return self

    # パレット取得
    # -----------------------------------------------------
    # デジタルカラーパレット取得
    @property
    def pal_digital16(self) -> list[int]:
        add_index = [36*3, 6*3, 36*3+6*3, 3, 36*3+3, 6*3+3, 36*4+6*4+4, 36*3+6*3+3, 36*5, 6*5, 36*5+6*5, 5, 36*5+5, 6*5+5, 36*5+6*5+5]
        return [0] + [self.colors_offset + i-1 for i in add_index]

    @property
    def pal_digital8(self) -> list[int]:
        return [0] + self.pal_digital16[9:]

    # モノクロパレット取得
    @property
    def pal_gray16(self) -> list[int]:
        return [0] + [self.gray_offset + i for i in range(13)] + [7] + [self.pal_white]

    # カラーパレット取得
    @property
    def pal_colors(self) -> list[int]:
        return [0] + [self.colors_offset + i for i in range(6*6*6-1)]

    # 単色
    # -----------------------------------------------------
    # 海外フリーゲームでよく使われるカラーキー(Magenta)
    @property
    def pal_magenta(self) -> int:
        return self.pal_digital8[5]

    # フリーゲームや映像でよく使われるカラーキー(Green)
    @property
    def pal_green(self) -> int:
        return self.pal_digital8[2]

    # 白
    @property
    def pal_white(self) -> int:
        return self.pal_digital8[7]
