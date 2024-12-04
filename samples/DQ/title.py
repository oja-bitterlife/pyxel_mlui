import pyxel

# タイトル画面
from xmlui_core import XMLUI,XUState,XUEvent
from xmlui_pyxel import xmlui_pyxel_init,select,text,win,input

class Title:
    def __init__(self):
        self.ui_setup()

    def update(self):
        pass

    def draw(self):
        self.start_ui.check_input_on(pyxel.btn)
        self.start_ui.draw()

        self.speed_ui.check_input_on(pyxel.btn)
        self.speed_ui.draw()

    # UI
    # *****************************************************************************
    def ui_setup(self):
        self.start_ui = XMLUI()
        self.speed_ui = XMLUI()

        # 初期化セット
        xmlui_pyxel_init(self.start_ui,
            inputlist_dict = input.INPUT_LIST,
            font_path = "../common_assets/font/b12.bdf"
        )
        xmlui_pyxel_init(self.speed_ui,
            inputlist_dict = input.INPUT_LIST,
            font_path = "../common_assets/font/b12.bdf"
        )

        # (ライブラリ開発用)
        self.start_ui.debug.level = self.start_ui.debug.DEBUG_LEVEL_LIB
        self.speed_ui.debug.level = self.speed_ui.debug.DEBUG_LEVEL_LIB

        self.start_ui.template_fromfile("assets/ui/dq.xml", "title")
        self.speed_ui.template_fromfile("assets/ui/dq.xml", "title")
        self.start_ui.open("title", "game_start")
        self.speed_ui.open("title", "game_speed")

        # カーソル描画
        def draw_menu_cursor(state:XUState, x:int, y:int):
            tri_size = 6
            left = state.area.x + x
            top = state.area.y+2 + y
            pyxel.tri(left, top, left, top+tri_size, left+tri_size//2, top+tri_size//2, 7)

        @select.list(self.start_ui, "menu_list", "menu_item", "item_w", "item_h")
        def start_menu(list_win:select.List, event:XUEvent):
            # メニュー選択
            list_win.select_by_event(event.trg, *input.UP_DOWN)
            # カーソル追加
            draw_menu_cursor(list_win.selected_item, 0, 1)

        @select.list(self.speed_ui, "menu_list", "menu_item", "item_w", "item_h")
        def speed_menu(list_win:select.List, event:XUEvent):
            # メニュー選択
            list_win.select_by_event(event.trg, *input.LEFT_RIGHT)
            # カーソル追加
            draw_menu_cursor(list_win.selected_item, 0, 1)

        # メニューアイテム
        # ---------------------------------------------------------
        @select.item(self.start_ui, "menu_item")
        def start_item(menu_item:select.Item, event:XUEvent):
            pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, 7, text.default.font)

        @select.item(self.speed_ui, "menu_item")
        def speed_item(menu_item:select.Item, event:XUEvent):
            pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, 7, text.default.font)
