# 今回はpyxel向けのライブラリを作るのです
import pyxel
# initを呼ぶまでWebでファイルシステムが使えないことに注意
pyxel.init(256, 256)

# ここからゲーム本体開始
# *********************************************************
from xmlui.ext.scene import XUESceneManager

from DQ.title import Title
from DQ.field import Field
from DQ.battle import Battle

# 最初はタイトル
scene_manager = XUESceneManager(Title())
#scene_manager = XUESceneManager(Field())
#scene_manager = XUESceneManager(Battle())

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
