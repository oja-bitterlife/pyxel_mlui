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

s = xmlui.findByID("msg")
if s != None:
    s.remove = True
# print(s.element)

import xmlui_pyxel
xmlui_pyxel.setDefaults(xmlui)


# アプリケーションの実行
pyxel.run(update, draw)
