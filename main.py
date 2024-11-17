import pyxel # Pyxelモジュールをインポート

pyxel.init(256, 256) # 初期化(ウィンドウサイズを指定)

from xmlui import XMLUI
xmlui = XMLUI.createFromFile("assets/ui/test.xml")

# お試しサンプルUI
import xmlui_pyxel
xmlui_pyxel.setDefaults(xmlui)

from xmlui import UI_MENU
command_item_data = [
    ["speak", "tool"],
    ["status", "check"],
]

command_win = xmlui.findByID("command_win")
if command_win:
    command_items = UI_MENU(command_item_data, command_win, 0, 0)
    xmlui.openMenu(command_items)


# Main
def update(): # フレームの更新処理
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

    active_menu = xmlui.menu.getActive()
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
            if active_menu.getData() == "speak":
                msg_text = xmlui.findByTag("msg_text")
                if msg_text:
                    msg_text.update_count = 0

    xmlui.update()

def draw(): # 描画処理
    pyxel.cls(0)

    # UI描画
    xmlui.draw()

# アプリケーションの実行
pyxel.run(update, draw)
