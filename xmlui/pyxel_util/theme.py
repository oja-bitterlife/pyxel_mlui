default = """
[win]
frame_pattern = [7, 13]
bg_color = 12

[font]
#system = "assets/font/b12.bdf"

[input]
LEFT = "DIR_L"
RIGHT = "DIR_R"
UP = "DIR_U"
DOWN = "DIR_D"
A = "BTN_A"
B = "BTN_B"
X = "BTN_X"
Y = "BTN_Y"

[debug]
debug_level = 128
"""

import tomllib
from xmlui_core import XMLUI
from lib import input
from pyxel_util.text import PyxelFont

class Theme:
    def __init__(self, xmlui:XMLUI, default_font:PyxelFont):
        self.xmlui = xmlui

        self.toml = tomllib.loads(default)
        self.win = _Win(xmlui, self.toml['win'])
        self.font = _Font(xmlui, self.toml['font'], default_font)
        self.debug = _Debug(xmlui, self.toml['debug'])
        self.input = _Input(xmlui, self.toml['input'])

class _Win:
    def __init__(self, xmlui:XMLUI, section:dict):
        self.frame_pattern = section.get('frame_pattern', [7, 13])
        self.bg_color = section.get('bg_color', 12)

class _Font:
    def __init__(self, xmlui:XMLUI, section:dict, default_font:PyxelFont):
        self.default = default
        self.system = PyxelFont(section["system"]) if "system" in section else default_font

class _Debug:
    def __init__(self, xmlui:XMLUI, section:dict):
        self.debug_level = section.get('debug_level', 0)
        xmlui.debug.level = self.debug_level

class _Input(input.InputDef):
    def __init__(self, xmlui:XMLUI, section:dict):
        super().__init__(
            section.get('LEFT', "DIR_L"),
            section.get('RIGHT', "DIR_R"),
            section.get('UP', "DIR_U"),
            section.get('DOWN', "DIR_D"),
            section.get('A', "BTN_A"),
            section.get('B', "BTN_B"),
            section.get('X', "BTN_X"),
            section.get('Y', "BTN_Y")
        )
