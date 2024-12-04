# 今回はpyxel向けのライブラリを作るのです
import pyxel

# ui_code内のUIライブラリへのアクセス
from .ui_code import xmlui,UI_TEMPLATE,input,select

# ここからゲーム本体開始
# *********************************************************
pyxel.init(256, 256)

import title
state = "TITLE"

# Main
def update(): # フレームの更新処理
    # ゲームの更新コード
    if state == "TITLE":
        title.update()

    # # ゲームの中でメインメニューを開く
    # xmlui.open_by_event(input.BTN_A, UI_TEMPLATE, "command_menu_win")

    # dial = xmlui.event.get_state("close", input.Dial)
    # if dial:
    #     print(dial)
    # yes_no = xmlui.event.get_state("dial_yes", select.List)
    # if yes_no:
    #     print(yes_no)

def draw(): # 描画処理
    # ゲームの描画コード
    pyxel.cls(0)

    if state == "TITLE":
        title.draw()

    # UI描画
    xmlui.check_input_on(pyxel.btn)
    xmlui.draw()

# アプリケーションの実行
def run():
    pyxel.run(update, draw)
