from typing import Self

import pyxel
from xmlui.lib.text import _XUFontBase

# Pyxelのフォントを使う
# #############################################################################
class PyxelFont(_XUFontBase):
    def __init__(self, font_path:str):
        self.font_path = font_path
        super().__init__(pyxel.Font(font_path), PyxelFont.get_bdf_size(font_path))
 
     # フォントサイズ算出
    @classmethod
    def get_bdf_size(cls, bdf_font_path) -> int:
        with open(bdf_font_path, "r") as f:
            for i, line in enumerate(f.readlines()):
                if i > 100:  # 100行も見りゃええじゃろ...
                    raise RuntimeError(f"{bdf_font_path} has not PIXEL_SIZE")
                if line.startswith("PIXEL_SIZE"):
                    return int(line.split()[-1])
        raise RuntimeError(f"{bdf_font_path} has not PIXEL_SIZE")

    def text_width(self, text:str) -> int:
        return self.font.text_width(text)


# Pyxelの255パレットをたくさん使う
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

    # 明度操作
    # -----------------------------------------------------
    def _splitRGB6(self, pal:int) -> tuple[int, int, int]:
        pal = min(max(pal-self.colors_offset+1, 0), 6*6*6-1)
        return pal//36, pal%36//6, pal%6

    def brightR(self, pal:int, add:int) -> int:
        r, g, b = self._splitRGB6(pal)
        pal = min(max(r+add, 0), 5)*36 + g*6 + b
        return self.pal_colors[pal]

    def brightG(self, pal:int, add:int) -> int:
        r, g, b = self._splitRGB6(pal)
        pal = r*36 + min(max(g+add, 0), 5)*6 + b
        return self.pal_colors[pal]

    def brightB(self, pal:int, add:int) -> int:
        r, g, b = self._splitRGB6(pal)
        pal = r*36 + g*6 + min(max(b+add, 0), 5)
        return self.pal_colors[pal]

    def bright(self, pal:int, add:int) -> int:
        if pal in self.pal_gray16:
            gray_pal = max(pal - self.gray_offset + 1, 0)
            return self.pal_gray16[min(max(gray_pal+add, 0), 15)]
        else:
            return self.brightR(self.brightG(self.brightB(pal, add), add), add)

    # デバッグ用
    # -----------------------------------------------------
    def getColor(self, pal:int):
        return self.palette[pal]

    def strRGB(self, pal:int):
        return format(self.palette[pal], "06X")

