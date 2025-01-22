import pyxel

from xmlui.core import XURect
from xmlui.ext.db import XUECSVDict
from orm.user_unit_state import UserUnitState

class Unit(UserUnitState):
    IMAGE_BANK = 1

    def __init__(self, unit_name:str):
        super().__init__(unit_name)
        self.img_u = 0
        self.img_v = 0

    def draw(self, screen_x:int, screen_y:int):
        rect = XURect(self.map_x*16 - screen_x, self.map_x*16 - screen_x, 16, 16)
        if not rect.intersect(XURect(0, 0, 256, 256)).is_empty:
            pyxel.blt(rect.x, rect.y, self.IMAGE_BANK, self.img_u, self.img_v, 16, 16, 0)

class Units:
    # ステージごとに初期化する
    def __init__(self, stage_no:int):
        unit_map_place = XUECSVDict(f"assets/stage/units-{stage_no}.csv")

        # ユニット読み込みと配置
        self.units:dict[str,Unit] = {}
        for row in unit_map_place.rows:
            unit = Unit(row["UNIT_NAME"])  # 読み込み
            unit.reset(int(row["MAP_X"]), int(row["MAP_Y"]))  # 配置
            self.units[row["UNIT_NAME"]] = unit

    def load_image(self):
        pass

    def draw(self, screen_x:int, screen_y:int):
        for unit in self.units.values():
            unit.draw(screen_x, screen_y)
