import pyxel
pyxel.init(256, 256)

# ここからゲーム本体開始
# *********************************************************
from xmlui.core import XMLUI
XMLUI.debug_enable = True

# 作成するシーン選択
from xmlui.ext.scene import XUESceneManager
from scenes import field

scene_manager = XUESceneManager(field.Field())

# Main
def update():
    pass

def draw(): # 描画処理
    # ゲームの描画コード
    pyxel.cls(0)

    # シーン描画
    scene_manager.run()

# アプリケーションの実行
pyxel.run(update, draw)

