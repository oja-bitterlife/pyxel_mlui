import random
import pyxel

# タイトル画面
from xmlui.core import XMLUI,XUEvent,XUWinBase,XUSelectItem,XUTextUtil
from xmlui.lib import select,text
from xmlui_ext import dq
from ui_common import ui_theme
from params import param_db

battle_db = {
    "enemy": "なにか",
}

class Battle:
    UI_TEMPLATE_BATTLE = "ui_battle"

    # バトルの状態遷移
    ST_MSG_DRAWING = "msg_drawing"
    ST_CMD_WAIT = "command_wait"
    ST_ENEMY_TURN = "enemy_turn"
    state = ST_MSG_DRAWING

    def __init__(self, xmlui:XMLUI):
        self.xmlui = xmlui

        # UIの読み込み
        self.template = self.xmlui.load_template("assets/ui/battle.xml")
        ui_init(self.template)

        # バトル開始UI初期化
        self.battle = self.xmlui.open("battle")
        msg_dq = dq.MsgDQ(self.battle.find_by_id("msg_text"))
        msg_dq.append_msg("{enemy}が　あらわれた！", battle_db)

    def __del__(self):
        # 読みこんだUIの削除
        self.template.remove()

    def update(self):
        msg_dq = dq.MsgDQ(self.battle.find_by_id("msg_text"))
        match self.state:
            case Battle.ST_MSG_DRAWING:
                # メッセージ表示完了
                if msg_dq.is_all_finish:
                    # コマンド入力開始
                    msg_dq.append_msg("コマンド？")
                    self.battle.open("menu")
                    self.state = Battle.ST_CMD_WAIT

            case Battle.ST_CMD_WAIT:
                menu = dq.MsgDQ(self.battle.find_by_id("menu"))
                if "attack" in self.xmlui.event.trg:
                    battle_db["hit"] = XUTextUtil.format_zenkaku(random.randint(1, 100))
                    marge_db = param_db | battle_db

                    msg_dq.append_msg("{name}の　こうげき！", marge_db)
                    msg_dq.append_msg("{enemy}に　{hit}ポイントの\nダメージを　あたえた！", marge_db)
                    XUWinBase(menu).start_close()
                    self.state = Battle.ST_ENEMY_TURN

            case Battle.ST_ENEMY_TURN:
                battle_db["damage"] = XUTextUtil.format_zenkaku(random.randint(1, 10))
                marge_db = param_db | battle_db

                msg_dq.append_enemy("{enemy}の　こうげき！", marge_db)
                msg_dq.append_enemy("{name}は　{damage}ポイントの\nだめーじを　うけた", marge_db)
                self.state = Battle.ST_MSG_DRAWING


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
    battle_dq = dq.Decorator(template)

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
    def menu_item(menu_item:XUSelectItem):
        # ウインドウのクリップ状態に合わせて表示する
        if menu_item.area.y < get_world_clip(XUWinBase.find_parent_win(menu_item)).bottom():
            pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, 7, ui_theme.font.system.font)

            # カーソル表示
            if menu_item.selected and menu_item.enable:
                draw_menu_cursor(menu_item, 0, 0)

    # コマンドメニュー
    # ---------------------------------------------------------
    @battle_select.grid("menu_grid", "menu_item")
    def menu_grid(menu_grid:select.Grid, event:XUEvent):
        # 各アイテムの描画
        for item in menu_grid.items:
            menu_item(item)

        # メニュー選択
        input_def = ui_theme.input_def
        menu_grid.select_by_event(event.trg, *input_def.CURSOR)

        # 選択アイテムの表示
        if input_def.BTN_A in event.trg:
            return menu_grid.action


    @battle_dq.msg_dq("msg_text")
    def msg_text(msg_text:dq.MsgDQ, event:XUEvent):
        # メッセージ共通処理
        common_msg_text(msg_text, event, False)

        # メッセージウインドウの無効化(カーソル用)
        # msg_text.enable = False

        # メッセージウインドウがアクティブの時は自動テキスト送り
        if event.is_active and msg_text.is_next_wait:
            msg_text.next()

        if msg_text.is_all_finish:
            return "finish_msg"
