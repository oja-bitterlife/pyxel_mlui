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

from xmlui_core import *

screen_buf = pyxel.screen.data_ptr()
win1 = XUIWinRound([7,7,12,12,12], pyxel.width, pyxel.height).setShadow(2, [1])
win2 = XUIWinRound([7,7,12,12,12], pyxel.width, pyxel.height).setShadow(2, [1])
win3 = XUIWinRound([7,7,12,12,12], pyxel.width, pyxel.height).setShadow(2, [1])
win4 = XUIWinRound([7,7,12,12,12], pyxel.width, pyxel.height).setShadow(2, [1])

win5 = XUIWinRound([7,7,12,12,12,12,12,12,12,12,12,12], pyxel.width, pyxel.height).setShadow(2, [1])
win6 = XUIWinRect([7,7,12], pyxel.width, pyxel.height).setShadow(2, [1])
win7 = XUIWinRound([3,11,12,8,-1], pyxel.width, pyxel.height)
win8 = XUIWinRound([1,2,3,4,5,6,7,8,12], pyxel.width, pyxel.height).setShadow(2, [1])

wins = [win1, win2, win3, win4, win5, win6, win7, win8]

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

    win_size = 64
    count = ui_worker.root.update_count*2-100
    for i,win in enumerate(wins):
        win_w = win_size
        win_h = win_size

        if i == 0:
            win.clip.h = count
        elif i == 1:
            win.clip.w = count
        elif i == 2:
            win_h = min(win_size, count)
        elif i == 3:
            win.clip.x = win_size//2 - count//2
            win.clip.w = count
            win.clip.y = win_size//2 - count//2
            win.clip.h = count

        win.drawBuf((i%4)*win_size, (i//4)*win_size, win_w, win_h , screen_buf)

# アプリケーションの実行
pyxel.run(update, draw)
