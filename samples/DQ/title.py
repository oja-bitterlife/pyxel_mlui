import pyxel

# タイトル画面
from xmlui.core import XMLUI,XUTemplate,XUEvent
from xmlui.lib import select
from ui_common import ui_theme

class Title:
    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui
        self.template = self.xmlui.load_template("assets/ui/title.xml")
        self.xmlui.open("game_title")

        ui_init(self.template)

    def __del__(self):
        self.template.remove()

    def update(self):
        if "game_start" in self.xmlui.event.trg:
            return "field"
        return None

    def draw(self):
        self.xmlui.draw()


# タイトル画面UI
# ---------------------------------------------------------
from ui_common import draw_menu_cursor
def ui_init(template:XUTemplate):
    title_select = select.Decorator(template)

    @title_select.list("game_start", "menu_item")
    def game_start(game_start:select.List, event:XUEvent):
        # メニュー選択
        input_def = ui_theme.input_def
        game_start.select_by_event(event.trg, *input_def.UP_DOWN)
        if input_def.BTN_A in event.trg:
            match game_start.action:
                case "start":
                    game_start.close()
                    game_start.xmlui.on("game_start")
                case "continue":
                    game_start.xmlui.popup("under_construct")

    @title_select.list("game_speed", "menu_item")
    def game_speed(game_speed:select.List, event:XUEvent):
        # メニュー選択。カーソルが動いたらTrueが返る
        input_def = ui_theme.input_def
        if game_speed.select_by_event(event.trg, *input_def.LEFT_RIGHT):
            # メッセージスピードを切り替える
            match game_speed:
                case "slow":
                    print("msg is slow")
                case "normal":
                    print("msg is normal")
                case "fast":
                    print("msg is fast")

    # メニューアイテム
    # ---------------------------------------------------------
    @title_select.item("menu_item")
    def start_item(menu_item:select.Item, event:XUEvent):
        area = menu_item.area
        pyxel.text(area.x+6, area.y, menu_item.text, 7, ui_theme.font.system.font)
    
        # カーソル追加
        if menu_item.selected:
            draw_menu_cursor(menu_item, 0, 1)
