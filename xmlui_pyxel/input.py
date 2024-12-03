import pyxel

from xmlui_core import *

# キー定義
LEFT = "left"
RIGHT = "right"
UP = "up"
DOWN = "down"
BTN_A = "btn_a"
BTN_B = "btn_b"
BTN_X = "btn_x"
BTN_Y = "btn_y"

# キー定義おまとめ版。*????で展開できる
# 例) select_by_event(LEFT,RIGHT,UP,DOWN) -> select_by_event(*CURSOR_LRUD)
CURSOR = [LEFT, RIGHT, UP, DOWN]
UP_DOWN = [UP, DOWN]
LEFT_RIGHT = [LEFT, RIGHT]
ANY = CURSOR + [BTN_A, BTN_B, BTN_X, BTN_Y]

# デフォルトインプット設定
INPUT_LIST = {
    UP: [
        pyxel.GAMEPAD1_BUTTON_DPAD_UP,
        pyxel.KEY_UP,
        pyxel.KEY_W,
    ],
    DOWN: [
        pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
        pyxel.KEY_DOWN,
        pyxel.KEY_S,
    ],
    LEFT: [
        pyxel.GAMEPAD1_BUTTON_DPAD_LEFT,
        pyxel.KEY_LEFT,
        pyxel.KEY_A,
    ],
    RIGHT: [
        pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT,
        pyxel.KEY_RIGHT,
        pyxel.KEY_D,
    ],
    BTN_A: [
        pyxel.GAMEPAD1_BUTTON_A,
        pyxel.KEY_RETURN,
        pyxel.KEY_SPACE,
    ],
    BTN_B: [
        pyxel.GAMEPAD1_BUTTON_B,
        pyxel.KEY_BACKSPACE,
    ],
    BTN_X: [
        pyxel.GAMEPAD1_BUTTON_X,
    ],
    BTN_Y: [
        pyxel.GAMEPAD1_BUTTON_Y,
    ],
    # デバッグ用
    "DEBUG_PRINT_TREE": [
        pyxel.KEY_TAB,
    ],
}

# ボタン配列の辞書を突っ込むとイベント通知するようになる
def set_Inputlist_fromdict(xmlui:XMLUI, dict_:dict[str,list[int]]):
    for key,value in dict_.items():
        xmlui.set_inputlist(key, value)


# メッセージ
# *****************************************************************************
class Dial(XUDial):
    PAGE_LINES_ATTR = "page_lines"  # ページの行数
    WRAP_ATTR = "wrap"  # ワードラップ文字数

    # タグのテキストを処理する
    def __init__(self, state:XUState, digit_length:int, digit_list:str="0123456789"):
        super().__init__(state, digit_length, digit_list)

# デコレータを用意
def dial(xmlui:XMLUI, tag_name:str, digit_length:int, digit_list:str="0123456789"):
    def wrapper(bind_func:Callable[[Dial,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUState, event:XUEvent):
            bind_func(Dial(state, digit_length, digit_list), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper
