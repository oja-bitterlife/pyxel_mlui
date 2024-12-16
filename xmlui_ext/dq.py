from enum import StrEnum,auto

from xmlui.core import *
from xmlui.lib.text import Msg

# テキストを扱う
# #############################################################################
class MsgDQ(Msg):
    TALK_START = "＊「"
    MARK_ATTR = "_xmlui_talk_mark"

    class Mark(StrEnum):
        NONE = auto()
        TALK = auto()
        ENEMY = auto()

        @classmethod
        def from_str(cls, type_:str) -> "MsgDQ.Mark":
            for v in cls.__members__.values():
                if v == type_:
                    return v
            raise Exception(f"Invalid mark type: {type_}")

    # インデント用
    # -----------------------------------------------------
    class PageItemDQ(XUPageItem):
        def __init__(self, page_item:XUElem):
            super().__init__(page_item)

        def set_mark(self, mark:"MsgDQ.Mark") -> Self:
            self.set_attr(MsgDQ.MARK_ATTR, mark)
            return self

        def get_lines_mark(self) -> "list[MsgDQ.Mark]":
            out:list[MsgDQ.Mark] = []
            for line in self.all_text.splitlines():
                mark = self.attr_str(MsgDQ.MARK_ATTR, MsgDQ.Mark.NONE)
                # 会話開始時はマークなしに
                if mark == MsgDQ.Mark.TALK and line.startswith(MsgDQ.TALK_START):
                     mark = MsgDQ.Mark.NONE
                out.append(MsgDQ.Mark.from_str(mark))
            return out

    # スクロール用
    # -----------------------------------------------------
    class ScrollInfo:
        def __init__(self, line_text:str, mark_type:"MsgDQ.Mark"):
            self.line_text:str = line_text
            self.mark_type:MsgDQ.Mark = mark_type

    # 必要な行だけ返す(アニメーション対応)
    def get_scroll_lines(self, scroll_size:int) -> list[ScrollInfo]:
        # スクロール枠の中に収まる前のページを取得する
        all_lines = []
        mark_type = []
        for i in range(self.page_no-1, -1, -1):  # 現在より前へ戻りながら追加
            page_item = self.PageItemDQ(self.pages[i])

            all_lines = page_item.all_text.splitlines() + all_lines
            mark_type = page_item.get_lines_mark() + mark_type

            if len(all_lines) >= scroll_size:
                break

        # 現在のページの情報を追加
        page_item = self.PageItemDQ(self.current_page)
        all_lines += page_item.text.splitlines()
        mark_type += page_item.get_lines_mark()

        # オーバーした行を削除
        over_line = max(0, len(all_lines) - scroll_size)
        all_lines = all_lines[over_line:]
        mark_type = mark_type[over_line:]

        # scroll枠に収まるlineリストを返す
        return [self.ScrollInfo(line, mark_type[i]) for i,line in enumerate(all_lines)]

    # ページ登録
    # -----------------------------------------------------
    # 会話マークを追加して格納
    def append_talk(self, text:str, all_params:dict[str,Any]={}):
        for page in self.append_msg(text, all_params):
            # 追加されたページにTALKをマーキング
            page_item = self.PageItemDQ(page).set_mark(MsgDQ.Mark.TALK)
            page._element.text = self.TALK_START + page_item.all_text

    # Enemyマークを追加して格納
    def append_enemy(self, text:str, all_params:dict[str,Any]={}):
        for page in self.append_msg(text, all_params):
            # 追加されたページにTALKをマーキング
            page_item = self.PageItemDQ(page).set_mark(MsgDQ.Mark.ENEMY)
            page._element.text = page_item.all_text


# デコレータを用意
# *****************************************************************************
class Decorator(XUTemplate.HasRef):
    def msg_dq(self, tag_name:str):
        def wrapper(bind_func:Callable[[MsgDQ,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(MsgDQ(elem), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper
