import pyxel # Pyxelモジュールをインポート

pyxel.init(512, 512) # 初期化(ウィンドウサイズを指定)

def update(): # フレームの更新処理
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

    xmlui.update()

def draw(): # 描画処理
    pyxel.cls(0)

    xmlui.draw(0, 0, pyxel.width, pyxel.height)

from xmlui import XMLUI
xmlui = XMLUI.createFromFile("assets/ui/test.xml")

import xmlui_pyxel
xmlui_pyxel.setDefaults(xmlui)


# アプリケーションの実行
pyxel.run(update, draw)
