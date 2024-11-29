import xmlui_core as core

# パッケージ一覧
import xmlui_pyxel.input as input
from . import win
from . import font


# XMLUIのおすすめ設定による初期化をよしなにやってくれるやつ
# これを呼ぶだけでだいたいいい感じになるように頑張る
def initialize(
        xmlui:core.XMLUI,
        font_path:str
    ):
    input.set_Inputlist_fromdict(xmlui, input.DEFAULT_INPUT_KEY_DICT)
    font.set_font(font_path)
