from typing import Callable,Generic,TypeVar
import pyxel

from xmlui.core import XMLUI,XUEventItem
from xmlui.lib.debug import get_logger
from xmlui.ext.input import XUEInput
from xmlui.ext.timer import XUETimeout


# ステータス遷移管理用。NPCの寸劇とかで使うやつ
# #############################################################################
T = TypeVar('T')

# 一定時間後に1つのaction。アクションをつなげて実行する場合は主にこちら
class XUEActItem(XUETimeout, Generic[T]):
    # デフォルトはすぐ実行
    def __init__(self):
        super().__init__(0)
        self._init_func:Callable|None = self.init
        self._manager:T|None = None  # 呼び出しActへの参照

    # コンストラクタではなくinit()の中で時間を設定する。
    def set_wait(self, wait:int):
        self._count_max = wait

    # オーバーライドして使う物
    def init(self):
        pass

    # 呼び出しActを返す(Actの中で次のActをaddする用)
    # GenericsでActではなくnewしたクラスそのものを返す
    @property
    def manager(self) -> T:
        if self._manager is None:
            raise RuntimeError("act is not set")
        return self._manager

# 一定時間内ずっとwaigingが実行され、最後にaction。
class XUEActWait(XUEActItem[T]):
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
    def _update(self) -> bool:
        if not self.is_finish:
            if self.waiting():
                self.finish()
        return super()._update()

    # オーバーライドして使う物
    # -----------------------------------------------------
    def waiting(self) -> bool:
        return False

# Act管理クラス。各Itemをコレに登録していく
# *****************************************************************************
class XUEActManager:
    def __init__(self):
        self.act_queue:list[XUEActItem] = []

    # キュー操作
    # -----------------------------------------------------
    def add_act(self, *items:XUEActItem):
        for item in items:
            item._manager = self  # 自分を登録しておく
            self.act_queue.append(item)

    def clear_act(self):
        self.act_queue.clear()

    def next_act(self):
        if self.act_queue:
            self.act_queue.pop(0)

    # 状態更新
    # -----------------------------------------------------
    def _update_act(self):
        if not self.is_act_empty:
            act = self.current_act
            if act._init_func:
                act._init_func()  # 初回はinitも実行
                act._init_func = None
            act._update()

            # 完了したら次のAct
            if act.is_finish:
                self.next_act()

    # 状態取得
    # -----------------------------------------------------
    @property
    def current_act(self) -> XUEActItem:
        return self.act_queue[0]

    @property
    def is_act_empty(self) -> bool:
        return len(self.act_queue) == 0


# シーン管理(フェードイン・フェードアウト)用
# #############################################################################
# シーン管理用仕込み
class _XUESceneBase(XUEActManager):
    def __init__(self, xmlui:XMLUI):
        super().__init__()

        self.xmlui = xmlui
        self._next_scene:XUEFadeScene|None = None
        self.is_end = False

        # デフォルトでUpdateを使えるように
        self.add_act(_XUESceneBase._UpdateAct(self))

    # シーン遷移
    def set_next_scene(self, scene:"XUEFadeScene"):
        self._next_scene = scene

    # シーンマネージャから呼ばれるもの
    # -----------------------------------------------------
    def update_scene(self):
        # xmluiのキーイベントサポート
        XUEInput(self.xmlui).check()
        for event in self.xmlui.event.trg:
            self.event(event)

        # Actの更新
        self._update_act()

        # シーン完了チェック。完了時はclosed()内で次シーンを設定しておくように
        if self.is_act_empty:
            self.closed()
            self.is_end = True
            return

    def draw_scene(self):
        self.draw()

    # デフォルトでUpdateを使えるように
    # -----------------------------------------------------
    class _UpdateAct(XUEActWait[T]):
        def __init__(self, scene:"_XUESceneBase"):
            super().__init__()
            self.scene = scene

        def waiting(self) -> bool:
            self.scene.update()
            return super().waiting()

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
class XUEFadeScene(_XUESceneBase):
    # デフォルトフェードカラー
    FADE_COLOR = 0

    # デフォルトフェードインアウト時間
    OPEN_COUNT = 10
    CLOSE_COUNT = 20

    # フェード管理
    # -----------------------------------------------------
    class FadeAct(XUEActManager):
        def __init__(self):
            super().__init__()
            self.alpha:float = 0.0

    # 各フェードパート
    # -----------------------------------------------------
    # パートベース。fade_actのalphaを書き換える
    class _FadeActItem(XUEActWait):
        def __init__(self, scene:"XUEFadeScene"):
            super().__init__()
            self.scene = scene

    # フェードイン
    class FadeIn(_FadeActItem):
        def __init__(self, scene:"XUEFadeScene", open_count:int):
            super().__init__(scene)
            self.set_wait(open_count)

        def waiting(self) -> bool:
            self.scene.alpha = 1-self.alpha  # 黒から
            return self.is_finish

        # フェードインが終わったら綺麗な0にしておく
        def action(self):
            self.scene.alpha = 0

    # フェードアウト
    class FadeOut(_FadeActItem):
        def __init__(self, scene:"XUEFadeScene", close_count:int):
            super().__init__(scene)
            self.set_wait(close_count)

        def waiting(self) -> bool:
            self.scene.xmlui.event.clear()  # フェード中は動かさない
            self.scene.alpha = self.alpha
            return False

    # 初期化
    # -----------------------------------------------------
    def __init__(self, xmlui:XMLUI, open_count=OPEN_COUNT):
        super().__init__(xmlui)
        self.alpha = 0.0

        # フェードインから
        self.add_act(XUEFadeScene.FadeIn(self, open_count))

    # シーンマネージャから呼ばれるもの
    # -----------------------------------------------------
    def draw_scene(self):
        pyxel.dither(1.0)  # 戻しておく

        # フェード描画
        # -------------------------------------------------
        # Actがない(=シーン切り替え中)
        if self.is_act_empty:
            self.alpha = 1  # 常に塗りつぶす
            pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, self.FADE_COLOR)

        # Actがある(=シーン中)
        else:
            super().draw_scene()

            # 無駄な描画をしないよう
            if self.alpha > 0:
                pyxel.dither(self.alpha)  # フェードで
                pyxel.rect(0, 0, self.xmlui.screen_w, self.xmlui.screen_h, self.FADE_COLOR)

    # フェードアウトを開始する
    def close(self):
        # Actを全て破棄してフェードアウト開始
        self.clear_act()
        self.add_act(XUEFadeScene.FadeOut(self, self.CLOSE_COUNT))


# シーン管理。mainの中で各シーンを実行する
# *****************************************************************************
class XUESceneManager:
    def __init__(self, start_scene:_XUESceneBase):
        self.current_scene:_XUESceneBase = start_scene

    def update(self):
        # next_sceneが設定されていたら
        if self.current_scene._next_scene is not None:
            self.current_scene = self.current_scene._next_scene
            self.current_scene._next_scene = None

        # updateはend以降は呼ばない
        if not self.current_scene.is_end:
            self.current_scene.update_scene()

    def draw(self):
        # drawはend以降も呼ぶ(endの状態を描画)
        self.current_scene.draw_scene()
