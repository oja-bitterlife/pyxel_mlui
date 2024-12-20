from enum import StrEnum

from xmlui.core import XMLUI
from xmlui.ext.tilemap import XUXTilemap
import db

class NPC:
    def __init__(self, data:db.NPCData):
        self.data = data
        self.tile = XUXTilemap(1)

    def draw(self, offset_x:int, offset_y:int):
        self.tile.update()
        self.tile.draw(self.data.x*16 + offset_x, self.data.y*16 + offset_y, self.data.anim_pat)

class NPCManager:
    class TALK_EVENT(StrEnum):
        EAST = "start_talk_east"
        WEST = "start_talk_west"
        SOUTH = "start_talk_south"
        NORTH = "start_talk_north"
    # 全方向定義
    TALK_EVENTS = [TALK_EVENT.EAST, TALK_EVENT.WEST, TALK_EVENT.SOUTH, TALK_EVENT.NORTH]

    def __init__(self):
        self.npcs = [NPC(data) for data in db.npc_data]

    def draw(self, scroll_x:int, scroll_y:int):
        for npc in self.npcs:
            npc.draw(scroll_x-1, scroll_y-1)

    # ぶつかりチェック
    def hit_check(self, block_x:int, block_y:int):
        for npc in self.npcs:
            if npc.data.x == block_x and npc.data.y == block_y:
                return True
        return False

    # 会話チェック
    def _talk_check(self, block_x:int, block_y:int) -> str|None:
        for npc in self.npcs:
            if npc.data.x == block_x and npc.data.y == block_y:
                return npc.data.talk
        return None

    # 会話イベントチェック
    def check_talk(self, talk_event:TALK_EVENT, block_x:int, block_y:int) -> str | None:
        match talk_event:
            case self.TALK_EVENT.EAST:
                return self._talk_check(block_x+1, block_y)
            case self.TALK_EVENT.WEST:
                return self._talk_check(block_x-1, block_y)
            case self.TALK_EVENT.SOUTH:
                return self._talk_check(block_x, block_y+1)
            case self.TALK_EVENT.NORTH:
                return self._talk_check(block_x, block_y-1)
