from enum import StrEnum,auto

from xmlui.core import *
from xmlui.lib.text import MsgScr

# テキストを扱う
# #############################################################################
class MsgDQ(MsgScr):
    TALK_START = "＊「"
    INDENT_TYPE_ATTR = "_xmlui_indent_type"

    class IndentType(StrEnum):
        NONE = auto()
        TALK = auto()
        ENEMY = auto()

        @classmethod
        def from_str(cls, type_:str) -> "MsgDQ.IndentType":
            for v in cls.__members__.values():
                if v == type_:
                    return v
            return cls.NONE

    # スクロール用
    # -----------------------------------------------------
    # 各行とその行のインデントタイプを対で保存する
    class DQLineInfo:
        def __init__(self, line_text:str, indent_type:"MsgDQ.IndentType"):
            self.line_text = line_text
            self.indent_type = indent_type

    # 必要な行だけ返す(アニメーション対応)
    def dq_scroll_lines(self, scroll_size:int) -> list[DQLineInfo]:
        line_info_list = super().get_scroll_lines(scroll_size)

        # scroll枠に収まるlineリストを返す
        out = []
        for line_info in line_info_list:
            page_indent = self.IndentType.from_str(line_info.attr_str(self.INDENT_TYPE_ATTR))

            # ENEMYのときは全行ENEMY
            if page_indent == self.IndentType.ENEMY:
                out.append(MsgDQ.DQLineInfo(line_info.text, self.IndentType.ENEMY))
            # TALKの時は行頭以外をTALK
            elif page_indent == self.IndentType.TALK and line_info.page_line_no != 0:
                out.append(MsgDQ.DQLineInfo(line_info.text, self.IndentType.TALK))
            else:
                out.append(MsgDQ.DQLineInfo(line_info.text, self.IndentType.NONE))

        return out

    @property
    def is_line_end(self) -> bool:
        return len(self.current_page.current_line) == self.current_page.current_line_length

    # ページ登録
    # -----------------------------------------------------
    # 会話マークを追加して格納
    def append_talk(self, text:str, all_params:dict[str,Any]={}):
        for page in self.append_msg(text, all_params):
            # 追加されたページにTALKをマーキング
            page_item = XUPageItem(page).set_attr(MsgDQ.INDENT_TYPE_ATTR, MsgDQ.IndentType.TALK)
            page._element.text = self.TALK_START + page_item.all_text

    # Enemyマークを追加して格納
    def append_enemy(self, text:str, all_params:dict[str,Any]={}):
        for page in self.append_msg(text, all_params):
            # 追加されたページにTALKをマーキング
            page_item = XUPageItem(page).set_attr(MsgDQ.INDENT_TYPE_ATTR, MsgDQ.IndentType.ENEMY)
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
