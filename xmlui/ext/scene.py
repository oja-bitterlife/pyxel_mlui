from enum import StrEnum
from typing import Callable
import pyxel

from xmlui.core import XMLUI
from xmlui.ext.input import XUXInput
from xmlui.ext.timer import XUXCountUp,XUXCountDown,XUXTimeout


# ステータス遷移管理用。NPCの寸劇とかで使うやつ
# *****************************************************************************
class XUXActItem(XUXTimeout):
    # デフォルトはすぐ実行
    def __init__(self, xmlui:XMLUI):
        super().__init__(0)
        self.xmlui = xmlui
        self._init_func:Callable|None = self.init

    # コンストラクタではなくinit()の中で時間を設定する。
    def set_wait(self, wait:int):
        self._count_max = wait

    # オーバーライドして使う物
    def init(self):
        pass

class XUXActWait(XUXActItem):
    WAIT_FOREVER = 2**31-1

    # デフォルトは無限待機
    def __init__(self, xmlui:XMLUI):
        super().__init__(xmlui)
        self.set_wait(self.WAIT_FOREVER)

    # override
    @property
    def alpha(self):
        if self._count_max == self.WAIT_FOREVER:
            return 1
        else:
            return self.alpha

    # override
    def update(self) -> bool:
        update_result = super().update()
        if not self.is_finish:
            if self.waiting():
                self.finish()
        return update_result

    # オーバーライドして使う物
    def waiting(self) -> bool:
        return False

class XUXAct:
    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui
        self.queue:list[XUXActItem] = []

    def add(self, *items:XUXActItem):
        for item in items:
            self.queue.append(item)

    def next(self):
        self.queue.pop(0)

    def update(self):
        if self.queue:
            act = self.queue[0]
            if act._init_func:
                act._init_func()  # 初回はinitも実行
                act._init_func = None
            act.update()

            # 完了したら次のAct
            if act.is_finish:
                self.next()


# シーン管理(フェードイン・フェードアウト)用
# *****************************************************************************
class XUXScene:
    # デフォルトフェードインアウト時間
    OPEN_COUNT = 15
    CLOSE_COUNT = 15

    # シーン管理用
    current_scene:"XUXScene|None" = None

    # Sceneのopen/close状態
    class OpenCloseState(StrEnum):
        OPENING = "opening"
        OPENED = "opened"
        CLOSING = "closing"
        CLOSED = "closed"

    def __init__(self, xmlui:XMLUI, open_count=OPEN_COUNT):
        self.xmlui = xmlui
        self._state:XUXScene.OpenCloseState = self.OpenCloseState.OPENING

        # フェードインから
        self._timer = XUXCountDown(open_count)
        self.fade_color = 0

    # mainから呼び出すもの
    # -----------------------------------------------------
    def update_scene(self):
        # open/close中はupdateを呼び出さない
        if self._state == self.OpenCloseState.OPENED:
            # 更新処理呼び出し
            XUXInput(self.xmlui).check()  # UI用キー入力
            self.update()

    def draw_scene(self):
        pyxel.dither(1.0)  # 戻しておく

        # シーン終了後はdrawも呼び出さない
        if self._state == self.OpenCloseState.CLOSED:
            pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, self.fade_color)
            self.closed()  # 代わりにclosedを呼び出す
        else:
            self.draw()
            self._draw_after()

    def end_scene(self, close_count=CLOSE_COUNT):
        self._timer = XUXCountUp(close_count)
        self._state = self.OpenCloseState.CLOSING

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
        if self._state == self.OpenCloseState.OPENING:
            if self._timer.update():
                self._state = self.OpenCloseState.OPENED
            pyxel.dither(self._timer.alpha)
            pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, self.fade_color)

        if self._state == self.OpenCloseState.CLOSING:
            if self._timer.update():
                self._state = self.OpenCloseState.CLOSED
            pyxel.dither(self._timer.alpha)
            pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, self.fade_color)

