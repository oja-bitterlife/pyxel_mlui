from enum import StrEnum
import pyxel

from xmlui.core import XMLUI
from xmlui.ext.input import XUXInput
from xmlui.ext.timer import XUXCountUp,XUXCountDown

class XUXScene:
    # デフォルトフェードインアウト時間
    OPEN_COUNT = 15
    CLOSE_COUNT = 15

    # シーン管理用
    current_scene:"XUXScene|None" = None

    # Sceneのopen/close状態
    class State(StrEnum):
        OPENING = "opening"
        OPENED = "opened"
        CLOSING = "closing"
        CLOSED = "closed"

    def __init__(self, xmlui:XMLUI, open_count=OPEN_COUNT):
        self.xmlui = xmlui
        self._state:XUXScene.State = self.State.OPENING

        # フェードインから
        self._timer = XUXCountDown(open_count)
        self.fade_color = 0

    @property
    def fade_alpha(self) -> float:
        return self._timer.alpha

    # mainから呼び出すもの
    # -----------------------------------------------------
    def update_scene(self):
        # open/close中はupdateを呼び出さない
        if self._state == self.State.OPENED:
            # 更新処理呼び出し
            XUXInput(self.xmlui).check()  # UI用キー入力
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

    def end_scene(self, close_count=CLOSE_COUNT):
        self._timer = XUXCountUp(close_count)
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
            if self._timer.update():
                self._state = self.State.OPENED
            pyxel.dither(self.fade_alpha)
            pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, self.fade_color)

        if self._state == self.State.CLOSING:
            if self._timer.update():
                self._state = self.State.CLOSED
            pyxel.dither(self.fade_alpha)
            pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, self.fade_color)

