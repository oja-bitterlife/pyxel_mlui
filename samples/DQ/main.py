# 今回はpyxel向けのライブラリを作るのです
import pyxel


# ここからゲーム本体開始
# *********************************************************
pyxel.init(256, 256)

from title import Title
from field import Field
from battle import Battle

# 最初はタイトル
from ui_common import xmlui
from ui_common import ui_theme

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
                case "battle":
                    scene = Battle(xmlui)

    # デバッグ用
    if pyxel.btnp(pyxel.KEY_TAB):
        print(xmlui.strtree())

def draw(): # 描画処理
    global scene
    # ゲームの描画コード
    pyxel.cls(0)

    # UI用キー入力
    if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
        xmlui.on(ui_theme.input_def.LEFT)
    if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
        xmlui.on(ui_theme.input_def.RIGHT)
    if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
        xmlui.on(ui_theme.input_def.UP)
    if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
        xmlui.on(ui_theme.input_def.DOWN)
    if pyxel.btn(pyxel.KEY_RETURN) or pyxel.btn(pyxel.KEY_SPACE)  or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
        xmlui.on(ui_theme.input_def.BTN_A)
    if pyxel.btn(pyxel.KEY_BACKSPACE) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_B):
        xmlui.on(ui_theme.input_def.BTN_B)

    # UI描画
    if scene:
        scene.draw()

# アプリケーションの実行
pyxel.run(update, draw)
