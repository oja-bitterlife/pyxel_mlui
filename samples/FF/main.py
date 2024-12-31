import pyxel
pyxel.init(256, 256)

# ここからゲーム本体開始
# *********************************************************
from xmlui.ext.scene import XUXSceneManager

from shop import Shop

# 最初はショップ
scene_manager = XUXSceneManager(Shop())

# Main
def update(): # フレームの更新処理
    # デバッグ用
    if pyxel.btnp(pyxel.KEY_TAB):
        print(scene_manager.current_scene.xmlui.strtree()) # type: ignore
    if pyxel.btnp(pyxel.KEY_F5):
        scene_manager.current_scene.xmlui.reload_templates() # type: ignore

    # シーン更新
    scene_manager.update()

def draw(): # 描画処理
    # ゲームの描画コード
    pyxel.cls(0)

    # シーン描画
    scene_manager.draw()

# アプリケーションの実行
pyxel.run(update, draw)

