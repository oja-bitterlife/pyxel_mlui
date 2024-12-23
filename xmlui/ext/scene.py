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
    def __init__(self):
        super().__init__(0)
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
    def __init__(self):
        super().__init__()
        self.set_wait(self.WAIT_FOREVER)

    # override
    @property
    def alpha(self):
        if self._count_max == self.WAIT_FOREVER:
            return 1
        else:
            return super().alpha

    # override
    def update(self) -> bool:
        if not self.is_finish:
            if self.waiting():
                self.finish()
        return super().update()

    # オーバーライドして使う物
    def waiting(self) -> bool:
        return False

class XUXAct:
    def __init__(self):
        self.queue:list[XUXActItem] = []

    def add(self, *items:XUXActItem):
        for item in items:
            self.queue.append(item)

    def next(self):
        if not self.is_empty:
            self.queue.pop(0)

    def update(self):
        if not self.is_empty:
            act = self.current_act
            if act._init_func:
                act._init_func()  # 初回はinitも実行
                act._init_func = None
            act.update()

            # 完了したら次のAct
            if act.is_finish:
                self.next()

    @property
    def current_act(self):
        return self.queue[0]

    @property
    def is_empty(self) -> bool:
        return len(self.queue) == 0


# シーン管理(フェードイン・フェードアウト)用
# *****************************************************************************
class XUXScene:
    # デフォルトフェードインアウト時間
    OPEN_COUNT = 15
    CLOSE_COUNT = 15

    # デフォルトフェードカラー
    FADE_COLOR = 0

    # シーン管理用
    current_scene:"XUXScene|None" = None

    class FadeAct(XUXAct):
        def __init__(self):
            super().__init__()
            self.alpha = 1.0

    class _FadeActItem(XUXActWait):
        def __init__(self, fade_act:"XUXScene.FadeAct"):
            super().__init__()
            self.fade_act = fade_act

    class FadeIn(_FadeActItem):
        def __init__(self, fade_act:"XUXScene.FadeAct", open_count:int):
            super().__init__(fade_act)
            self.set_wait(open_count)

        def waiting(self) -> bool:
            self.fade_act.alpha = 1-self.alpha
            return self.is_finish

    class FadeOut(_FadeActItem):
        def waiting(self) -> bool:
            self.fade_act.alpha = self.alpha
            return False

    class FadeNone(_FadeActItem):
        def waiting(self) -> bool:
            self.fade_act.alpha = 0
            return False

    def __init__(self, xmlui:XMLUI, open_count=OPEN_COUNT):
        self.xmlui = xmlui

        # フェードインから
        self.fade_act = XUXScene.FadeAct()
        self.fade_act.add(
            XUXScene.FadeIn(self.fade_act, open_count),
            XUXScene.FadeNone(self.fade_act),
            XUXScene.FadeOut(self.fade_act))

    # mainから呼び出すもの
    # -----------------------------------------------------
    def update_scene(self):
        # シーンは終了している
        if self.fade_act.is_empty:
            self.closed()
            return

        if not isinstance(self.fade_act.current_act, XUXScene.FadeOut):
            # 更新処理呼び出し
            XUXInput(self.xmlui).check()  # UI用キー入力
            self.update()

        self.fade_act.update()

    def draw_scene(self):
        pyxel.dither(1.0)  # 戻しておく

        # フェード描画
        if not self.fade_act.is_empty:
            # シーン終了後はdrawも呼び出さない
            self.draw()
            pyxel.dither(self.fade_act.alpha)

        pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, self.FADE_COLOR)

    def end_scene(self, close_count=CLOSE_COUNT):
        if isinstance(self.fade_act.current_act, XUXScene.FadeNone):
            self.fade_act.next()
            if isinstance(self.fade_act.current_act, XUXScene.FadeOut):
                self.fade_act.current_act.set_wait(close_count)

    # オーバーライドして使う物
    # これらはsceneの中から呼び出すように(自分で呼び出さない)
    # -----------------------------------------------------
    def update(self):
        pass
    def draw(self):
        pass
    def closed(self):
        pass
 