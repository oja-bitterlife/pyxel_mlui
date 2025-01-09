from enum import StrEnum,auto
import pyxel

from xmlui.core import *
from xmlui.lib.text import MsgScr

from DQ.system import system_font
from DQ.db import user_config

from DQ.ui_common import draw_msg_cursor,get_world_clip,get_text_color

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
    def dq_scroll_lines(self, scroll_line_num:int) -> list[DQLineInfo]:
        line_info_list = super().get_scroll_lines(scroll_line_num)

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
        for page in self.append_zenkaku(text, all_params):
            # 追加されたページにTALKをマーキング
            page_item = XUPageItem(page).set_attr(MsgDQ.INDENT_TYPE_ATTR, MsgDQ.IndentType.TALK)
            page._element.text = self.TALK_START + page_item.all_text

    # Enemyマークを追加して格納
    def append_enemy(self, text:str, all_params:dict[str,Any]={}):
        for page in self.append_zenkaku(text, all_params):
            # 追加されたページにTALKをマーキング
            page_item = XUPageItem(page).set_attr(MsgDQ.INDENT_TYPE_ATTR, MsgDQ.IndentType.ENEMY)
            page._element.text = page_item.all_text


    # メッセージ描画
    def draw(self, event:XUEvent, cursor_visible:bool):
        area = self.area  # areaは重いので必ずキャッシュ
        line_height = system_font.size + 5  # 行間設定
        page_line_num = self.attr_int(self.PAGE_LINE_NUM_ATTR)
        scroll_line_num = page_line_num + 1  # スクロールバッファサイズはページサイズ+1
        scroll_split = 3  # スクロールアニメ分割数

        # テキストが空
        if not self.pages:
            return

        # カウンタ操作
        # ---------------------------------------------------------
        # ボタンを押している間は速度MAX
        speed = user_config.msg_spd
        if XUEvent.Key.BTN_A in event.now or XUEvent.Key.BTN_B in event.now:
            speed = user_config.MsgSpd.FAST

        # カウンタを進める。必ず行端で一旦止まる
        remain_count = self.current_page.current_line_length - len(self.current_page.current_line)
        self.current_page.draw_count += min(remain_count, speed.value)

        # 行が完了してからの経過時間
        if self.is_line_end:
            over_count = self.attr_int("_over_count") + 1
            # ページ切り替えがあったらリセット
            if self.current_page_no != self.attr_int("_old_page", -1):
                over_count = 0
        else:
            over_count = 0

        # 更新
        self.set_attr("_over_count", over_count)
        self.set_attr("_old_page", self.current_page_no)

        # 表示バッファ
        # ---------------------------------------------------------
        scroll_info =  self.dq_scroll_lines(scroll_line_num)

        # スクロール
        shift_y = 0
        # ページが完了している
        if self.current_page.is_finish:
            # スクロールが必要？
            if len(scroll_info) > page_line_num:
                # スクロールが終わった
                if over_count >= scroll_split:
                    scroll_info = scroll_info[1:]
                # スクロール
                else:
                    shift_y = min(over_count,scroll_split) * line_height*0.8 / scroll_split

        # 行だけが完了している
        elif self.is_line_end:
            # スクロールが必要？
            if len(scroll_info) > page_line_num:
                # スクロールが終わった
                if over_count >= scroll_split:
                    scroll_info = scroll_info[1:]
                    self.current_page.draw_count = int(self.current_page.draw_count) + 1  # 次の文字へ
                    self.set_attr("_over_count", 0)  # 最速表示対応
                # スクロール
                else:
                    shift_y = min(over_count,scroll_split) * line_height*0.8 / scroll_split

            # スクロールが不要でも一瞬待機
            elif over_count >= scroll_split:
                self.current_page.draw_count = int(self.current_page.draw_count) + 1  # 次の文字へ
                self.set_attr("_over_count", 0)  # 最速表示対応


        # テキスト描画
        for i,info in enumerate(scroll_info):
            # yはスクロール考慮
            y = area.y + i*line_height - shift_y
            clip = get_world_clip(XUWinBase.find_parent_win(self)).intersect(self.area)
            if y+system_font.size >= clip.bottom():  # メッセージもクリップ対応
                break

            # インデント設定
            x = area.x
            if info.indent_type == MsgDQ.IndentType.TALK:
                x += system_font.text_width(MsgDQ.TALK_START)
            elif info.indent_type == MsgDQ.IndentType.ENEMY:
                x += system_font.size

            col = get_text_color()
            pyxel.text(x, y, info.line_text, col, system_font.font)


        # カーソル表示
        # ---------------------------------------------------------
        if cursor_visible and self.is_next_wait and shift_y == 0:  # ページ送り待ち中でスクロール中でない
            cursor_count = self.current_page.draw_count - self.current_page.length
            if cursor_count//7 % 2 == 0:
                draw_msg_cursor(self, 0, (scroll_line_num-1)*line_height-4)



# デコレータを用意
# *****************************************************************************
class Decorator(XMLUI.HasRef):
    def msg_dq(self, tag_name:str):
        def wrapper(bind_func:Callable[[MsgDQ,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(MsgDQ(elem), event)
            # 関数登録
            self.xmlui.set_drawfunc(tag_name, draw)
        return wrapper
