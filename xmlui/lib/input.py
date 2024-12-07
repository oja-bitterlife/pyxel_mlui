from xmlui.xmlui_core import *
from ..lib import text

# 入力系
# #############################################################################
# 数値設定ダイアル
class Dial(XUDial):
    PAGE_LINES_ATTR = "page_lines"  # ページの行数
    WRAP_ATTR = "wrap"  # ワードラップ文字数

    # タグのテキストを処理する
    def __init__(self, state:XUState, digit_length:int, align:str, valign:str, digit_list:str):
        super().__init__(state, digit_length, digit_list)
        self._align = align
        self._valign = valign

    def aligned_pos(self, font:text.FontBase, w:int=0, h:int=0) -> tuple[int, int]:
        area = self.area  # 低速なので使うときは必ず一旦ローカルに
        x = area.aligned_x(font.text_width(self.digits) + w, self._align)
        y = area.aligned_y(font.size+h, self._valign)
        return x, y

    def aligned_zenkaku_pos(self, font:text.FontBase, w:int=0, h:int=0) -> tuple[int, int]:
        area = self.area  # 低速なので使うときは必ず一旦ローカルに
        x = area.aligned_x(font.text_width(self.zenkaku_digits) + w, self._align)
        y = area.aligned_y(font.size+h, self._valign)
        return x, y


# デコレータを用意
# *****************************************************************************
class Decorators:
    def __init__(self, xmlui:XMLUI, group:str):
        self.xmlui = xmlui
        self.group = group

    def __del__(self):
        self.xmlui.remove_drawfunc(self.group)

    # デコレータを用意
    def dial(self, tag_name:str, digit_length:int, align:str="center", valign:str="center", digit_list:str="0123456789"):
        def wrapper(bind_func:Callable[[Dial,XUEvent], None]):
            # 登録用関数をジェネレート
            def draw(state:XUState, event:XUEvent):
                bind_func(Dial(state, digit_length, align, valign, digit_list), event)
            # 関数登録
            self.xmlui.set_drawfunc(self.group, tag_name, draw)
        return wrapper
