import pyxel

from xmlui.core import XUEvent,XUWinBase,XUSelectItem
from xmlui.lib import select,text

from DQ import msg_dq
from DQ.msg_dq import MsgDQ

from DQ.system import system_font
from DQ.ui_common import KOJICHU_COL,get_text_color


# バトルUI
# *****************************************************************************
from ui_common import get_world_clip, draw_menu_cursor

def ui_init(template):
    # fieldグループ用デコレータを作る
    battle_select = select.Decorator(template)
    battle_text = text.Decorator(template)
    battle_dq = msg_dq.Decorator(template)

    # コマンドメニューのタイトル
    @battle_text.label("title")
    def title(title:text.Label, event:XUEvent):
        clip = get_world_clip(XUWinBase.find_parent_win(title)).intersect(title.area)
        pyxel.rect(title.area.x, title.area.y, title.area.w, clip.h, 0)  # タイトルの下地

        col = get_text_color()

        # テキストはセンタリング
        if title.area.y < clip.bottom():  # world座標で比較
            x, y = title.aligned_pos(system_font)
            pyxel.text(x, y-1, title.text, col, system_font.font)

    # メニューアイテム
    # ---------------------------------------------------------
    def menu_item(menu_item:XUSelectItem):
        # ウインドウのクリップ状態に合わせて表示する
        if menu_item.area.y < get_world_clip(XUWinBase.find_parent_win(menu_item)).bottom():
            col = KOJICHU_COL if menu_item.value == "工事中" else get_text_color()
            pyxel.text(menu_item.area.x+6, menu_item.area.y, menu_item.text, col, system_font.font)

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
        menu_grid.select_by_event(event.trg, *XUEvent.Key.CURSOR())

        # 選択アイテムの表示
        if event.check(XUEvent.Key.BTN_A):
            return menu_grid.action


    @battle_dq.msg_dq("msg_text")
    def msg_text(msg_text:MsgDQ, event:XUEvent):
        # メッセージ共通処理
        msg_text.draw(event, False)

        # 自動テキスト送り
        if msg_text.is_next_wait:
            msg_text.next_page()

        if msg_text.is_all_finish:
            return "finish_msg"
