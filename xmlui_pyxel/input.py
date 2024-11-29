import pyxel

from xmlui_core import *

# デフォルトインプット設定
DEFAULT_INPUTLIST_DICT = {
    "up": [
        pyxel.GAMEPAD1_BUTTON_DPAD_UP,
        pyxel.KEY_UP,
        pyxel.KEY_W,
    ],
    "down": [
        pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
        pyxel.KEY_DOWN,
        pyxel.KEY_S,
    ],
    "left": [
        pyxel.GAMEPAD1_BUTTON_DPAD_LEFT,
        pyxel.KEY_LEFT,
        pyxel.KEY_A,
    ],
    "right": [
        pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT,
        pyxel.KEY_RIGHT,
        pyxel.KEY_D,
    ],
    "button_a": [
        pyxel.GAMEPAD1_BUTTON_A,
        pyxel.KEY_RETURN,
        pyxel.KEY_SPACE,
    ],
    "button_b": [
        pyxel.GAMEPAD1_BUTTON_B,
        pyxel.KEY_BACKSPACE,
    ],
    "button_X": [
        pyxel.GAMEPAD1_BUTTON_X,
    ],
    "button_y": [
        pyxel.GAMEPAD1_BUTTON_Y,
    ]
}

def set_Inputlist_fromdict(xmlui:XMLUI, dict_:dict[str,list[int]]):
    for key,value in dict_.items():
        xmlui.set_inputlist(key, value)

