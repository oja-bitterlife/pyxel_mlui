from xmlui.core import *

# フォントを扱う
# #############################################################################
class FontBase:
    def __init__(self, font:Any, size:int):
        self.font = font
        self.size = size

    # フォントサイズ算出
    @classmethod
    def get_bdf_size(cls, bdf_font_path):
        with open(bdf_font_path, "r") as f:
            for i, line in enumerate(f.readlines()):
                if i > 100:  # 100行も見りゃええじゃろ...
                    raise Exception(f"{bdf_font_path} has not PIXEL_SIZE")
                if line.startswith("PIXEL_SIZE"):
                    return int(line.split()[-1])
        raise Exception(f"{bdf_font_path} has not PIXEL_SIZE")

    def text_width(self, text:str) -> int:
        return len(text) * self.size

    def text_height(self, text:str) -> int:
        return len(text.splitlines()) * self.size


# テキストを扱う
# #############################################################################
# ラベル
class Label(XUElem):
    def __init__(self, elem:XUElem, align_attr:str, valign_attr:str):
        super().__init__(elem.xmlui, elem._element)
        self.align = elem.attr_str(align_attr, "left")
        self.valign = elem.attr_str(valign_attr, "top")

    def aligned_pos(self, font:FontBase) -> tuple[int, int]:
        area = self.area
        return area.aligned_pos(font.text_width(self.text), font.size, self.align, self.valign)

# メッセージ
class Msg(XUPageText):
    PAGE_LINE_NUM_ATTR = 'page_line_num'
    WRAP_ATTR = 'wrap'

    # タグのテキストを処理する
    def __init__(self, elem:XUElem):
        page_line_num = elem.attr_int(self.PAGE_LINE_NUM_ATTR, 1024)
        wrap = elem.attr_int(self.WRAP_ATTR, 4096)
        super().__init__(elem, page_line_num, wrap)

    # スクロール用
    # -----------------------------------------------------
    # 全体スクロール用。[-line_num:-lime_num+size]で好きな範囲を拾える
    @property
    def all_lines(self) -> list[str]:
        return sum([page.all_text.splitlines() for page in self.pages], [])

    # 必要な行だけ返す(アニメーション対応)
    def get_scroll_lines(self, scroll_size:int) -> list[str]:
        # スクロール枠の中に収まる行を取得する
        all_lines = []
        for i in range(self.page_no-1, -1, -1):  # 現在より前へ戻りながら追加
            all_lines = self.pages[i].all_text.splitlines() + all_lines
            if len(all_lines) >= scroll_size:
                break
        all_lines += self.current_page.text.splitlines()  # 現在のページを追加

        # scroll枠に収まるlineリストを返す
        return all_lines[-scroll_size:]

    @classmethod
    def clear_msg(cls, elem:XUElem):
        XUPageInfo(elem).clear_pages()

    @classmethod
    def append_msg(cls, elem:XUElem, text:str, all_params:dict[str,Any]={}):
        page_line_num = elem.attr_int(cls.PAGE_LINE_NUM_ATTR, 1024)
        wrap = elem.attr_int(cls.WRAP_ATTR, 4096)
        XUPageInfo(elem).add_pages(XUTextUtil.format_dict(text, all_params), page_line_num, wrap)

    @classmethod
    def start_msg(cls, elem:XUElem, text:str, all_params:dict[str,Any]={}):
        cls.clear_msg(elem)
        cls.append_msg(elem, text, all_params)

# おまけ
class MsgDQ(Msg):
    TALK_MARK = "＊「"
    IS_TALK_ATTR = "_xmlui_talk_mark"

    @property
    def is_talk(self):
        return self.attr_bool(self.IS_TALK_ATTR, False)

    @classmethod
    def start_talk(cls, elem:XUElem, text:str, all_params:dict[str,Any]={}):
        elem.set_attr(cls.IS_TALK_ATTR, True)
        cls.start_msg(elem, text, all_params)

        # 会話マーク追加
        for page in XUPageText(elem).pages:
            page._element.text = cls.TALK_MARK + page.all_text

    @classmethod
    def start_system(cls, elem:XUElem, text:str, all_params:dict[str,Any]={}):
        elem.set_attr(cls.IS_TALK_ATTR, False)
        cls.start_msg(elem, text, all_params)

# デコレータを用意
# *****************************************************************************
class Decorator(XUTemplate.HasRef):
    def label(self, tag_name:str, align_attr:str="align", valign_attr:str="valign"):
        def wrapper(bind_func:Callable[[Label,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(Label(elem, align_attr, valign_attr), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper

    def msg(self, tag_name:str):
        def wrapper(bind_func:Callable[[Msg,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(Msg(elem), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper

    def msg_dq(self, tag_name:str):
        def wrapper(bind_func:Callable[[MsgDQ,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(MsgDQ(elem), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper
