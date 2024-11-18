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

menu_win = ui_worker.root.dupAddChild(ui_template.root.findByID("menu_cmd")).updateChildren()
menu_grid = menu_win.findByTag("menu_grid").openMenu(UI_MENU(command_item_data, 0, 0))

# Main
def update(): # フレームの更新処理
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

    active_menu = menu_win.getActiveMenu()
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
            try:
                #  表示中なら消す
                win_message = menu_win.findByTag("win_message")
                win_message.remove()
            except:
                # 非表示なら新規で追加
                if active_menu.getData() == "speak":
                    ui_worker.root.dupAddChild(ui_template.root.findByID("win_message")).openMenu(UI_MENU())

        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            menu_win.remove()

    ui_worker.update()

def draw(): # 描画処理
    pyxel.cls(0)

    # UI描画
    ui_worker.draw()

# アプリケーションの実行
pyxel.run(update, draw)
