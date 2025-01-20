from xmlui.ext.db import XUECSVDict
from orm.user_unit_state import USER_UNIT_STATE

class UNIT(USER_UNIT_STATE):
    def __init__(self, unit_name:str):
        super().__init__(unit_name)

class UNITS:
    # ステージごとに初期化する
    def __init__(self, stage_no:int):
        unit_map_place = XUECSVDict(f"assets/stage/stage{stage_no}_units.csv")

        # ユニット読み込みと配置
        self.units:dict[str,USER_UNIT_STATE] = {}
        for row in unit_map_place.rows:
            unit = USER_UNIT_STATE(row["UNIT_NAME"])  # 読み込み
            unit.reset(int(row["MAP_X"]), int(row["MAP_Y"]))  # 配置
            self.units[row["UNIT_NAME"]] = unit
