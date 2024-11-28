import pyxel # Pyxelモジュールをインポート

pyxel.init(256, 256) # 初期化(ウィンドウサイズを指定)

# お試しサンプルUI
import samples.sample1 as sample
ui_worker = sample.ui_worker

ui_worker.set_inputlist("up", [
    pyxel.GAMEPAD1_BUTTON_DPAD_UP,
    pyxel.KEY_UP,
    pyxel.KEY_W,
])
ui_worker.set_inputlist("down", [
    pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
    pyxel.KEY_DOWN,
    pyxel.KEY_S,
])
ui_worker.set_inputlist("left", [
    pyxel.GAMEPAD1_BUTTON_DPAD_LEFT,
    pyxel.KEY_LEFT,
    pyxel.KEY_A,
])
ui_worker.set_inputlist("right", [
    pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT,
    pyxel.KEY_RIGHT,
    pyxel.KEY_D,
])
ui_worker.set_inputlist("button_a", [
    pyxel.GAMEPAD1_BUTTON_A,
    pyxel.KEY_RETURN,
    pyxel.KEY_SPACE,
])
ui_worker.set_inputlist("button_b", [
    pyxel.GAMEPAD1_BUTTON_B,
    pyxel.KEY_BACKSPACE,
])
ui_worker.set_inputlist("button_X", [
    pyxel.GAMEPAD1_BUTTON_X,
])
ui_worker.set_inputlist("button_y", [
    pyxel.GAMEPAD1_BUTTON_Y,
])

# Main
def update(): # フレームの更新処理
    ui_worker.check_input_on(pyxel.btn)

    # UI更新
    ui_worker.update()

    # デバッグ
    if ui_worker.debug:
        if pyxel.btnp(pyxel.KEY_T):
            print(ui_worker.root.strtree())

def draw(): # 描画処理
    pyxel.cls(0)

    # UI描画
    ui_worker.draw()

# アプリケーションの実行
pyxel.run(update, draw)
