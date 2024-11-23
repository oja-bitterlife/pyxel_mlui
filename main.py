import pyxel # Pyxelモジュールをインポート

pyxel.init(256, 256) # 初期化(ウィンドウサイズを指定)

# お試しサンプルUI
import xmlui_pyxel
ui_worker = xmlui_pyxel.ui_worker

# お試し
ui_template = xmlui_pyxel.ui_template
ui_worker.root.open(ui_template, "menu_command")


# Main
def update(): # フレームの更新処理
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

    if pyxel.btn(pyxel.KEY_LEFT):
        ui_worker.event.on("left")
    if pyxel.btn(pyxel.KEY_RIGHT):
        ui_worker.event.on("right")
    if pyxel.btn(pyxel.KEY_UP):
        ui_worker.event.on("up")
    if pyxel.btn(pyxel.KEY_DOWN):
        ui_worker.event.on("down")

    if pyxel.btn(pyxel.KEY_SPACE):
        ui_worker.event.on("action")
    if pyxel.btn(pyxel.KEY_BACKSPACE):
        ui_worker.event.on("cancel")

    ui_worker.update()

def draw(): # 描画処理
    pyxel.cls(0)

    # UI描画
    ui_worker.draw()

# アプリケーションの実行
pyxel.run(update, draw)
