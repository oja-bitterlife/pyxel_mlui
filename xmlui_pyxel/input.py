import pyxel

from xmlui_core import *

LEFT = "left"
RIGHT = "right"
UP = "up"
DOWN = "down"
BTN_A = "btn_a"
BTN_B = "btn_b"
BTN_X = "btn_x"
BTN_Y = "btn_y"

CURSOR_LRUD = [LEFT, RIGHT, UP, DOWN]
CURSOR_UD = [UP, DOWN]
CURSOR_LR = [LEFT, RIGHT]

# デフォルトインプット設定
DEFAULT_INPUTLIST_DICT = {
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
    ]
}

def set_Inputlist_fromdict(xmlui:XMLUI, dict_:dict[str,list[int]]):
    for key,value in dict_.items():
        xmlui.set_inputlist(key, value)

