import pyxel # Pyxelモジュールをインポート

pyxel.init(256, 256) # 初期化(ウィンドウサイズを指定)

def update(): # フレームの更新処理
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

    xmlui.update()

def draw(): # 描画処理
    pyxel.cls(0)

    # UI描画
    xmlui.draw()

from xmlui import XMLUI
xmlui = XMLUI.createFromFile("assets/ui/test.xml")

# お試しサンプルUI
import xmlui_pyxel
xmlui_pyxel.setDefaults(xmlui)

from xmlui import UI_GRID
command_menu = [
    ["speak", "tool"],
    ["status", "check"],
]
command_menu = xmlui.findByID("command_menu")
if command_menu:
    command_menu.userData["item_data"] = UI_GRID(command_menu, 1, 1)


# アプリケーションの実行
pyxel.run(update, draw)
