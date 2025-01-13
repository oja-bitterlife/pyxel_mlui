from typing import Self

# タイマー管理
class _XUETimerBase:
    # タイマー開始
    def __init__(self, count:int):
        if count < 0:
            raise ValueError("count must be greater than 0")

        self._count = 0
        self._count_max = count
        self.is_finish = False  # 完了済みフラグ

    # タイマー完了
    def finish(self) -> Self:
        self.is_finish = True
        return self

    # 現在カウント。基本はカウントアップ
    @property
    def count(self) -> int:
        return self._count

    # 現在カウントの進捗具合
    @property
    def alpha(self) -> float:
        # 一瞬で終わる場合常に1(完了)
        if self._count_max == 0:
            return 1.0
        return max(0, min(1, float(self.count)/float(self._count_max)))

    # タイマー更新
    def update(self):
        raise NotImplementedError()

    # タイマーアクション
    def action(self):
        pass


# 利用クラス
# *****************************************************************************
# 指定時間後に発火
# ---------------------------------------------------------
# 時間がきたら一度きりの実行
class XUETimeout(_XUETimerBase):
    def update(self):
        # 完了済み
        if self.is_finish:
            return

        # 1,2,3,4,...10
        self._count += 1

        # カウントアップ完了
        if self._count >= self._count_max:
            self.action()
            self.finish()

# 時間ごとに何度も実行
class XUEInterval(_XUETimerBase):
    def update(self):
        # 完了済み
        if self.is_finish:
            return

        # 1,2,3,4,...10
        self._count += 1

        # カウントアップ完了
        if self.count >= self._count_max:
            self.action()
            self._count = 0  # intervalはカウントし直し

# 指定時間までずっと発火
# ---------------------------------------------------------
# カウントアップ
class XUECountUp(_XUETimerBase):
    def update(self):
        # 完了済み
        if self.is_finish:
            return

        # 1,2,3,4,...10
        self._count += 1
        self.action()

        if self._count >= self._count_max:
            self.finish()  # カウントアップ完了

# カウントダウン。0も含める
class XUECountDown(_XUETimerBase):
    def update(self):
        # 完了済み
        if self.is_finish:
            return

        # 0,9,8...1,0
        self._count += 1
        self.action()

        if self._count >= self._count_max:
            self.finish()  # カウントダウン完了

    # カウントダウンにオーバーライド
    @property
    def count(self) -> int:
        return max(0, self._count_max - self._count)
