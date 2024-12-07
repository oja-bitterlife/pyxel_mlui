import pyxel

# タイトル画面
from xmlui.core import XUState,XUEvent
from xmlui.lib import select,text,input
from ui_common import xmlui,ui_theme,draw_menu_cursor


class Title:
    UI_TEMPLATE_TITLE = "ui_title"

    def __init__(self):
        xmlui.template_fromfile("assets/ui/title.xml", self.UI_TEMPLATE_TITLE)
        xmlui.open(self.UI_TEMPLATE_TITLE, "game_title")

    def __del__(self):
        xmlui.remove_template(self.UI_TEMPLATE_TITLE)
        global title_select
        title_select = None

    def update(self):
        if "game_start" in xmlui.event.trg:
            return "field"
        return None

    def draw(self):
        # キー入力
        if pyxel.btn(pyxel.KEY_LEFT):
            xmlui.on(ui_theme.input_def.LEFT)
        if pyxel.btn(pyxel.KEY_RIGHT):
            xmlui.on(ui_theme.input_def.RIGHT)
        if pyxel.btn(pyxel.KEY_UP):
            xmlui.on(ui_theme.input_def.UP)
        if pyxel.btn(pyxel.KEY_DOWN):
            xmlui.on(ui_theme.input_def.DOWN)
        if pyxel.btn(pyxel.KEY_RETURN) or pyxel.btn(pyxel.KEY_SPACE):
            xmlui.on(ui_theme.input_def.BTN_A)
        if pyxel.btn(pyxel.KEY_BACKSPACE):
            xmlui.on(ui_theme.input_def.BTN_B)

        xmlui.draw()


# タイトル画面UI
# ---------------------------------------------------------
title_select = select.Decorators(xmlui, "title")

@title_select.list("game_start", "menu_item", "item_w", "item_h")
def game_start(game_start:select.List, event:XUEvent):
    # カーソル追加
    draw_menu_cursor(game_start.selected_item, 0, 1)

    # メニュー選択
    input_def = ui_theme.input_def
    game_start.select_by_event(event.trg, *input_def.UP_DOWN)
    if input_def.BTN_A in event.trg:
        match game_start.action:
            case "start":
                game_start.close()
                game_start.xmlui.on("game_start")
            case "continue":
                game_start.xmlui.popup("common", "under_construct")

@title_select.list("game_speed", "menu_item", "item_w", "item_h")
def game_speed(game_speed:select.List, event:XUEvent):
    if event.on_init:  # 初期化
        game_speed.select(1)  # デフォルトはNormal

    # カーソル追加
    draw_menu_cursor(game_speed.selected_item, 0, 1)

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
