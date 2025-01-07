from typing import Callable

import pyxel

from xmlui.core import XMLUI,XUEventItem
from xmlui.lib.debug import get_logger
from xmlui.ext.input import XUEInput
from xmlui.ext.timer import XUETimeout


# ステータス遷移管理用。NPCの寸劇とかで使うやつ
# #############################################################################
# 一定時間内ずっとwaigingが実行され、最後にaction。
class XUEActItem(XUETimeout):
    WAIT_FOREVER = 2**31-1

    # デフォルトはfinish()が呼ばれるまで無限待機
    def __init__(self, count:int=WAIT_FOREVER):
        super().__init__(count)

        # Managerで設定されるもの
        self._init_func:Callable|None = None
        self._manager:XUEActManager|None = None

        # SceneBaseで使われるもの
        self.use_key_event = True  # キーイベントの取得要求

    # コンストラクタではなくinit()の中で時間を設定する。
    def set_wait(self, wait:int):
        self._count_max = wait

    # override
    @property
    def alpha(self):
        if self._count_max == self.WAIT_FOREVER:
            return 1
        else:
            return super().alpha

    # override
    def _update(self):
        if not self.is_finish:
            self.waiting()
            if self.is_finish:
                self.action()  # 完了呼び出し
        super()._update()

    # 呼び出しManagerを返す(Actの中で次のActをaddする用)
    @property
    def act(self) -> "XUEActManager":
        if self._manager is None:
            raise RuntimeError("act is not set")
        return self._manager

    # == で現在のActのチェックができるように
    def __eq__(self, other) -> bool:
        if issubclass(other, XUEActItem):
            return other.__name__ == self.__class__.__name__
        else:
            return super().__eq__(other)

    # オーバーライドして使う物
    # -----------------------------------------------------
    def init(self):
        pass
    def waiting(self):
        pass
    # def action(self)は親クラスで定義


# Act管理クラス。各Itemをコレに登録していく
# *****************************************************************************
class XUEActManager:
    def __init__(self):
        self._act_queue:list[XUEActItem] = []

    # キュー操作
    # -----------------------------------------------------
    def add_act(self, *items:XUEActItem):
        for item in items:
            # Actの初期化
            item._manager = self
            item._init_func = item.init

            self._act_queue.append(item)

    def clear_act(self):
        self._act_queue.clear()

    def next_act(self) -> XUEActItem | None:
        if self._act_queue:
            return self._act_queue.pop(0)

    # 状態更新
    # -----------------------------------------------------
    def update(self):
        if not self.is_act_empty:
            act = self.current_act
            if act._init_func:
                act._init_func()  # 初回はinitも実行
                act._init_func = None
            # Actの実行
            act._update()

            # 完了したら次のAct
            if act.is_finish:
                self.next_act()

    # 状態取得
    # -----------------------------------------------------
    @property
    def current_act(self) -> XUEActItem:
        return self._act_queue[0]

    @property
    def is_act_empty(self) -> bool:
        return len(self._act_queue) == 0


# シーン管理(フェードイン・フェードアウト)用
# #############################################################################
# シーン管理用仕込み
class XUESceneBase(XUEActManager):
    def __init__(self, xmlui:XMLUI):
        super().__init__()
        self.xmlui = xmlui
        self.input = XUEInput()  # xmluiのキーイベントサポート

        self._next_scene:XUEFadeScene|None = None
        self.is_end = False  # このシーンが終了したかどうか

    # シーン遷移
    def set_next_scene(self, scene:"XUEFadeScene"):
        self._next_scene = scene

    # シーン終了(closedの中でset_next_sceneをする)
    def close_scene(self):
        if not self.is_end:
            self.closed()
            self.is_end = True

    # シーンマネージャから呼ばれるもの
    # -----------------------------------------------------
    def update_scene(self):
        # 終了していたらなにもしない
        if self.is_end:
            return

        # actがempty(updateを使う)か、actがuse_keyか
        if self.is_act_empty or self.current_act.use_key_event:
            self.input.check(self.xmlui)  # xmluiのキーイベントサポート

        # イベント処理
        for event in self.xmlui.event.trg:
            self.event(event)

        # ActがあればActの更新。なければ通常のUpdate
        if not self.is_act_empty:
            super().update()
        else:
            self.update()

    def draw_scene(self):
        if not self.is_end:
            self.draw()

    # オーバーライドして使う物
    # -----------------------------------------------------
    def event(self, event:XUEventItem):
        pass
    def update(self):
        pass
    def draw(self):
        pass
    # フェードアウト完了時に呼ばれる。主に次シーン設定を行う
    def closed(self):
        get_logger().debug("scene.closed is not implemented")

# シーンクラス。継承して使おう
class XUEFadeScene(XUESceneBase):
    # デフォルトフェードカラー
    FADE_COLOR = 0

    # デフォルトフェードインアウト時間
    OPEN_COUNT = 10
    CLOSE_COUNT = 20

    # 各フェードパート
    # -----------------------------------------------------
    # パートベース。fade_actのalphaを書き換える
    class _FadeActItem(XUEActItem):
        def __init__(self, scene:"XUEFadeScene"):
            super().__init__()
            self.scene = scene

    # フェードイン
    class FadeIn(_FadeActItem):
        def __init__(self, scene:"XUEFadeScene", open_count:int):
            super().__init__(scene)
            self.set_wait(open_count)

        def waiting(self):
            self.scene.alpha = 1-self.alpha  # 黒から

        # フェードインが終わったら綺麗な0にしておく
        def action(self):
            self.scene.alpha = 0

    # フェードアウト
    class FadeOut(_FadeActItem):
        def __init__(self, scene:"XUEFadeScene", close_count:int):
            super().__init__(scene)
            self.set_wait(close_count)

            self.use_key_event = False  # フェード中は動かさない

        def waiting(self):
            self.scene.alpha = self.alpha

        # フェードアウトが終わったら終了
        def action(self):
            self.scene.close_scene()

    # 初期化
    # -----------------------------------------------------
    def __init__(self, xmlui:XMLUI, open_count=OPEN_COUNT):
        super().__init__(xmlui)
        self.alpha = 0.0

        # フェードインから
        self.add_act(XUEFadeScene.FadeIn(self, open_count))

    # フェードアウトを開始する
    def fade_close(self):
        # Actを全て破棄してフェードアウト開始
        self.clear_act()
        self.add_act(XUEFadeScene.FadeOut(self, self.CLOSE_COUNT))

    # シーンマネージャから呼ばれるもの
    # -----------------------------------------------------
    def draw_scene(self):
        if self.is_end:
            return

        # フェード描画
        # -------------------------------------------------
        # 画面の描画
        self.draw()

        # フェードを上から描画
        if self.alpha > 0:  # 無駄な描画をしないよう
            pyxel.dither(self.alpha)  # フェードで
            pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, self.FADE_COLOR)
            pyxel.dither(1.0)  # 戻しておく

# シーン管理。mainの中で各シーンを実行する
# *****************************************************************************
class XUESceneManager:
    def __init__(self, start_scene:XUESceneBase):
        self.current_scene:XUESceneBase = start_scene

    def update(self):
        # next_sceneが設定されていたら
        if self.current_scene._next_scene is not None:
            self.current_scene = self.current_scene._next_scene
            self.current_scene._next_scene = None

        self.current_scene.update_scene()

    def draw(self):
        # drawはend以降も呼ぶ(endの状態を描画)
        self.current_scene.draw_scene()
