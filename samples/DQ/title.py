# タイトル画面
from xmlui_core import XMLUI
from xmlui_pyxel import xmlui_pyxel_init,select,text,win,input

# ライブラリのインスタンス化
def init():
    global start_ui
    global speed_ui

    start_ui = XMLUI()
    speed_ui = XMLUI()

    # 初期化セット
    xmlui_pyxel_init(start_ui,
            inputlist_dict = input.INPUT_LIST,
            font_path = "../common_assets/font/b12.bdf"
        )

    # (ライブラリ開発用)
    start_ui.debug.level = start_ui.debug.DEBUG_LEVEL_LIB

    start_ui.template_fromfile("assets/ui/dq.xml", "title")
    opened = start_ui.open("title", "game_start")
    print(opened)

def update():

    pass

def draw():
    global start_ui
    start_ui.xmlui.draw()

