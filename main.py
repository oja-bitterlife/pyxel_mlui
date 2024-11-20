import pyxel # Pyxelモジュールをインポート

pyxel.init(256, 256) # 初期化(ウィンドウサイズを指定)

from xmlui import XMLUI
ui_template = XMLUI.createFromFile("assets/ui/test.xml")
ui_worker = XMLUI.createWorker("my_ui")


# お試しサンプルUI
import xmlui_pyxel
xmlui_pyxel.setDefaults(ui_worker)


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

    # コマンドメニュー表示
    ui_worker.root.open(ui_template, "menu_command")

    ui_worker.update()

def draw(): # 描画処理
    pyxel.cls(0)

    # UI描画
    ui_worker.draw()

# アプリケーションの実行
pyxel.run(update, draw)
