# 今回はpyxel向けのライブラリを作るのです
import pyxel
# initを呼ぶまでWebでファイルシステムが使えないことに注意
pyxel.init(256, 256)

# ここからゲーム本体開始
# *********************************************************
from ui_common import xmlui

from xmlui.ext.scene import XUXSceneManager

from title import Title
from field import Field
from battle import Battle

# 最初はタイトル
scene_manager = XUXSceneManager(Title(xmlui))
#scene_manager = XUXSceneManager(Field(xmlui))
#scene_manager = XUXSceneManager(Battle(xmlui))

# Main
def update(): # フレームの更新処理
    # デバッグ用
    if pyxel.btnp(pyxel.KEY_TAB):
        print(xmlui.strtree())
    if pyxel.btnp(pyxel.KEY_F5):
        xmlui.reload_templates()

    # シーン更新
    scene_manager.update()

def draw(): # 描画処理
    # ゲームの描画コード
    pyxel.cls(0)

    # シーン描画
    scene_manager.draw()

# アプリケーションの実行
pyxel.run(update, draw)
