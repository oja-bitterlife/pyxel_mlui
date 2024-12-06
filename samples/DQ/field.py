import pyxel

# タイトル画面
from xmlui_core import XUState,XUEvent
from ui_common import xmlui,draw_menu_cursor,draw_msg_cursor
from xmlui_pyxel import select,text,input
from field_player import Player
from field_bg import BG
from field_npc import NPC
from field_treasure import Treasure

class Field:
    UI_TEMPLATE_FIELD = "ui_field"

    def __init__(self):
        xmlui.template_fromfile("assets/ui/field.xml", self.UI_TEMPLATE_FIELD)
        self.player = Player(10, 10)
        self.bg = BG()
        self.npc = NPC()
        self.treasure = Treasure()

    def __del__(self):
        xmlui.remove_template(self.UI_TEMPLATE_FIELD)

        global field_select, field_text
        field_select = None
        field_text = None

    def update(self):
        # メニューが開いていたら他はなにもできない
        if xmlui.exists_id("menu"):
            return None

        # メニューオープン
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
            xmlui.open(self.UI_TEMPLATE_FIELD, "menu")

        # プレイヤの移動
        self.player.update(self.bg.blocks, self.npc.npc)

        return None

    def draw(self):
        scroll_x = -self.player.x +160-32
        scroll_y = -self.player.y +160-32

        # 画面構築
        self.bg.draw(scroll_x, scroll_y)
        self.npc.draw(scroll_x, scroll_y)
        self.treasure.draw(scroll_x, scroll_y)
        self.player.draw()

        # UIの描画
        xmlui.check_input_on(pyxel.btn)
        xmlui.draw()



# 町の中UI
# *****************************************************************************
field_select = select.Decorators(xmlui, "field")
field_text = text.Decorators(xmlui, "field")

# ラベル
# ---------------------------------------------------------
@field_text.label("title", "center", "top")
def title_draw(label:text.Label, event:XUEvent):
    pyxel.rect(label.area.x, label.area.y, label.area.w, label.area.h, 0)
    x, y = label.aligned_pos(text.default)
    pyxel.text(x, y-1, label.text, 7, text.default.font)

# メニューアイテム
# ---------------------------------------------------------
@field_select.item("menu_item")
def menu_item(menu_item:select.Item, event:XUEvent):
    pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, 7, text.default.font)

# コマンドメニュー
# ---------------------------------------------------------
@field_select.grid("menu_grid", "menu_item", "rows", "item_w", "item_h")
def menu_grid(menu_grid:select.Grid, event:XUEvent):
    # メニュー選択
    menu_grid.select_by_event(event.trg, *input.CURSOR)

    # 選択アイテムの表示
    if input.BTN_A in event.trg:
        match menu_grid:
            case "speak":
                menu_grid.open(Field.UI_TEMPLATE_FIELD, "message")
            case "spel":
                menu_grid.open("common", "under_construct")
            case "status":
                menu_grid.open("common", "under_construct")
            case "tools":
                menu_grid.open("common", "under_construct")
            case "step":
                menu_grid.open("common", "under_construct")
            case "check":
                menu_grid.open("common", "under_construct")
            case "door":
                menu_grid.open("common", "under_construct")
            case "take":
                menu_grid.open("common", "under_construct")

    # 閉じる
    if input.BTN_B in event.trg:
        menu_grid.close()

    # カーソル追加
    draw_menu_cursor(menu_grid.selected_item, 0, 0)

# メッセージウインドウ
# ---------------------------------------------------------
@field_text.msg("msg_text")
def msg_text(msg_text:text.Msg, event:XUEvent):
    # カーソル表示
    if msg_text.is_next_wait:
        if msg_text.update_count//15 % 2:
            draw_msg_cursor(msg_text)

    # テキスト表示
    area = msg_text.area  # areaは重いので必ずキャッシュ

    # Scroll
    scroll_cache = msg_text._alllines[msg_text._page_start-msg_text.page_num:msg_text._page_start]
    if msg_text.page_no <= 1:
        scroll_cache = [""] + scroll_cache
    scroll_cache += msg_text.anim.text.splitlines()

    max_line = msg_text._page_lines+2 if not msg_text.anim.is_finish else msg_text._page_lines+1
    scroll_cache = list(reversed(list(reversed(scroll_cache))[:max_line]))

    # テキスト描画
    for i,page in enumerate(scroll_cache):
        pyxel.text(area.x, area.y + i*text.default.size, page, 7, text.default.font)

    # テキストを進める
    msg_text.anim.draw_count += 1

    # 入力アクション
    if input.BTN_A in event.trg or input.BTN_B in event.trg:
        if msg_text.is_finish:
            msg_text.close()  # メニューごと閉じる
        elif msg_text.is_next_wait:
            msg_text.page_no += 1  # 次ページへ
        else:
            msg_text.anim.draw_count = msg_text.anim.length  # 一気に表示
