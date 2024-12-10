import pyxel

# タイトル画面
from xmlui.core import XMLUI,XUEvent,XUWinBase,XUTextPage
from xmlui.lib import select,text
from ui_common import ui_theme
from field_player import Player
from field_bg import BG
from field_npc import NPC
from field_treasure import Treasure

class Field:
    UI_TEMPLATE_FIELD = "ui_field"

    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui

        # ゲーム本体(仮)
        self.player = Player(10, 10)
        self.bg = BG()
        self.npc = NPC()
        self.treasure = Treasure()

        # UIの読み込み
        self.xmlui.template_fromfile("assets/ui/field.xml", self.UI_TEMPLATE_FIELD)
        ui_init(self.xmlui, "field")

    def __del__(self):
        # 読みこんだUIの削除
        self.xmlui.remove_template(self.UI_TEMPLATE_FIELD)
        self.xmlui.remove_drawfunc("field")

    def update(self):
        # UIメニューが開いていたらキャラが動かないように
        if not self.xmlui.exists_id("menu"):
            # プレイヤの移動
            self.player.update(self.bg.blocks, self.npc.npc_data)

            # キャラが動いていなければメニューオープン可能
            if not self.player.is_moving:
                self.xmlui.open_by_event(ui_theme.input_def.BTN_A, self.UI_TEMPLATE_FIELD, "menu")

        else:
            # 会話イベントチェック
            self.npc.check_talk(self.xmlui, self.player)
            self.bg.check_door(self.xmlui, self.player)
            


    def draw(self):
        # プレイヤを中心に世界が動く。さす勇
        scroll_x = -self.player.x +160-32
        scroll_y = -self.player.y +160-32-8

        # ゲーム画面構築
        self.bg.draw(scroll_x, scroll_y)
        self.npc.draw(scroll_x, scroll_y)
        self.treasure.draw(scroll_x, scroll_y)
        self.player.draw()

        # キー入力
        if pyxel.btn(pyxel.KEY_LEFT):
            self.xmlui.on(ui_theme.input_def.LEFT)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.xmlui.on(ui_theme.input_def.RIGHT)
        if pyxel.btn(pyxel.KEY_UP):
            self.xmlui.on(ui_theme.input_def.UP)
        if pyxel.btn(pyxel.KEY_DOWN):
            self.xmlui.on(ui_theme.input_def.DOWN)
        if pyxel.btn(pyxel.KEY_RETURN) or pyxel.btn(pyxel.KEY_SPACE):
            self.xmlui.on(ui_theme.input_def.BTN_A)
        if pyxel.btn(pyxel.KEY_BACKSPACE):
            self.xmlui.on(ui_theme.input_def.BTN_B)

        # UIの描画(fieldとdefaultグループ)
        self.xmlui.draw(["field"])

# 町の中UI
# *****************************************************************************
from ui_common import draw_menu_cursor, draw_msg_cursor, get_world_clip

def ui_init(xmlui, group):
    # fieldグループ用デコレータを作る
    field_select = select.Decorator(xmlui, group)
    field_text = text.Decorator(xmlui, group)

    # ラベル
    # ---------------------------------------------------------
    # コマンドメニューのタイトル
    @field_text.label("title", "align", "valign")
    def title(title:text.Label, event:XUEvent):
        area = title.area
        clip = get_world_clip(XUWinBase.find_win(title)).intersect(area)
        pyxel.rect(area.x, area.y, area.w, clip.h, 0)  # タイトルの下地

        # テキストはセンタリング
        if area.y < clip.bottom():  # world座標で比較
            x, y = title.aligned_pos(ui_theme.font.system)
            pyxel.text(x, y-1, title.text, 7, ui_theme.font.system.font)

    # ステータスウインドウ( ｰ`дｰ´)ｷﾘｯのタイトル
    @field_text.label("status_title", "align", "valign")
    def status_title(status_title:text.Label, event:XUEvent):
        area = status_title.area
        clip = get_world_clip(XUWinBase.find_win(status_title)).intersect(area)
        pyxel.rect(area.x, area.y, area.w, clip.h, 0)  # タイトルの下地

        # テキストは左寄せ
        if area.y < clip.bottom():  # world座標で比較
            x, y = status_title.aligned_pos(ui_theme.font.system)
            pyxel.text(x+1, y-1, status_title.text, 7, ui_theme.font.system.font)


    # コマンドメニューのタイトル
    @field_text.label("menu_item_title", "align", "valign")
    def menu_item_title(menu_item_title:text.Label, event:XUEvent):
        area = menu_item_title.area
        clip = get_world_clip(XUWinBase.find_win(menu_item_title)).intersect(area)
        clip.h = max(clip.h, 4)  # フレームを隠すように
        pyxel.rect(area.x, area.y, area.w, clip.h, 0)  # タイトルの下地

        # テキストはセンタリングで常に表示
        x, y = menu_item_title.aligned_pos(ui_theme.font.system)
        pyxel.text(x, y-1, menu_item_title.text, 7, ui_theme.font.system.font)

    # メニューアイテム
    # ---------------------------------------------------------
    @field_select.item("menu_item")
    def menu_item(menu_item:select.Item, event:XUEvent):
        area = menu_item.area

        # ウインドウのクリップ状態に合わせて表示する
        if area.y < get_world_clip(XUWinBase.find_win(menu_item)).bottom():
            pyxel.text(area.x+6, area.y, menu_item.text, 7, ui_theme.font.system.font)

            # カーソル表示
            if menu_item.selected:
                draw_menu_cursor(menu_item, 0, 0)

    # コマンドメニュー
    # ---------------------------------------------------------
    @field_select.grid("menu_grid", "menu_item", "rows", "item_w", "item_h")
    def menu_grid(menu_grid:select.Grid, event:XUEvent):
        # メニュー選択
        input_def = ui_theme.input_def
        menu_grid.select_by_event(event.trg, *input_def.CURSOR)

        # 選択アイテムの表示
        if input_def.BTN_A in event.trg:
            match menu_grid.action:
                case "talk":
                    menu_grid.open(Field.UI_TEMPLATE_FIELD, "talk_dir")
                case "spel":
                    menu_grid.xmlui.popup("common", "under_construct")
                case "status":
                    menu_grid.xmlui.popup("common", "under_construct")
                case "tools":
                    menu_grid.xmlui.popup("common", "under_construct")
                case "step":
                    menu_grid.xmlui.popup("common", "under_construct")
                case "check":
                    menu_grid.xmlui.popup("common", "under_construct")
                case "door":
                    return "open_door"
                case "take":
                    menu_grid.xmlui.popup("common", "under_construct")

        # 閉じる
        if input_def.BTN_B in event.trg:
            XUWinBase.find_win(menu_grid).start_close()

    # メッセージウインドウ
    # ---------------------------------------------------------
    @field_text.msg_dq("msg_text")
    def msg_text(msg_text:text.MsgDQ, event:XUEvent):
        # テーマ情報取得
        system_font = ui_theme.font.system  # フォント
        input_def = ui_theme.input_def  # 入力イベント情報

        # テキスト表示
        # ---------------------------------------------------------
        msg_text.anim.draw_count += 0.5
        area = msg_text.area  # areaは重いので必ずキャッシュ

        # talkの時は各ページ先頭にマーク
        if msg_text.is_talk:
            for i,page in enumerate(msg_text.pages):
                msg_text.pages[i][0] = text.MsgDQ.TALK_MARK + page[0]

        # Scroll
        scroll_size = msg_text.page_line_num+2
        scroll_buf = msg_text.scroll_buf(scroll_size)
        if msg_text.page_text.startswith("＊「"):
            scroll_indents = msg_text.scroll_indents(scroll_size)
        else:
            scroll_indents = [False for _ in range(scroll_size)]

        # アニメーション用表示位置ずらし。スクロール時半文字ずれる
        y = -3 if not msg_text.anim.is_finish and len(scroll_buf) >= scroll_size else 5

        # テキスト描画
        line_height = system_font.size + 3  # 行間設定。見えない行間が見える人向けではない一般向け
        for i,page in enumerate(scroll_buf):
            x = area.x + (system_font.size*2 if scroll_indents[i] else 0)
            pyxel.text(x, y + area.y + i*line_height, page, 7, system_font.font)

        # カーソル表示
        # ---------------------------------------------------------
        if msg_text.is_next_wait:
            cursor_count = msg_text.anim.draw_count-msg_text.anim.length
            if cursor_count//7 % 2 == 0:
                draw_msg_cursor(msg_text, 0, len(scroll_buf)*line_height + y-3)

        # 入力アクション
        # ---------------------------------------------------------
        if input_def.BTN_A in event.trg or input_def.BTN_B in event.now:
            if msg_text.is_finish:
                XUWinBase.find_win(msg_text).start_close()
            elif msg_text.is_next_wait:
                msg_text.page_no += 1  # 次ページへ

        # 表示途中のアクション
        if not msg_text.is_next_wait:
            if input_def.BTN_A in event.now or input_def.BTN_B in event.now:
                msg_text.anim.draw_count += 2  # 素早く表示

        # 自分が閉じたらメニューごと閉じる
        if XUWinBase.find_win(msg_text).win_state == XUWinBase.STATE_CLOSED:
            XUWinBase(msg_text.xmlui.find_by_id("menu")).start_close()

    # ステータス各種アイテム
    # ---------------------------------------------------------
    @field_text.label("status_item")
    def status_item(status_item:text.Label, event:XUEvent):
        system_font = ui_theme.font.system

        # テキストは右寄せ
        x, y = status_item.aligned_pos(system_font, 5, 0)
        if y < get_world_clip(XUWinBase.find_win(status_item)).bottom():
            pyxel.text(x, y, status_item.text, 7, system_font.font)


    # 会話方向
    # ---------------------------------------------------------
    @field_select.list("dir_select", "dir_item", "item_w", "item_h")
    def dir_select(dir_select:select.List, event:XUEvent):
        # メニュー選択
        input_def = ui_theme.input_def
        # menu_grid.select_by_event(event.trg, *input_def.CURSOR)

        # 会話ウインドウは特別な配置
        if input_def.UP in event.trg:
            dir_select.select(0)
        if input_def.LEFT in event.trg:
            dir_select.select(1)
        if input_def.RIGHT in event.trg:
            dir_select.select(2)
        if input_def.DOWN in event.trg:
            dir_select.select(3)

        if input_def.BTN_A in event.trg:
            dir_win = XUWinBase.find_win(dir_select)
            dir_win.start_close()
            return f"start_talk_{dir_select.action}"

        # 閉じる
        if input_def.BTN_B in event.trg:
            XUWinBase.find_win(dir_select).start_close()

        # カーソル追加。ウインドウのクリップ状態に合わせて表示する
        if dir_select.selected_item.area.y < get_world_clip(XUWinBase.find_win(dir_select)).bottom():
            if event.is_active:
                draw_menu_cursor(dir_select.selected_item, -5, 0)

    # 会話方向アイテム
    # ---------------------------------------------------------
    @field_select.item("dir_item")
    def dir_item(dir_item:select.Item, event:XUEvent):
        area = dir_item.area

        # ウインドウのクリップ状態に合わせて表示する
        if area.y < get_world_clip(XUWinBase.find_win(dir_item)).bottom():
            pyxel.text(area.x, area.y, dir_item.text, 7, ui_theme.font.system.font)
