import pyxel # Pyxelモジュールをインポート

pyxel.init(256, 256) # 初期化(ウィンドウサイズを指定)

from xmlui import XMLUI
ui_template = XMLUI.createFromFile("assets/ui/test.xml")
ui_worker = XMLUI.createWorker("my_ui")


# お試しサンプルUI
import xmlui_pyxel
xmlui_pyxel.setDefaults(ui_worker)

from xmlui import UI_MENU
command_item_data = [
    ["speak", "tool"],
    ["status", "check"],
]

# Main
def update(): # フレームの更新処理
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

    active_menu = ui_worker.root.getTopMenu()
    if active_menu:
        if pyxel.btnp(pyxel.KEY_LEFT):
            active_menu.moveLeft()
        if pyxel.btnp(pyxel.KEY_RIGHT):
            active_menu.moveRight()
        if pyxel.btnp(pyxel.KEY_UP):
            active_menu.moveUp()
        if pyxel.btnp(pyxel.KEY_DOWN):
            active_menu.moveDown()

        if pyxel.btnp(pyxel.KEY_SPACE):
            active_menu.on("action")

    else:
        if pyxel.btnp(pyxel.KEY_SPACE):
            # コマンドメニュー表示
            try:
                ui_worker.findByID("menu_command")
            except:
                menu_win = ui_worker.duplicate(ui_template.findByID("menu_command"))
                ui_worker.addChild(menu_win.openMenu(UI_MENU("command", menu_win, command_item_data)))

        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            menu_win.remove()

    ui_worker.update()

def draw(): # 描画処理
    pyxel.cls(0)

    # UI描画
    ui_worker.draw()

# アプリケーションの実行
pyxel.run(update, draw)
