# 今回はpyxel向けのライブラリを作るのです
import pyxel


# ここからゲーム本体開始
# *********************************************************
pyxel.init(256, 256)

from title import Title
from field import Field

# 最初はタイトル
scene = Title()
# scene = Field()

# Main
def update(): # フレームの更新処理
    global scene
    if scene:
        # ゲームの更新コード
        next_scene = scene.update()
        if next_scene is not None:
            match next_scene:
                case "title":
                    scene = Title()
                case "field":
                    scene = Field()

def draw(): # 描画処理
    global scene
    # ゲームの描画コード
    pyxel.cls(0)

    if scene:
        scene.draw()

# アプリケーションの実行
pyxel.run(update, draw)
