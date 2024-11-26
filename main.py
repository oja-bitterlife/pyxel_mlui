import pyxel # Pyxelモジュールをインポート

pyxel.init(256, 256) # 初期化(ウィンドウサイズを指定)

# お試しサンプルUI
import xmlui_pyxel
ui_worker = xmlui_pyxel.ui_worker

# お試し
ui_template = xmlui_pyxel.ui_template
# ui_worker.root.open(ui_template, "menu_command")

ui_worker.setInputList("up", [
    pyxel.GAMEPAD1_BUTTON_DPAD_UP,
    pyxel.KEY_UP,
    pyxel.KEY_W,
])
ui_worker.setInputList("down", [
    pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
    pyxel.KEY_DOWN,
    pyxel.KEY_S,
])
ui_worker.setInputList("left", [
    pyxel.GAMEPAD1_BUTTON_DPAD_LEFT,
    pyxel.KEY_LEFT,
    pyxel.KEY_A,
])
ui_worker.setInputList("right", [
    pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT,
    pyxel.KEY_RIGHT,
    pyxel.KEY_D,
])
ui_worker.setInputList("button_a", [
    pyxel.GAMEPAD1_BUTTON_A,
    pyxel.KEY_RETURN,
    pyxel.KEY_SPACE,
])
ui_worker.setInputList("button_b", [
    pyxel.GAMEPAD1_BUTTON_B,
    pyxel.KEY_BACKSPACE,
])
ui_worker.setInputList("button_X", [
    pyxel.GAMEPAD1_BUTTON_X,
])
ui_worker.setInputList("button_y", [
    pyxel.GAMEPAD1_BUTTON_Y,
])

from xmlui_core import UI_WINDOW

screen_buf = pyxel.screen.data_ptr()
win = UI_WINDOW(4, 4, pyxel.width, pyxel.height)

# Main
def update(): # フレームの更新処理
    ui_worker.checkInputAndOn(pyxel.btn)

    # UI更新
    ui_worker.update()

    # デバッグ
    if ui_worker.debug:
        if pyxel.btnp(pyxel.KEY_T):
            print(ui_worker.root.strTree())

def draw(): # 描画処理
    pyxel.cls(0)

    # UI描画
    ui_worker.draw()

    win.draw_buf(-100, -100, 160, 160, screen_buf)

# アプリケーションの実行
pyxel.run(update, draw)
