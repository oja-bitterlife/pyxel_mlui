from typing import Callable,Self

# タイマー管理
class _XUXTimerBase:
    # タイマー開始
    def __init__(self, count:int):
        if count < 0:
            raise ValueError("count must be greater than 0")

        self._count = 0
        self.count_max = count

    # タイマー停止
    def finish(self) -> Self:
        self._count = self.count_max
        return self

    @property
    def is_finish(self) -> bool:
        return self._count >= self.count_max

    @property
    def count(self) -> int:
        return self._count

    # タイマー更新
    def update(self) -> bool:
        raise NotImplementedError()

    # タイマーアクション
    def action(self):
        pass


# 指定時間後に発火
class XUXTimeout(_XUXTimerBase):
    def update(self):
        # 1,2,3,4,...10
        self._count += 1

        # カウントアップ完了
        if self._count >= self.count_max:
            self.action()
            self.finish()  
            return True

        return False


# 指定時間毎に発火
class XUXInterval(_XUXTimerBase):
    def update(self):
        # 1,2,3,4,...10
        self._count += 1

        # カウントアップ完了
        if self.count >= self.count_max:
            self.action()
            self._count = 0  # intervalはカウントし直し
            return True

        return False


# 指定時間までずっと発火(カウントアップ)
class XUXCountUp(_XUXTimerBase):
    def update(self) -> bool:
        # 1,2,3,4,...10
        self._count += 1
        self.action()

        if self._count >= self.count_max:
            self.finish()  # カウントアップ完了
            return True

        return False


# 指定時間までずっと発火(カウントダウン。0も含める)
class XUXCountDown(_XUXTimerBase):
    def update(self) -> bool:
        # 10,9,8...1,0
        self.action()

        if self._count >= self.count_max:
            self.finish()  # カウントダウン完了
            return True

        self._count += 1  # 0を含めるため最後に
        return False

    # カウントダウンにオーバーライド
    @property
    def count(self) -> int:
        return self.count_max - self._count
