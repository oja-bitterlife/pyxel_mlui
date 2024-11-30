import xmlui_core as xuc

# パッケージ一覧
from . import input
from . import font
from . import win
from . import label


# XMLUIのおすすめ設定による初期化をよしなにやってくれるやつ
# これを呼ぶだけでだいたいいい感じになるように頑張る
def initialize(
        xmlui:xuc.XMLUI,
        inputlist_dict: dict[str,list[int]],
        font_path:str
    ):
    input.set_Inputlist_fromdict(xmlui, inputlist_dict)
    font.set_font(font_path)
