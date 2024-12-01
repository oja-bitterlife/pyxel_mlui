import pyxel

from xmlui_core import *
from . import text

# フォントを扱う
# #############################################################################
default:"FONT" = None # type: ignore

class FONT:
    def __init__(self, font_path:str):
        # フォントデータ読み込み
        self.data = pyxel.Font(font_path)

        # フォントサイズ算出
        self.size = 0
        with open(font_path, "r") as f:
            for i, line in enumerate(f.readlines()):
                if i > 100:  # 100行も見りゃええじゃろ...
                    raise Exception(f"{font_path} has not PIXEL_SIZE")
                if line.startswith("PIXEL_SIZE"):
                    self.size = int(line.split()[-1])
                    break
 
    def text_width(self, text:str) -> int:
        return self.data.text_width(text)

    def draw(self, x:int, y:int, text:str, color:int):
        pyxel.text(x, y, text, color, self.data)


# ラベルを扱う
# #############################################################################
class LabelRO(XUStateRO):
    TEXT_OFFSET_X_ATTR:str = "text_x"
    TEXT_OFFSET_Y_ATTR:str = "text_y"

    def __init__(self, state:XUStateRO, align:str="center"):
        super().__init__(state.xmlui, state._element)
        self._align = align

    def draw(self):
        area = self.area  # 低速なので使うときは必ず一旦ローカルに
        pyxel.rect(area.x, area.y, area.w, area.h, 12)

        text_w = default.text_width(self.text)
        match self.align:
            case "left":
                x =  area.x + self.offset_x
            case "center":
                x = area.center_x(text_w) + self.offset_x
            case "right":
                x = area.right() - text_w - self.offset_x
            case _:
                raise ValueError(f"align:{self.align} is not supported.")

        # ラベルテキスト描画
        default.draw(x, area.center_y(default.size) + self.offset_y, self.text, 7)

    @property
    def align(self) -> str:
        return self._align

    @property
    def offset_x(self) -> int:
        return self.attr_int(self.TEXT_OFFSET_X_ATTR, 0)

    @property
    def offset_y(self) -> int:
        return self.attr_int(self.TEXT_OFFSET_Y_ATTR, 0)

class Label(LabelRO, XUState):
    def __init__(self, state:XUState, align:str="center"):
        super().__init__(state, align)

    def set_offset(self, x:int, y:int):
        rw = self.asRW()
        rw.set_attr(self.TEXT_OFFSET_X_ATTR, x)
        rw.set_attr(self.TEXT_OFFSET_Y_ATTR, y)

# デコレータを用意
def label_update_bind(xmlui:XMLUI, tag_name:str):
    def wrapper(update_func:Callable[[Label,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(Label(state), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def label_draw_bind(xmlui:XMLUI, tag_name:str, align:str="center"):
    def wrapper(draw_func:Callable[[LabelRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(LabelRO(state, align), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper


# メッセージ
# *****************************************************************************
class MsgRO(XUPageRO):
    LINE_NUM_ATTR = "lines"  # ページの行数
    WRAP_ATTR = "wrap"  # ワードラップ文字数

    # tag_textタグのテキストを処理する
    def __init__(self, state:XUStateRO, tag_text:str):
        super().__init__(state)

        # tag_textタグ下にpage管理タグとpage全部が入っている
        root = state.find_by_tag(tag_text)
        self.page = XUPageRO(root)

    def draw(self):
        # テキスト描画
        for i,page in enumerate(self.page.page_text.split()):
            if self.page.page_root.update_count > 0:  # 子を強制描画するので更新済みチェック
                area = self.page.page_root.area
                text.default.draw(area.x, area.y+i*text.default.size, page, 7)

class Msg(MsgRO, XUState):
    # tag_textタグのテキストを処理する
    def __init__(self, state:XUState, tag_text:str):
        # tag_textタグ下にpage管理タグとpage全部が入っている
        # super()でそれらを読むので、super()の前に作っておく
        root = state.find_by_tag(tag_text).asRW()
        page = XUPage(root, root.text, root.attr_int(self.LINE_NUM_ATTR, 1), root.attr_int(self.WRAP_ATTR))

        # page管理タグがなければ新規作成。あればそれを使う
        super().__init__(state, tag_text)

        # super().__init__でself.pageが上書きされるので、あとからself.pageに突っ込み直す
        self.page = page

# デコレータを用意
def msg_update_bind(xmlui:XMLUI, tag_name:str, tag_text:str):
    def wrapper(update_func:Callable[[Msg,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(Msg(state, tag_text), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def msg_draw_bind(xmlui:XMLUI, tag_name:str, tag_text:str):
    def wrapper(draw_func:Callable[[MsgRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(MsgRO(state, tag_text), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper


