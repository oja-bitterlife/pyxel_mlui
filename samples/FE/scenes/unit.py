import pyxel

from xmlui.core import XURect
from xmlui.ext.db import XUECSVDict
from orm.user_unit_state import UserUnitState

class Unit(UserUnitState):
    def __init__(self, unit_name:str):
        super().__init__(unit_name)

    def draw(self, screen:XURect):
        rect = XURect(self.map_x*16, self.map_y*16, 16, 16)
        if not screen.intersect(rect).is_empty:
            pyxel.blt(rect.x, rect.y, 0, 0, 0, 16, 16, 0)


class Units:
    # ステージごとに初期化する
    def __init__(self, stage_no:int):
        unit_map_place = XUECSVDict(f"assets/stage/stage{stage_no}_units.csv")

        # ユニット読み込みと配置
        self.units:dict[str,Unit] = {}
        for row in unit_map_place.rows:
            unit = Unit(row["UNIT_NAME"])  # 読み込み
            unit.reset(int(row["MAP_X"]), int(row["MAP_Y"]))  # 配置
            self.units[row["UNIT_NAME"]] = unit
