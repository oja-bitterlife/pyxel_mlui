# 今回はpyxel向けのライブラリを作るのです
import pyxel

# ここからゲーム本体開始
# *********************************************************
pyxel.init(256, 256)

from xmlui.core import XUEvent
from ui_common import xmlui
from scene import SceneBase

# 最初はタイトル
from title import Title
from field import Field
#from battle import Battle

SceneBase.current_scene = Title(xmlui)
#SceneBase.current_scene = Field(xmlui)
#SceneBase.current_scene = Battle(xmlui)

# Main
def update(): # フレームの更新処理
    # デバッグ用
    if pyxel.btnp(pyxel.KEY_TAB):
        print(xmlui.strtree())
    if pyxel.btnp(pyxel.KEY_F5):
        xmlui.reload_templates()

    # シーン更新
    if SceneBase.current_scene:
        SceneBase.current_scene.update_scene()


def draw(): # 描画処理
    # ゲームの描画コード
    pyxel.cls(0)

    # シーン描画
    if SceneBase.current_scene:
        SceneBase.current_scene.draw_scene()

# アプリケーションの実行
pyxel.run(update, draw)
