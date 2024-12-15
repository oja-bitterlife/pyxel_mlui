import pyxel

# タイトル画面
from xmlui.core import XMLUI,XUEvent,XUWinBase,XUTextUtil,XURect
from xmlui.lib import select,text,input
from ui_common import ui_theme
from params import param_db

class Battle:
    UI_TEMPLATE_BATTLE = "ui_battle"

    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui

        # UIの読み込み
        self.template = self.xmlui.load_template("assets/ui/battle.xml")
        ui_init(self.template)

        # バトル開始UI初期化
        battle = self.xmlui.open("battle")
        battle.find_by_tag("msg_text").set_text("てきが　あらわれた")

    def __del__(self):
        # 読みこんだUIの削除
        self.template.remove()

    def update(self):
        if not self.xmlui.exists_id("menu"):
            msg_text = self.xmlui.find_by_tag("msg_text")
            text.MsgDQ.start_system(msg_text, msg_text.text + "\n" + "コマンド？")

            # コマンド待ち開始
            self.xmlui.open("menu")
            
    def draw(self):
        # UIの描画(fieldとdefaultグループ)
        self.xmlui.draw()

# バトルUI
# *****************************************************************************
from ui_common import common_msg_text, get_world_clip, draw_menu_cursor

def ui_init(template):
    # fieldグループ用デコレータを作る
    battle_select = select.Decorator(template)
    battle_text = text.Decorator(template)

    # コマンドメニューのタイトル
    @battle_text.label("title", "align", "valign")
    def title(title:text.Label, event:XUEvent):
        clip = get_world_clip(XUWinBase.find_parent_win(title)).intersect(title.area)
        pyxel.rect(title.area.x, title.area.y, title.area.w, clip.h, 0)  # タイトルの下地

        # テキストはセンタリング
        if title.area.y < clip.bottom():  # world座標で比較
            x, y = title.aligned_pos(ui_theme.font.system)
            pyxel.text(x, y-1, title.text, 7, ui_theme.font.system.font)

    # メニューアイテム
    # ---------------------------------------------------------
    @battle_select.item("menu_item")
    def menu_item(menu_item:select.Item, event:XUEvent):
        # ウインドウのクリップ状態に合わせて表示する
        if menu_item.area.y < get_world_clip(XUWinBase.find_parent_win(menu_item)).bottom():
            pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, 7, ui_theme.font.system.font)

            # カーソル表示
            if menu_item.selected and menu_item.enable:
                draw_menu_cursor(menu_item, 0, 0)

    # コマンドメニュー
    # ---------------------------------------------------------
    @battle_select.grid("menu_grid", "menu_item", "rows", "item_w", "item_h")
    def menu_grid(menu_grid:select.Grid, event:XUEvent):
        # メニュー選択
        input_def = ui_theme.input_def
        menu_grid.select_by_event(event.trg, *input_def.CURSOR)

        # 選択アイテムの表示
        if input_def.BTN_A in event.trg:
            match menu_grid.action:
                case "attack":
                    menu_grid.xmlui.popup("common", "under_construct")
                case "spel":
                    menu_grid.xmlui.popup("common", "under_construct")
                case "run":
                    menu_grid.xmlui.popup("common", "under_construct")
                case "tools":
                    menu_grid.open("tools")

        # # アイテムの無効化(アイテムカーソル用)
        # is_message_oepn = menu_grid.xmlui.exists_id("message")
        # for item in menu_grid._items:
        #     item.enable = event.is_active and not is_message_oepn


    @battle_text.msg_dq("msg_text")
    def msg_text(msg_text:text.MsgDQ, event:XUEvent):
        # メッセージ共通処理
        common_msg_text(msg_text, event)

        if msg_text.is_all_finish:
            return "finish_msg"
