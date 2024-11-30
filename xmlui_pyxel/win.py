import pyxel

from xmlui_core import *
from . import font

# ウインドウ基底
# *****************************************************************************
# アクティブカラーにする
def _active_color(state:XUStateRO, color:int):
        return 10 if  state.xmlui.debug.is_lib_debug and state.xmlui.active_state == state and color == 7 else color

class _BaseRound(XUWinRound):
    DEFAULT_PAT = [7,7,12]

    def __init__(self, state:XUStateRO, speed:float=16):
        pat = [_active_color(state, c)  for c in self.DEFAULT_PAT]  # アクティブカラーに
        super().__init__(state, pat, pyxel.width, pyxel.height)

        self.set_attr("speed", speed)

    def draw(self):
        self.clip.h = int(self.update_count*self.speed)
        self.draw_buf(pyxel.screen.data_ptr())

class _BaseRect(XUWinRect):
    DEFAULT_PAT = [7,7,12]

    def __init__(self, state:XUStateRO, speed:float=16):
        pat = [_active_color(state, c)  for c in self.DEFAULT_PAT]  # アクティブカラーに
        super().__init__(state, pat, pyxel.width, pyxel.height)

        self.set_attr("speed", speed)

    def draw(self):
        self.clip.h = int(self.update_count*self.speed)
        self.draw_buf(pyxel.screen.data_ptr())


# グリッドメニュー付きウインドウ
# *****************************************************************************
class MenuRO(_BaseRound):
    def __init__(self, state:XUStateRO, tag_group:str, tag_item:str):
        super().__init__(state)
        self._grid_root = XUSelectGrid(state, tag_group, tag_item)

    def draw(self):
        super().draw()  # ウインドウ描画

        for group in self._grid_root._grid:
            for item in group:
                if self.clip.h >= item.area.y-self.area.y + font.size:  # ウインドウが表示されるまで表示しない
                    pyxel.text(item.area.x+6, item.area.y, item.text, 7, font.data)

    @property
    def selected_item(self) -> XUStateRO:
        return self._grid_root.selected_item

class Menu(MenuRO):
    def __init__(self, state:XUState, tag_group:str, tag_item:str):
        super().__init__(state, tag_group, tag_item)

    def arrange_items(self, w:int, h:int):
        self._grid_root.arrange_items(w, h)

    def select_by_event(self, left:str, right:str, up:str, down:str) -> XUState:
        if self.xmlui.active_state == self:
            self._grid_root.select_by_event(self.xmlui.event.trg, left, right, up, down)
        return self.selected_item

    @property
    def selected_item(self) -> XUState:
        return self._grid_root.selected_item


# デコレータを用意
def menu_update_bind(xmlui:XMLUI, tag_name:str, tag_group:str, tag_item:str):
    def wrapper(update_func:Callable[[Menu,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(Menu(state, tag_group, tag_item), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def menu_draw_bind(xmlui:XMLUI, tag_name:str, tag_group:str, tag_item:str):
    def wrapper(draw_func:Callable[[MenuRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(MenuRO(state, tag_group, tag_item), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper


# リストウインドウ
# *****************************************************************************
class ListRO(_BaseRound):
    def __init__(self, state:XUStateRO, tag_item:str):
        super().__init__(state)
        self._grid_root = XUSelectList(state, tag_item)

    def draw(self):
        super().draw()  # ウインドウ描画

        for group in self._grid_root._grid:
            item = group[0]
            if self.clip.h >= item.area.y-self.area.y + font.size:  # ウインドウが表示されるまで表示しない
                pyxel.text(item.area.x+6, item.area.y, item.text, 7, font.data)

    @property
    def selected_item(self) -> XUStateRO:
        return self._grid_root.selected_item

class List(ListRO):
    def __init__(self, state:XUState, tag_item:str):
        super().__init__(state, tag_item)

    def arrange_items(self, w:int, h:int):
        self._grid_root.arrange_items(w, h)

    def select_by_event(self, up:str, down:str) -> XUState:
        if self.xmlui.active_state == self:
            self._grid_root.select_by_event(self.xmlui.event.trg, up, down)
        return self.selected_item

    @property
    def selected_item(self) -> XUState:
        return self._grid_root.selected_item


# デコレータを用意
def list_update_bind(xmlui:XMLUI, tag_name:str, tag_item:str):
    def wrapper(update_func:Callable[[List,XUEvent], None]):
        # 登録用関数をジェネレート
        def update(state:XUState, event:XUEvent):
            update_func(List(state, tag_item), event)
        # 関数登録
        xmlui.set_updatefunc(tag_name, update)
    return wrapper

def list_draw_bind(xmlui:XMLUI, tag_name:str, tag_item:str):
    def wrapper(draw_func:Callable[[ListRO,XUEvent], None]):
        # 登録用関数をジェネレート
        def draw(state:XUStateRO, event:XUEvent):
            draw_func(ListRO(state, tag_item), event)
        # 関数登録
        xmlui.set_drawfunc(tag_name, draw)
    return wrapper


# メッセージウインドウ
# *****************************************************************************
class MsgRO(_BaseRound):
    LINE_NUM_ATTR = "lines"  # ページの行数
    WRAP_ATTR = "wrap"  # ワードラップ文字数

    # tag_textタグのテキストを処理する
    def __init__(self, state:XUStateRO, tag_text:str):
        super().__init__(state)

        # tag_textタグ下にpage管理タグとpage全部が入っている
        root = state.find_by_tag(tag_text)
        self.page = XUPageRO(root)

    def draw(self):
        super().draw()  # ウインドウ描画

        # テキスト描画
        for i,page in enumerate(self.page.page_text.split()):
            if self.page.page_root.valid > 0:  # 子を強制描画するのでvaliedチェック
                area = self.page.page_root.area
                pyxel.text(area.x, area.y+i*font.size, page, 7, font.data)

class Msg(MsgRO):
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
