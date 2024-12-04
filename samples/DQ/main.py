# 今回はpyxel向けのライブラリを作るのです
import pyxel

# xmlui_pyxelの初期化
# *********************************************************
from xmlui_core import XMLUI
from xmlui_pyxel import select,text,win,input

# ここからゲーム本体開始
# *********************************************************
pyxel.init(256, 256)

from title import Title

# 最初はタイトル
state = Title()

# Main
def update(): # フレームの更新処理
    # ゲームの更新コード
    state.update()

def draw(): # 描画処理
    # ゲームの描画コード
    pyxel.cls(0)

    state.draw()

# アプリケーションの実行
def run():
    pyxel.run(update, draw)
