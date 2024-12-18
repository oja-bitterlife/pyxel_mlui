from enum import StrEnum
import pyxel

from xmlui.core import XMLUI
from xmlui.lib.pyxel_util import PyxelInput

class SceneBase:
    # シーン管理用
    current_scene:"SceneBase|None" = None

    class State(StrEnum):
        OPENING = "opening"
        OPENED = "opened"
        CLOSING = "closing"
        CLOSED = "closed"

    # フェードインアウト時間
    OPEN_COUNT_MAX = 15
    CLOSE_COUNT_MAX = 15

    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui
        self._state:SceneBase.State = self.State.OPENING

        # フェードインアウト設定
        self.open_count = self.OPEN_COUNT_MAX
        self.close_count = self.CLOSE_COUNT_MAX
        self.fade_color = 0

    # mainから呼び出すもの
    # -----------------------------------------------------
    def update_scene(self):
        # open/close中はupdateを呼び出さない
        if self._state == self.State.OPENED:
            # 更新処理呼び出し
            PyxelInput(self.xmlui).check()  # UI用キー入力
            self.update()

    def draw_scene(self):
        pyxel.dither(1.0)  # 戻しておく

        # シーン終了後はdrawも呼び出さない
        if self._state == self.State.CLOSED:
            pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, self.fade_color)
            self.closed()  # 代わりにclosedを呼び出す
        else:
            self.draw()
            self._draw_after()

    def end_scene(self):
        self._state = self.State.CLOSING

    # オーバーライドして使う物
    # これらはsceneの中から呼び出すように(自分で呼び出さない)
    # -----------------------------------------------------
    def update(self):
        pass
    def draw(self):
        pass
    def closed(self):
        pass

    # 内部処理用。オーバーライドして使ってもいい
    # -----------------------------------------------------
    def _draw_after(self):
        if self._state == self.State.OPENING:
            if self.open_count > 0:
                pyxel.dither(self.open_count/self.OPEN_COUNT_MAX)
                pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, self.fade_color)
                self.open_count -= 1
            else:
                self._state = SceneBase.State.OPENED

        if self._state == self.State.CLOSING:
            if self.close_count > 0:
                pyxel.dither((self.CLOSE_COUNT_MAX-self.close_count)/self.CLOSE_COUNT_MAX)
                pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, self.fade_color)
                self.close_count -= 1
            else:
                pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, self.fade_color)
                self._state = SceneBase.State.CLOSED

