import pyxel # Pyxelモジュールをインポート

pyxel.init(256, 256) # 初期化(ウィンドウサイズを指定)

# お試しサンプルUI
import samples.sample1 as sample
xmlui = sample.xmlui

xmlui.set_inputlist("up", [
    pyxel.GAMEPAD1_BUTTON_DPAD_UP,
    pyxel.KEY_UP,
    pyxel.KEY_W,
])
xmlui.set_inputlist("down", [
    pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
    pyxel.KEY_DOWN,
    pyxel.KEY_S,
])
xmlui.set_inputlist("left", [
    pyxel.GAMEPAD1_BUTTON_DPAD_LEFT,
    pyxel.KEY_LEFT,
    pyxel.KEY_A,
])
xmlui.set_inputlist("right", [
    pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT,
    pyxel.KEY_RIGHT,
    pyxel.KEY_D,
])
xmlui.set_inputlist("button_a", [
    pyxel.GAMEPAD1_BUTTON_A,
    pyxel.KEY_RETURN,
    pyxel.KEY_SPACE,
])
xmlui.set_inputlist("button_b", [
    pyxel.GAMEPAD1_BUTTON_B,
    pyxel.KEY_BACKSPACE,
])
xmlui.set_inputlist("button_X", [
    pyxel.GAMEPAD1_BUTTON_X,
])
xmlui.set_inputlist("button_y", [
    pyxel.GAMEPAD1_BUTTON_Y,
])

# Main
def update(): # フレームの更新処理
    xmlui.check_input_on(pyxel.btn)

    # UI更新
    xmlui.update()

    # デバッグ
    if xmlui.debug:
        if pyxel.btnp(pyxel.KEY_T):
            print(xmlui.strtree())

def draw(): # 描画処理
    pyxel.cls(0)

    # UI描画
    xmlui.draw()

# アプリケーションの実行
pyxel.run(update, draw)
