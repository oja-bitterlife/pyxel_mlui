default = """
[win]
frame_pattern = [7, 13]
bg_color = 0
open_speed = 16
close_speed = 32
closing_wait = 15

[font]
#system = "assets/font/b12.bdf"

[input_def]
LEFT = "CUR_L"
RIGHT = "CUR_R"
UP = "CUR_U"
DOWN = "CUR_D"
A = "BTN_A"
B = "BTN_B"
X = "BTN_X"
Y = "BTN_Y"

[debug]
debug_level = 128
"""

import tomllib
from xmlui.core import XMLUI,XUState
from xmlui.lib import input
from xmlui.pyxel_util.font import PyxelFont

class Theme:
    def __init__(self, xmlui:XMLUI, default_font:PyxelFont):
        self.xmlui = xmlui

        self.toml = tomllib.loads(default)
        self.win = _Win(xmlui, self.toml['win'])
        self.font = _Font(xmlui, self.toml['font'], default_font)
        self.debug = _Debug(xmlui, self.toml['debug'])
        self.input_def = _InputDef(xmlui, self.toml['input_def'])

class _Win:
    def __init__(self, xmlui:XMLUI, section:dict):
        self.frame_pattern = section.get('frame_pattern', [7, 13])
        self.bg_color = section.get('bg_color', 0)
        self.open_speed = section.get('open_speed', 16)  # 16px
        self.close_speed = section.get('close_speed', 16)  # 32px
        self.closing_wait = section.get('closing_wait', 15)  # 0.5s
    
    def get_closing_wait(self, state:XUState):
        owner = state.find_owner()
        return owner.closing_wait if owner.has_attr("closing_wait") else self.closing_wait

class _Font:
    def __init__(self, xmlui:XMLUI, section:dict, default_font:PyxelFont):
        self.default = default
        self.system = PyxelFont(section["system"]) if "system" in section else default_font

class _Debug:
    def __init__(self, xmlui:XMLUI, section:dict):
        self.debug_level = section.get('debug_level', 0)
        xmlui.debug.level = self.debug_level

class _InputDef(input.InputDef):
    def __init__(self, xmlui:XMLUI, section:dict):
        super().__init__(
            section.get('LEFT', "CUR_L"),
            section.get('RIGHT', "CUR_R"),
            section.get('UP', "CUR_U"),
            section.get('DOWN', "CUR_D"),
            section.get('A', "BTN_A"),
            section.get('B', "BTN_B"),
            section.get('X', "BTN_X"),
            section.get('Y', "BTN_Y")
        )
