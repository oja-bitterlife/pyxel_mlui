# 今回はpyxel向けのライブラリを作るのです
import pyxel
# initを呼ぶまでWebでファイルシステムが使えないことに注意
pyxel.init(256, 256)

# ここからゲーム本体開始
# *********************************************************
from xmlui.ext.scene import XUXSceneManager

from title import Title
from field import Field
from battle import Battle

# 最初はタイトル
scene_manager = XUXSceneManager(Title())
#scene_manager = XUXSceneManager(Field())
#scene_manager = XUXSceneManager(Battle())

# Main
def update(): # フレームの更新処理
    # シーン更新
    scene_manager.update()

def draw(): # 描画処理
    # ゲームの描画コード
    pyxel.cls(0)

    # シーン描画
    scene_manager.draw()

# アプリケーションの実行
pyxel.run(update, draw)
