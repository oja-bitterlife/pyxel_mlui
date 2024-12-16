import pyxel

# タイトル画面
from xmlui.core import XMLUI,XUTemplate,XUEvent,XUSelectItem
from xmlui.lib import select
from ui_common import input_def,system_font
from system_info import system_info

class Title:
    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui

        # XMLの読み込み
        self.template = self.xmlui.load_template("assets/ui/title.xml")
        self.xmlui.open("game_title")  # game_title以下表示開始

        # 描画関数登録
        ui_init(self.template)

    def __del__(self):
        # XMLの解放
        self.template.remove()

    def update(self):
        # 次のシーンへ
        if "game_start" in self.xmlui.event.trg:
            return "field"

        return None

    def draw(self):
        # UIの表示
        self.xmlui.draw()


# タイトル画面UI
# ---------------------------------------------------------
from ui_common import draw_menu_cursor
def ui_init(template:XUTemplate):
    title_select = select.Decorator(template)

    # START/CONTINUE選択
    @title_select.list("game_start", "menu_item")
    def game_start(game_start:select.List, event:XUEvent):
        for item in game_start.items:
            menu_item(item)

        # メニュー選択
        game_start.select_by_event(event.trg, *input_def.UP_DOWN)

        # メニュー決定
        if input_def.BTN_A in event.trg:
            match game_start.action:
                case "start":
                    return "game_start"
                case "continue":
                    game_start.xmlui.popup("under_construct")

    # メッセージスピード選択
    @title_select.list("game_speed", "menu_item")
    def game_speed(game_speed:select.List, event:XUEvent):
        for item in game_speed.items:
            menu_item(item)

        # メニュー選択。カーソルが動いたらTrueが返る
        if game_speed.select_by_event(event.trg, *input_def.LEFT_RIGHT):
            # メッセージスピードを切り替える
            match game_speed.action:
                case "change_slow":
                    system_info.msg_spd = 1.0/3
                case "change_normal":
                    system_info.msg_spd = 1
                case "change_fast":
                    system_info.msg_spd = 65535

    # メニューアイテム
    # ---------------------------------------------------------
    def menu_item(menu_item:XUSelectItem):
        area = menu_item.area
        pyxel.text(area.x+6, area.y, menu_item.text, 7, system_font.font)
    
        # カーソル追加
        if menu_item.selected:
            draw_menu_cursor(menu_item, 0, 1)
