import pyxel # Pyxelモジュールをインポート

pyxel.init(512, 512) # 初期化(ウィンドウサイズを指定)

def update(): # フレームの更新処理
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

def draw(): # 描画処理
    pyxel.cls(0)
    pyxel.rect(1, 1, 158, 118, 11)


from xmlui_pyxel import XMLUI_PYXEL
xmlui = XMLUI_PYXEL.createFromFile("assets/ui/test.xml")

# アプリケーションの実行
pyxel.run(update, draw)
