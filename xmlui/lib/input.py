from xmlui.core import *
from xmlui.lib.text import FontBase
from xmlui.lib.decorator import DefaultDecorator

# キー入力
# #############################################################################
# 定義のみ
class InputDef:
    LEFT:str
    RIGHT:str
    UP:str
    DOWN:str
    BTN_A:str
    BTN_B:str
    BTN_X:str
    BTN_Y:str

    def __init__(self, left:str, right:str, up:str, down:str, btn_a:str, btn_b:str, btn_x:str, btn_y:str):
        self.LEFT = left
        self.RIGHT = right
        self.UP = up
        self.DOWN = down
        self.BTN_A = btn_a
        self.BTN_B = btn_b
        self.BTN_X = btn_x
        self.BTN_Y = btn_y
    
    @property
    def CURSOR(self):
        return self.LEFT, self.RIGHT, self.UP, self.DOWN

    @property
    def LEFT_RIGHT(self):
        return self.LEFT, self.RIGHT

    @property
    def UP_DOWN(self):
        return self.UP, self.DOWN

    @property
    def ANY(self):
        return self.LEFT, self.RIGHT, self.UP, self.DOWN, self.BTN_A, self.BTN_B, self.BTN_X, self.BTN_Y


# 入力系
# #############################################################################
# 数値設定ダイアル
class Dial(XUDial):
    PAGE_LINES_ATTR = "page_lines"  # ページの行数
    WRAP_ATTR = "wrap"  # ワードラップ文字数

    # タグのテキストを処理する
    def __init__(self, state:XUState, digit_length:int, align:str, valign:str, digit_list:str):
        super().__init__(state, digit_length, digit_list)
        self.align = align
        self.valign = valign

    def aligned_pos(self, font:FontBase) -> tuple[int, int]:
        area = self.area  # 低速なので使うときは必ず一旦ローカルに
        return area.aligned_pos(font.text_width(self.digits), font.size, self.align, self.valign)


# デコレータを用意
# *****************************************************************************
class Decorator(DefaultDecorator):
    def __init__(self, xmlui:XMLUI, group:str|None=None):
        super().__init__(xmlui, group)

    # デコレータを用意
    def dial(self, tag_name:str, digit_length:int, align:str="center", valign:str="center", digit_list:str="0123456789"):
        def wrapper(bind_func:Callable[[Dial,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                return bind_func(Dial(state, digit_length, align, valign, digit_list), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw, self.group)
        return wrapper
