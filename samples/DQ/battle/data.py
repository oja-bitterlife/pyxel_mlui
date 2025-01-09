from xmlui.core import XMLUI

# バトル時データ
class BattleData:
    def __init__(self, xmlui:XMLUI["BattleData"]):
        super().__init__()
        self.xmlui = xmlui

        # データ受け渡しをここでやってみる
        self.sway_x = 0
        self.sway_y = 0
        self.blink = False
