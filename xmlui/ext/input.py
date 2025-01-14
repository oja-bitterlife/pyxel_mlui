import pyxel

from xmlui.core import XMLUI,XUEvent,XUEventItem
from xmlui.lib import debug

# Pyxelの入力をXMLUIのイベントに変換する。
# ちゃんと設定しないとUIとゲームで操作が違ってしまうので、
# 使用はお勧めできない、開発者用。
# #############################################################################
# インプット状態チェック用。状態を持たないのでどこで何個つくってもよい
class XUEInputInfo:
    # キーコンフィグ時はここの設定書き換える
    CFG_LEFT = [pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, pyxel.KEY_LEFT, pyxel.KEY_A]
    CFG_RIGHT = [pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT, pyxel.KEY_RIGHT, pyxel.KEY_D]
    CFG_UP = [pyxel.GAMEPAD1_BUTTON_DPAD_UP, pyxel.KEY_UP, pyxel.KEY_W]
    CFG_DOWN = [pyxel.GAMEPAD1_BUTTON_DPAD_DOWN, pyxel.KEY_DOWN, pyxel.KEY_S]
    # XBox準拠...
    CFG_A = [pyxel.GAMEPAD1_BUTTON_A, pyxel.KEY_Z, pyxel.KEY_SPACE, pyxel.KEY_RETURN]
    CFG_B = [pyxel.GAMEPAD1_BUTTON_B, pyxel.KEY_X, pyxel.KEY_BACKSPACE]
    CFG_X = [pyxel.GAMEPAD1_BUTTON_X, pyxel.KEY_Q, pyxel.KEY_C]
    CFG_Y = [pyxel.GAMEPAD1_BUTTON_Y, pyxel.KEY_E, pyxel.KEY_V]

    # その時のキー定義に合わせて構築し直すようプロパティで
    @property
    def key_config(self) -> dict[XUEvent.Key, list[int]]:
        return {
            XUEvent.Key.LEFT: self.CFG_LEFT,
            XUEvent.Key.RIGHT: self.CFG_RIGHT,
            XUEvent.Key.UP: self.CFG_UP,
            XUEvent.Key.DOWN: self.CFG_DOWN,
            XUEvent.Key.BTN_A: self.CFG_A,
            XUEvent.Key.BTN_B: self.CFG_B,
            XUEvent.Key.BTN_X: self.CFG_X,
            XUEvent.Key.BTN_Y: self.CFG_Y,
        }

# インプット管理クラス、状態更新用
# どこかで作ってcheck()を１回呼び出すように
class XUEInput(XUEInputInfo):
    def __init__(self):
        super().__init__()
        self.enable = True

    # 全ボタン一気に調べてイベント設定
    def check(self, xmlui:XMLUI):
        # enableの時だけ
        if self.enable:
            for event,keys in self.key_config.items():
                # 定義されたキーのどれか１つでも押されていたら押された扱い
                for key in keys:
                    if pyxel.btn(key):
                        xmlui.on(event)
                        break

        # デバッグ用
        if pyxel.btnp(pyxel.KEY_TAB):
            xmlui.on(debug.DebugXMLUI.DEBUGEVENT_PRINTTREE)
        if pyxel.btnp(pyxel.KEY_F5):
            xmlui.on(debug.DebugXMLUI.DEBUGEVENT_RELOAD)
