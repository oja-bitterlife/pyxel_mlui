from enum import StrEnum
import pyxel

from xmlui.core import XMLUI

class SceneBase:
    current_scene:"SceneBase|None" = None

    class State(StrEnum):
        INIT = "init"
        RUN = "run"
        CLOSING = "closing"
        CLOSED = "closed"

    # フェードインアウト時間
    OPEN_COUNT_MAX = 30
    CLOSE_COUNT_MAX = 30

    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui
        self._state = self.State.INIT

        # フェードインアウト時間設定
        self.open_count = self.OPEN_COUNT_MAX
        self.close_count = self.CLOSE_COUNT_MAX

    def draw(self):
        pyxel.dither(1.0)  # 戻しておく

        match self._state:
            case self.State.INIT:
                self.init()
                self.init_after()
            case self.State.RUN:
                self.run()
                self.run_after()
            case self.State.CLOSING:
                self.closing()
                self.closing_after()
            case self.State.CLOSED:
                self.closed()
            case _:
                print("SceneBase: Unknown state")

    def init(self):
        pass

    def init_after(self):
        self._state = self.State.RUN

    def run(self):
        pass

    def run_after(self):
        if self.open_count > 0:
            pyxel.dither(self.open_count/self.OPEN_COUNT_MAX)
            pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, 0)
            self.open_count -= 1

    def end_run(self):
        self._state = self.State.CLOSING

    def closing(self):
        pass

    def closing_after(self):
        if self.close_count > 0:
            pyxel.dither((self.CLOSE_COUNT_MAX-self.close_count)/self.CLOSE_COUNT_MAX)
            pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, 0)
            self.close_count -= 1
        else:
            self._state = self.State.CLOSED

    def closed(self):
        pass
