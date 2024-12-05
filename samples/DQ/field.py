import pyxel

# タイトル画面
from xmlui_core import XUState,XUEvent
from ui_common import xmlui,draw_menu_cursor
from xmlui_pyxel import select,text,input,win

class Field:
    UI_TEMPLATE_FIELD = "ui_field"

    def __init__(self):
        xmlui.template_fromfile("assets/ui/field.xml", self.UI_TEMPLATE_FIELD)
        self.player_x = 10*16
        self.player_y = 10*16
        self.move_x = 0
        self.move_y = 0

    def __del__(self):
        xmlui.remove_template(self.UI_TEMPLATE_FIELD)

    def update(self):
        if xmlui.is_open("menu"):
            return None

        def _hitcheck(x, y):
            block_x = x // 16
            block_y = y // 16
            if self.blocks[block_y][block_x] != 2:
                return False
            for npc in self.npc:
                if npc[1] == block_x and npc[2] == block_y:
                    return False
            return True

        # キー入力チェック
        if self.move_x == 0 and self.move_y == 0:
            if pyxel.btn(pyxel.KEY_UP):
                if _hitcheck(self.player_x, self.player_y-16):
                    self.move_y = -16
            if pyxel.btn(pyxel.KEY_DOWN):
                if _hitcheck(self.player_x, self.player_y+16):
                    self.move_y = 16
            if pyxel.btn(pyxel.KEY_LEFT):
                if _hitcheck(self.player_x-16, self.player_y):
                    self.move_x = -16
            if pyxel.btn(pyxel.KEY_RIGHT):
                if _hitcheck(self.player_x+16, self.player_y):
                    self.move_x = 16

        # プレイヤの移動
        if self.move_x < 0:
            self.player_x -= 1
            self.move_x += 1
        if self.move_x > 0:
            self.player_x += 1
            self.move_x -= 1
        if self.move_y < 0:
            self.player_y -= 1
            self.move_y += 1
        if self.move_y > 0:
            self.player_y += 1
            self.move_y -= 1

        # メニューオープン
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
            xmlui.open(self.UI_TEMPLATE_FIELD, "menu")

        return None

    def draw(self):
        scroll_x = -self.player_x +160-32
        scroll_y = -self.player_y +160-32
        self.draw_bg(scroll_x, scroll_y)
        self.draw_npc(scroll_x, scroll_y)
        self.draw_treasure(scroll_x, scroll_y)
        self.draw_player()

        xmlui.check_input_on(pyxel.btn)
        xmlui.draw()

    def _draw_triangle(self, x, y, color):
        pyxel.tri(x, y+14, x+7, y+1, x+14, y+14, color)

    # 背景
    blocks = [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,2,2,2,2,2,2,2,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,4,4,4,4,4,4,2,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,4,2,4,4,2,4,2,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,2,2,2,2,2,2,2,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,2,2,2,2,2,2,2,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,2,2,2,2,2,2,2,3,1,1,1,1,1],
        [1,1,1,1,1,3,3,3,3,5,3,3,3,3,3,1,1,1,1,1],
        [1,1,1,1,1,3,2,2,2,2,2,2,2,6,3,1,1,1,1,1],
        [1,1,1,1,1,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ]
    def draw_bg(self, scroll_x, scroll_y):
        for y,line in enumerate(self.blocks):
            for x,block in enumerate(line):
                match block:
                    case 1:
                        pyxel.rect(x*16+scroll_x, y*16+scroll_y, 15, 15, 13)
                    case 2:
                        pyxel.rect(x*16+scroll_x, y*16+scroll_y, 15, 15, 4)
                    case 3:
                        pyxel.rect(x*16+scroll_x, y*16+scroll_y, 15, 15, 15)
                    case 4:
                        pyxel.rect(x*16+scroll_x, y*16+scroll_y, 15, 15, 9)
                    case 5:
                        self._draw_triangle(x*16+scroll_x, y*16+scroll_y, 1)
                    case 6:
                        pyxel.rect(x*16+scroll_x, y*16+scroll_y, 15, 15, 1)

    npc = [
        ["king", 8, 8, 2, "おうさま"],
        ["knight1", 8, 11, 3, "兵士1"],
        ["knight2", 10, 11, 3, "兵士2"],
        ["knighg3", 12, 9, 3, "兵士3"],
    ]
    def draw_npc(self, scroll_x, scroll_y):
        for npc in self.npc:
            pyxel.circ(npc[1]*16+scroll_x+7, npc[2]*16+scroll_y+7, 6, npc[3])

    treasure = [
        ["tresure1", 9, 9, 10, "やくそう"],
        ["tresure2", 10, 9, 10, "100G"],
        ["tresure3", 11, 6, 10, "10G"],
    ]
    def draw_treasure(self, scroll_x, scroll_y):
        for treasure in self.treasure:
            pyxel.rect(treasure[1]*16+scroll_x+1, treasure[2]*16+scroll_y+2, 14, 12, treasure[3])

    def draw_player(self):
        pyxel.circ(128+7, 128+7, 7, 12)


# 町の中
# ---------------------------------------------------------
# 角丸ウインドウ
# ---------------------------------------------------------
@win.round(xmlui, "round_win")
def round_win_draw(round_win:win.Round, event:XUEvent):
    clip = round_win.area.to_offset()
    clip.h = int(round_win.update_count*round_win.speed)
    round_win.draw_buf(pyxel.screen.data_ptr(), [7,13,5], 12, clip)

# ラベル
# ---------------------------------------------------------
@text.label(xmlui, "title", "center", "top")
def title_draw(label:text.Label, event:XUEvent):
    pyxel.rect(label.area.x, label.area.y, label.area.w, label.area.h, 12)
    x, y = label.aligned_pos(text.default)
    pyxel.text(x, y, label.text, 7, text.default.font)

# メニューアイテム
# ---------------------------------------------------------
@select.item(xmlui, "menu_item")
def menu_item(menu_item:select.Item, event:XUEvent):
    pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, 7, text.default.font)

# メニュー
# *****************************************************************************
# コマンドメニュー
@select.grid(xmlui, "menu_grid", "menu_item", "rows", "item_w", "item_h")
def menu_grid(menu_grid:select.Grid, event:XUEvent):
    # メニュー選択
    menu_grid.select_by_event(event.trg, *input.CURSOR)

    # 選択アイテムの表示
    if input.BTN_A in event.trg:
        match menu_grid:
            case "speak":
                menu_grid.open(UI_TEMPLATE, "win_message")
            case "dial":
                menu_grid.open(UI_TEMPLATE, "win_dial")
            case "status":
                menu_grid.open(UI_TEMPLATE, "under_construct")

    # 閉じる
    if input.BTN_B in event.trg:
        menu_grid.close()

    # カーソル追加
    draw_menu_cursor(menu_grid.selected_item, 0, 0)
