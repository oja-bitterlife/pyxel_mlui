# 今回はpyxel向けのライブラリを作るのです
import pyxel

# ここからゲーム本体開始
# *********************************************************
pyxel.init(256, 256)

from xmlui.core import XUEvent
from xmlui.lib.pyxel_util import PyxelInput
from ui_common import xmlui

# 最初はタイトル
from title import Title
from field import Field
#from battle import Battle

scene = Title(xmlui)
#scene = Field(xmlui)
#scene = Battle(xmlui)

# Main
def update(): # フレームの更新処理
    global scene
    if scene:
        # ゲームの更新コード
        next_scene = scene.update()
        if next_scene is not None:
            match next_scene:
                case "title":
                    scene = Title(xmlui)
                case "field":
                    scene = Field(xmlui)
                # case "battle":
                #     scene = Battle(xmlui)

    # デバッグ用
    if pyxel.btnp(pyxel.KEY_TAB):
        print(xmlui.strtree())
    if pyxel.btnp(pyxel.KEY_F5):
        xmlui.reload_templates()

def draw(): # 描画処理
    # ゲームの描画コード
    pyxel.cls(0)

    # UI用キー入力
    PyxelInput(xmlui).check()

    # UI描画
    global scene
    scene.draw()

# アプリケーションの実行
pyxel.run(update, draw)
