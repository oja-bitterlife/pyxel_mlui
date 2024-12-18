import pyxel
from xmlui.core import XMLUI,XUEvent,XUEventItem

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

    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui

    # その時のキー定義に合わせて構築し直すようプロパティで
    @property
    def key_config(self) -> dict[XUEventItem, list[int]]:
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

    # pyxelのキーがどのイベントに割り当てられているか調べる
    def _find_keyevent(self, pyxel_key:int):
        for event,keys in self.key_config.items():
            if pyxel_key in keys:
                return event
    
    # 現在入力中
    def input(self, pyxel_key:int):
        key_event = self._find_keyevent(pyxel_key)
        if key_event:
            return key_event in self.xmlui.event.now
        return False

    # 押された
    def trg(self, pyxel_key:int):
        key_event = self._find_keyevent(pyxel_key)
        if key_event:
            return key_event in self.xmlui.event.trg
        return False

    # はなされた
    def release(self, pyxel_key:int):
        key_event = self._find_keyevent(pyxel_key)
        if key_event:
            return key_event in self.xmlui.event.release
        return False

# インプット管理クラス。どこかでcheck()を呼び出す
class XUEInput(XUEInputInfo):
    # 全ボタン一気に調べてイベント設定
    def check(self):
        for event,keys in self.key_config.items():
            # 定義されたキーのどれか１つでも押されていたら押された扱い
            for key in keys:
                if pyxel.btn(key):
                    self.xmlui.on(event)
                    break
