import pyxel

from xmlui.core import XUElem,XUEvent,XUWinBase,XURect
from xmlui.lib import select,debug

from system import system_font,hand_cursor
from ui_common import get_world_clip

from battle.data import BattleData
from battle.act import *


def ui_init(xmlui:debug.DebugXMLUI[BattleData]):
    action_select = select.Decorator(xmlui)

    # 各キャラのアクション表示
    # *************************************************************************
    def battle_action(battle_action:XUElem, clip:XURect):
        area = battle_action.area

        # ウインドウが表示されてる場所のみ描画
        if clip.bottom() < area.y:
            return

        # コマンドの表示
        pyxel.text(area.x, area.y, battle_action.text, 7, system_font.font)

        # コマンド選択中はHandIconを表示
        if xmlui.data_ref.scene.current_act == BattleCmdSel:
            if battle_action.selected:
                hand_cursor.draw(area.x, area.y+4)

    @action_select.list("command", "battle_action")
    def command(command:select.List, event:XUEvent):
        clip = get_world_clip(XUWinBase.find_parent_win(command))
        for item in command.items:
            battle_action(item, clip)

        command.select_by_event(event.repeat, *XUEvent.Key.UP_DOWN())
