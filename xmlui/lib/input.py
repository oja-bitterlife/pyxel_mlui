from xmlui.core import *

# 入力系
# #############################################################################
# 数値設定ダイアル
class Dial(XUSelectNum):
    ITEM_W_ATTR = "item_w"  # ワードラップ文字数

    # タグのテキストを処理する
    def __init__(self, elem:XUElem, item_tag:str):
        item_w = elem.attr_int(self.ITEM_W_ATTR, 0)
        super().__init__(elem, item_tag, item_w)

    # def aligned_pos(self, font:FontBase) -> tuple[int, int]:
    #     area = self.area  # 低速なので使うときは必ず一旦ローカルに
    #     return area.aligned_pos(font.text_width(self.digits), font.size, self.align, self.valign)


# デコレータを用意
# *****************************************************************************
class Decorator(XUTemplate.HasRef):
    # デコレータを用意
    def dial(self, tag_name:str, item_tag:str):
        def wrapper(bind_func:Callable[[Dial,XUEvent], str|None]):
            # 登録用関数をジェネレート
            def draw(elem:XUElem, event:XUEvent):
                return bind_func(Dial(elem, item_tag), event)
            # 関数登録
            self.template.set_drawfunc(tag_name, draw)
        return wrapper
