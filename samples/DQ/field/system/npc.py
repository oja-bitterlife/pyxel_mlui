import dataclasses
from enum import StrEnum

from xmlui.core import XMLUI
from xmlui.ext.tilemap import XUXTilemap

@dataclasses.dataclass
class NPC_Data:
    name: str
    x: int
    y: int
    anim_pat: list[int]
    talk: str

    def setup(self):
        self.tile = XUXTilemap(1)

    def draw(self, offset_x:int, offset_y:int):
        self.tile.update()
        self.tile.draw(self.x*16 + offset_x, self.y*16 + offset_y, self.anim_pat)

class NPC:
    class TALK_EVENT(StrEnum):
        EAST = "start_talk_east"
        WEST = "start_talk_west"
        SOUTH = "start_talk_south"
        NORTH = "start_talk_north"
    # 全方向定義
    TALK_EVENTS = [TALK_EVENT.EAST, TALK_EVENT.WEST, TALK_EVENT.SOUTH, TALK_EVENT.NORTH]

    npc_data = [
        # typ,   x, y, color, talk
        NPC_Data("king", 8, 8, [8, 9], "{name}が　つぎのれべるになるには\nあと　{rem_exp}ポイントの\nけいけんが　ひつようじゃ\\pでは　また　あおう！\nゆうしゃ　{name}よ！"),
        NPC_Data("knight1", 8, 11, [0, 1], "とびらのまえで　とびら　をせんたくしてね"),
        NPC_Data("knight2", 10, 11, [0, 1], "とびらのさきに　かいだんがある"),
        NPC_Data("knighg3", 12, 9, [0, 1], "たからばこ？\nとっちゃだめだだよ？"),
    ]
    def __init__(self):
        for npc in self.npc_data:
            npc.setup()

    def draw(self, scroll_x, scroll_y):
        for npc in self.npc_data:
            npc.draw(scroll_x-1, scroll_y-1)

    # 会話チェック
    def _check(self, block_x, block_y) -> str|None:
        for data in self.npc_data:
            if data.x == block_x and data.y == block_y:
                return data.talk
        return None


    # 会話イベントチェック
    def check_talk(self, talk_event:TALK_EVENT, block_x, block_y) -> str | None:
        match talk_event:
            case self.TALK_EVENT.EAST:
                return self._check(block_x+1, block_y)
            case self.TALK_EVENT.WEST:
                return self._check(block_x-1, block_y)
            case self.TALK_EVENT.SOUTH:
                return self._check(block_x, block_y+1)
            case self.TALK_EVENT.NORTH:
                return self._check(block_x, block_y-1)
