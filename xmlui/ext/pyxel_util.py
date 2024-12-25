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

        # 15 デジタルパレット(16階調の0抜き)
        self.digital_offset = len(self.palette)
        self.palette += [0x800000, 0x008000, 0x808000, 0x000080, 0x800080, 0x008080, 0xc0c0c0, 0x808080, 0xff0000, 0x00ff00, 0xffff00, 0x0000ff, 0xff00ff, 0x00ffff, 0xffffff]

        # 15 セピア
        self.sepia_offset = len(self.palette)
        self.palette += list(map(lambda v: int(v*0.93)<<16 | int(v*0.69)<<8 | int(v*0.4), [(v+1)*16 for v in range(15)]))

        # 14 白黒
        self.gray_offset = len(self.palette)
        self.palette += [c<<16|c<<8|c for c in [17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 187, 204, 221, 238]]

        # 180-1
        self.colors_offset = len(self.palette)
        for r in [0, 60, 120, 180, 240]:  # 5
            for g in [0, 48, 96, 144, 192, 240]:  # 6
                for b in [0, 48, 96, 144, 192, 240]:  # 6
                    # 黒は0が持ってるのでナシで
                    if r == g == b == 0:
                        continue
                    self.palette.append(r<<16 | g<<8 | b)

        # 16+15+15+14+179 = 239
        self.free_offset = len(self.palette)
        self.reset()

    # システムにパレットを設定する
    def reset(self) -> Self:
        pyxel.colors.from_list(self.palette)
        return self

    # パレット取得
    # -----------------------------------------------------
    # セピアカラーパレット取得
    @property
    def pal_sepia16(self) -> list[int]:
        return [0] + [self.sepia_offset + i for i in range(15)]

    # デジタルカラーパレット取得
    @property
    def pal_digital16(self) -> list[int]:
        return [0] + [self.digital_offset + i for i in range(15)]

    @property
    def pal_digital8(self) -> list[int]:
        return [0] + [self.digital_offset+8 + i for i in range(15)]

    # モノクロパレット取得
    @property
    def pal_gray16(self) -> list[int]:
        return [0] + [self.gray_offset + i for i in range(14)] + [self.pal_white]

    # 単色
    # -----------------------------------------------------
    # 海外フリーゲームでよく使われるカラーキー
    @property
    def pal_magenta(self) -> int:
        return self.digital_offset+12

    # フリーゲームや映像でよく使われるカラーキー
    @property
    def pal_green(self) -> int:
        return self.digital_offset+9

    # 白
    @property
    def pal_white(self) -> int:
        return self.digital_offset+14
