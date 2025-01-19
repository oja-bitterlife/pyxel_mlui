import dataclasses

from orm import db
from orm.user_unit_param import USER_UNIT_PARAM

# 現在の状態(書き換え可)
@dataclasses.dataclass
class USER_UNIT_STATE(USER_UNIT_PARAM):
    map_x:int
    map_y:int
    now_hp:int
    now_exp:int
    moved:bool
    dead:bool

    def __init__(self, unit_name:str):
        super().__init__(unit_name)

        sql = f"""
            SELECT * FROM user_unit_state WHERE UNIT_ID='{self.unit_id}'
        """
        data = dict(db.execute(sql).fetchone())

        self.map_x = data["MAP_X"]
        self.map_y = data["MAP_Y"]
        self.now_hp = data["NOW_HP"]
        self.now_exp = data["NOW_EXP"]
        self.moved = data["MOVED"]
        self.dead = data["MOVED"]

    def set_hp(self, hp:int):
        self.now_hp = hp
        sql = f"""
            UPDATE user_unit_state SET NOW_HP=? WHERE UNIT_NAME='{self.unit_name}'
        """
        db.execute(sql, (hp,))

    @classmethod
    def reset(cls, unit_name:str, map_x:int, map_y:int):
        param = USER_UNIT_PARAM(unit_name)
        row = db.execute(f"SELECT COUNT(*) FROM user_unit_state WHERE UNIT_ID='{param.unit_id}'").fetchone()
        if row[0] == 0:
            db.execute("INSERT INTO user_unit_state (UNIT_ID, MAP_X, MAP_Y, NOW_HP) VALUES (?, ?, ?, ?)", (param.unit_id, map_x, map_y, param.hp))
        else:
            db.execute(f"UPDATE user_unit_state SET MAP_X=?, MAP_Y=?, MOVED=0 WHERE UNIT_ID='{param.unit_id}'", (map_x, map_y))
