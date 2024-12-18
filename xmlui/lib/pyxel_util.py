from typing import Any,Self

import pyxel
from xmlui.core import XUEvent, XUEventItem
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

        # 210-1=209 人の色覚は緑が強い云々
        self.colors_offset = len(self.palette)
        for r in [0, 61, 122, 183, 244]:  # 5
            for g in [0, 41, 82, 123, 164, 205, 246]:  # 7
                for b in [0, 49, 98, 147, 196, 245]:  # 6
                    # 黒は0が持ってるのでナシで
                    if r == g == b == 0:
                        continue
                    self.palette.append(r<<16 | g<<8 | b)

        # 16+15+15+209 = 255
        self.reset()

    # システムにパレットを設定する
    def reset(self) -> Self:
        pyxel.colors.from_list(self.palette)
        return self

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


# Pyxelの入力をXMLUIのイベントに変換する
# #############################################################################
class PyxelInput:
    # キーコンフィグ時はここの設定書き換える
    LEFT = [pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, pyxel.KEY_LEFT, pyxel.KEY_A]
    RIGHT = [pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT, pyxel.KEY_RIGHT, pyxel.KEY_D]
    UP = [pyxel.GAMEPAD1_BUTTON_DPAD_UP, pyxel.KEY_UP, pyxel.KEY_W]
    DOWN = [pyxel.GAMEPAD1_BUTTON_DPAD_DOWN, pyxel.KEY_DOWN, pyxel.KEY_S]
    # XBox準拠...
    BTN_A = [pyxel.GAMEPAD1_BUTTON_A, pyxel.KEY_Z, pyxel.KEY_SPACE, pyxel.KEY_RETURN]
    BTN_B = [pyxel.GAMEPAD1_BUTTON_B, pyxel.KEY_X, pyxel.KEY_BACKSPACE]
    BTN_X = [pyxel.GAMEPAD1_BUTTON_X, pyxel.KEY_Q, pyxel.KEY_C]
    BTN_Y = [pyxel.GAMEPAD1_BUTTON_Y, pyxel.KEY_E, pyxel.KEY_V]

    def __init__(self, xmlui):
        self.xmlui = xmlui

    # 全ボタン一気に調べてイベント設定
    def check(self):
        # UI用キー入力
        for event,keys in self.key_config.items():
            for key in keys:
                if pyxel.btn(key):
                    self.xmlui.on(event)
                    break

    # その時のキー定義に合わせて構築し直すようプロパティで
    @property
    def key_config(self) -> dict[XUEventItem, list[int]]:
        return {
            XUEvent.Key.LEFT: self.LEFT,
            XUEvent.Key.RIGHT: self.RIGHT,
            XUEvent.Key.UP: self.UP,
            XUEvent.Key.DOWN: self.DOWN,
            XUEvent.Key.BTN_A: self.BTN_A,
            XUEvent.Key.BTN_B: self.BTN_B,
            XUEvent.Key.BTN_X: self.BTN_X,
            XUEvent.Key.BTN_Y: self.BTN_Y,
        }
