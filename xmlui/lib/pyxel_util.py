from typing import Any,Self

import pyxel
from xmlui.core import XMLUI,XUEvent,XUEventItem
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


# Pyxelの入力をXMLUIのイベントに変換する。
# ちゃんと設定しないとUIとゲームで操作が違ってしまうので、
# 使用はお勧めできない、開発者用。
# #############################################################################
# インプット状態チェック用。状態を持たないのでどこで何個つくってもよい
class PyxelInputInfo:
    # キーコンフィグ時はここの設定書き換える
    CFG_LEFT = [pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, pyxel.KEY_LEFT, pyxel.KEY_A]
    CFG_RIGHT = [pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT, pyxel.KEY_RIGHT, pyxel.KEY_D]
    CFG_UP = [pyxel.GAMEPAD1_BUTTON_DPAD_UP, pyxel.KEY_UP, pyxel.KEY_W]
    CFG_DOWN = [pyxel.GAMEPAD1_BUTTON_DPAD_DOWN, pyxel.KEY_DOWN, pyxel.KEY_S]
    # XBox準拠...
    CFG_A = [pyxel.GAMEPAD1_BUTTON_A, pyxel.KEY_Z, pyxel.KEY_SPACE, pyxel.KEY_RETURN]
    CFG_B = [pyxel.GAMEPAD1_BUTTON_B, pyxel.KEY_X, pyxel.KEY_BACKSPACE]
    CFG_X = [pyxel.GAMEPAD1_BUTTON_X, pyxel.KEY_Q, pyxel.KEY_C]
    CFG_Y = [pyxel.GAMEPAD1_BUTTON_Y, pyxel.KEY_E, pyxel.KEY_V]

    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui

    # その時のキー定義に合わせて構築し直すようプロパティで
    @property
    def key_config(self) -> dict[XUEventItem, list[int]]:
        return {
            XUEvent.Key.LEFT: self.CFG_LEFT,
            XUEvent.Key.RIGHT: self.CFG_RIGHT,
            XUEvent.Key.UP: self.CFG_UP,
            XUEvent.Key.DOWN: self.CFG_DOWN,
            XUEvent.Key.BTN_A: self.CFG_A,
            XUEvent.Key.BTN_B: self.CFG_B,
            XUEvent.Key.BTN_X: self.CFG_X,
            XUEvent.Key.BTN_Y: self.CFG_Y,
        }

    # pyxelのキーがどのイベントに割り当てられているか調べる
    def _find_keyevent(self, pyxel_key:int):
        for event,keys in self.key_config.items():
            if pyxel_key in keys:
                return event
    
    # 現在入力中
    def input(self, pyxel_key:int):
        key_event = self._find_keyevent(pyxel_key)
        if key_event:
            return key_event in self.xmlui.event.now
        return False

    # 押された
    def trg(self, pyxel_key:int):
        key_event = self._find_keyevent(pyxel_key)
        if key_event:
            return key_event in self.xmlui.event.trg
        return False

    # はなされた
    def release(self, pyxel_key:int):
        key_event = self._find_keyevent(pyxel_key)
        if key_event:
            return key_event in self.xmlui.event.release
        return False

# インプット管理クラス。どこかでcheck()を呼び出す
class PyxelInput(PyxelInputInfo):
    # 全ボタン一気に調べてイベント設定
    def check(self):
        for event,keys in self.key_config.items():
            # 定義されたキーのどれか１つでも押されていたら押された扱い
            for key in keys:
                if pyxel.btn(key):
                    self.xmlui.on(event)
                    break
