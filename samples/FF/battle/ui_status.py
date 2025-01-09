import pyxel

from xmlui.core import XUElem,XUEvent,XUTextUtil,XURect,XUWinBase
from xmlui.lib import text,debug
from system import system_font

from ui_common import get_world_clip
from db import user_data,enemy_data
from battle.data import BattleData

def ui_init(xmlui:debug.DebugXMLUI[BattleData]):
    status_text = text.Decorator(xmlui)

    # なぜかぽつんと一つあるHPラベル
    @status_text.label("hp_Label")
    def hp_Label(hp_Label:text.Label, event:XUEvent):
        pyxel.text(hp_Label.area.x, hp_Label.area.y, hp_Label.text, 7, system_font.font)


    # 各キャラのステータス表示
    # *************************************************************************
    # キャラ1人分
    def status_one(area:XURect, no:int, player_data:dict, clip:XURect):
        if clip.bottom < area.y+system_font.size:
            return

        pyxel.text(area.x, area.y, player_data["name"], 7, system_font.font)

        hp_text = XUTextUtil.format_zenkaku("{hp}／", player_data)
        hp_area = XURect(area.x+64, area.y, system_font.size*4, system_font.size)
        hp_x, hp_y = hp_area.aligned_pos(system_font.text_width(hp_text), 0, XURect.Align.RIGHT, XURect.Align.TOP)
        pyxel.text(hp_x, hp_y, hp_text, 7, system_font.font)

        # HPの右側は最大HPか、コマンド選択中ならコマンド
        hpmax_area = XURect(area.x+82+16, area.y, system_font.size*4, system_font.size)
        if xmlui.exists_id("command") and no < xmlui.data_ref.player_idx:
            right_text = xmlui.data_ref.command[no]
        else:
            right_text = XUTextUtil.format_zenkaku("{max_hp}", player_data)
        hpmax_x, hpmax_y = hpmax_area.aligned_pos(system_font.text_width(right_text), 0, XURect.Align.RIGHT, XURect.Align.TOP)
        pyxel.text(hpmax_x, hp_y, right_text, 7, system_font.font)

    # キャラ全員ステータス
    # -----------------------------------------------------
    @xmlui.tag_draw("status")
    def status(status:XUElem, event:XUEvent):
        area = status.area
        clip = get_world_clip(XUWinBase.find_parent_win(status))

        # ステータス各行のサイズ
        status_line_size = 16
        area.h = status_line_size

        # 一人ずつ表示
        for i,player_data in enumerate(user_data.player_data):
            status_one(area, i, player_data, clip)
            area.y += status_line_size

    # 敵の名前表示
    @xmlui.tag_draw("enemy_names")
    def enemy_names(enemy_names:XUElem, event:XUEvent):
        area = enemy_names.area
        clip = get_world_clip(XUWinBase.find_parent_win(enemy_names))

        # 各行のサイズ
        status_line_size = 16
        area.h = status_line_size

        enemy_kinds = set([data["name"] for data in enemy_data.data])

        # 種類ずつ表示
        for enemy_kind in enemy_kinds:
            if clip.bottom > area.y+status_line_size:
                pyxel.text(area.x, area.y, enemy_kind, 7, system_font.font)
            area.y += status_line_size
