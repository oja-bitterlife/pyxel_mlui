import pyxel

from xmlui.core import XMLUI,XUElem,XUEvent,XUSelectItem,XUWinBase,XUTextUtil,XURect
from xmlui.lib import select,text
from system import system_font, hand_cursor

from db import user_data

def ui_init(xmlui:XMLUI):
    status_select = select.Decorator(xmlui)
    status_text = text.Decorator(xmlui)


    # なぜかぽつんと一つあるHPラベル
    @status_text.label("hp_Label")
    def hp_Label(hp_Label:text.Label, event:XUEvent):
        pyxel.text(hp_Label.area.x, hp_Label.area.y, hp_Label.text, 7, system_font.font)


    # 各キャラのステータス表示
    # *************************************************************************
    # キャラ1人分
    def status_one(area:XURect, player_data:dict):
        pyxel.text(area.x, area.y, player_data["name"], 7, system_font.font)

        hp_text = XUTextUtil.format_zenkaku("{hp}／", player_data)
        hp_area = XURect(area.x+82, area.y, system_font.size*4//2, system_font.size)
        hp_x, hp_y = hp_area.aligned_pos(system_font.text_width(hp_text), 0, XURect.Align.RIGHT, XURect.Align.TOP)
        pyxel.text(hp_x, hp_y, hp_text, 7, system_font.font)

        max_hp_text = XUTextUtil.format_zenkaku("{max_hp}", player_data)
        pyxel.text(hp_x+32, hp_y, max_hp_text, 7, system_font.font)

    # キャラ全員ステータス
    # -----------------------------------------------------
    @xmlui.tag_draw("status")
    def status(status:XUElem, event:XUEvent):
        area = status.area

        # ステータス各行のサイズ
        status_line_size = 16
        area.h = status_line_size

        # 一人ずつ表示
        for player_data in user_data.player_data:
            status_one(area, player_data)
            area.y += status_line_size
