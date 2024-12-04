# 今回はpyxel向けのライブラリを作るのです
import pyxel

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
pyxel.run(update, draw)
