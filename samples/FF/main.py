import pyxel
pyxel.init(256, 256)

# ここからゲーム本体開始
# *********************************************************
from xmlui.core import XMLUI
from xmlui.lib import debug
XMLUI.debug_enable = True

# 作成するシーン選択
from xmlui.ext.scene import XUXSceneManager
from shop import Shop
from battle import Battle

scene_manager = XUXSceneManager(Shop())
#scene_manager = XUXSceneManager(Battle())

# Main
def update():
    # デバッグ用
    if pyxel.btnp(pyxel.KEY_TAB):
        scene_manager.current_scene.xmlui.on(debug.DebugXMLUI.DEBUGEVENT_PRINTTREE)
    if pyxel.btnp(pyxel.KEY_F5):
        scene_manager.current_scene.xmlui.on(debug.DebugXMLUI.DEBUGEVENT_RELOAD)

    # シーン更新
    scene_manager.update()

def draw(): # 描画処理
    # ゲームの描画コード
    pyxel.cls(0)

    # シーン描画
    scene_manager.draw()

# アプリケーションの実行
pyxel.run(update, draw)

