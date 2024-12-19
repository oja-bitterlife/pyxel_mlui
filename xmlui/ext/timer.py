from enum import Enum,auto
from typing import Callable,Any

# タイマー管理
class XUXTimer:
    class Mode(Enum):
        TIMEOUT = auto()
        INTERVAL = auto()
        COUNTUP = auto()
        COUNTDOWN = auto()

    # タイマー開始
    def __init__(self, mode:"XUXTimer.Mode", func:Callable, count:int):
        self.mode:XUXTimer.Mode|None = mode
        self.func = func
        self.count_max = count

        if self.count_max < 0:
            raise ValueError("count_max must be greater than 0")

        match mode:
            case XUXTimer.Mode.COUNTUP:
                self.count = 0
            case _:
                self.count = count

    # タイマー停止
    def stop(self):
        self.mode = None

    @property
    def is_stop(self) -> bool:
        return self.mode is None

    # タイマー更新
    def update(self):
        # タイマーは終了している
        if self.mode is None:
            return True

        # カウントアップ・ダウン系
        if self.mode == XUXTimer.Mode.COUNTUP or self.mode == XUXTimer.Mode.COUNTDOWN:
            self.func(self.count, self.count_max)

            if self.mode == XUXTimer.Mode.COUNTUP:
                self.count += 1
                if self.count >= self.count_max:
                    self.stop()  # カウントアップ完了
                    return True
            if self.mode == XUXTimer.Mode.COUNTDOWN:
                if self.count <= 0:
                    self.stop()  # カウントダウン完了
                    return True
                self.count -= 1  # 最大と0を含める

        # タイムアウト系
        else:
            self.count -= 1
            if self.count <= 0:
                self.func()

                # intervalはカウントし直し
                if self.mode == XUXTimer.Mode.INTERVAL:
                    self.count = self.count_max
                else:
                    self.stop()
                return True

        # イベントは発生しなかった
        return False
