# 今回はpyxel向けのライブラリを作るのです
import pyxel

# ここからゲーム本体開始
# *********************************************************
pyxel.init(256, 256)

from title import Title
from field import Field
# from battle.battle import Battle

# 最初はタイトル
from xmlui.core import XUEvent
from ui_common import xmlui

#scene = Title(xmlui)
scene = Field(xmlui)
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
    if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
        xmlui.on(XUEvent.Key.LEFT)
    if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
        xmlui.on(XUEvent.Key.RIGHT)
    if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
        xmlui.on(XUEvent.Key.UP)
    if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
        xmlui.on(XUEvent.Key.DOWN)
    if pyxel.btn(pyxel.KEY_RETURN) or pyxel.btn(pyxel.KEY_SPACE)  or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
        xmlui.on(XUEvent.Key.BTN_A)
    if pyxel.btn(pyxel.KEY_BACKSPACE) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_B):
        xmlui.on(XUEvent.Key.BTN_B)

    # UI描画
    global scene
    if scene:
        scene.draw()

# アプリケーションの実行
pyxel.run(update, draw)
