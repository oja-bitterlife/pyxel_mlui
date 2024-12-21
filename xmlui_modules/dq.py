from enum import StrEnum,auto

from xmlui.core import *
from xmlui.lib.text import Msg

# テキストを扱う
# #############################################################################
class MsgDQ(Msg):
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
    class ScrollInfo:
        def __init__(self, line_text:str, indent_type:"MsgDQ.IndentType"):
            self.line_text = line_text
            self.indent_type = indent_type

    # 必要な行だけ返す(アニメーション対応)
    def get_scroll_lines(self, scroll_size:int) -> list[ScrollInfo]:

        # 前ページのテキストを行ごとに保存
        text_lines = []
        indent_type = []
        for page_no in range(self.page_no-1, -1, -1):
            append_lines = self.pages[page_no].all_text.splitlines()
            text_lines = append_lines + text_lines

            # ページインデントがENEMYの場合はページ全部ENEMYインデント。TALKのときは行頭だけTALKインデント
            page_indent = self.IndentType.from_str(self.pages[page_no].attr_str(MsgDQ.INDENT_TYPE_ATTR))
            normal_indent = self.IndentType.ENEMY if page_indent == self.IndentType.ENEMY else self.IndentType.NONE
            indent_type = [normal_indent if i == 0 else page_indent for i in range(len(append_lines))] + indent_type

        # 現在のページの表示できるところまで
        for line in self.current_page.text.splitlines():
            text_lines.append(line)
        for i in range(len(self.current_page.all_text.splitlines())):
            # ページインデントがENEMYの場合はページ全部ENEMYインデント。TALKのときは行頭だけTALKインデント
            page_indent = self.IndentType.from_str(self.current_page.attr_str(MsgDQ.INDENT_TYPE_ATTR))
            normal_indent = self.IndentType.ENEMY if page_indent == self.IndentType.ENEMY else self.IndentType.NONE
            indent_type.append(normal_indent if i == 0 else page_indent)

        # オーバーした行を削除
        over_line = max(0, len(text_lines) - scroll_size)
        text_lines = text_lines[over_line:]
        indent_type = indent_type[over_line:]

        # scroll枠に収まるlineリストを返す
        return [self.ScrollInfo(line, indent_type[i]) for i,line in enumerate(text_lines)]

    @property
    def is_line_end(self) -> bool:
        # 現在表示中の行を取得
        anim_last_line = len(self.current_page.text.splitlines())-1
        if(anim_last_line < 0):  # まだ最初
            return False

        # アニメテキストの行の文字数とアニメしないテキストのおなじ行の文字数が一致すれば行末
        anim_last_count = self.current_page.text.splitlines()[anim_last_line]
        all_text_count = self.current_page.all_text.splitlines()[anim_last_line]
        return anim_last_count == all_text_count


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
