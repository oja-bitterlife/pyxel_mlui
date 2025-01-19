import dataclasses

from orm import db
#from orm.user_enemy_param import USER_ENEMY_PARAM

# 現在の状態(書き換え可)
@dataclasses.dataclass
class USER_ENEMY_STATE():
    map_x:int
    map_y:int
    now_hp:int
    moved:bool

    def __init__(self, unit_name:str):
        # super().__init__(unit_name)

        sql = f"""
            SELECT * FROM user_unit_state WHERE UNIT_NAME='{unit_name}'
        """
        data = dict(db.execute(sql).fetchone())

        self.map_x=data["MAP_X"]
        self.map_y=data["MAP_Y"]
        self.now_hp=data["NOW_HP"]
        self.moved=data["MOVED"]

    def set_hp(self, hp:int):
        self.now_hp = hp
        # sql = f"""
        #     UPDATE user_unit_state SET NOW_HP=? WHERE UNIT_NAME='{self.unit_name}'
        # """
        # db.execute(sql, (hp,))

    @classmethod
    def reset(cls, unit_name:str, map_x:int, map_y:int):
        # param = USER_ENEMY_PARAM(unit_name)
        # row = db.execute("SELECT COUNT(*) FROM user_unit_state WHERE UNIT_NAME='{unit_name}'").fetchone()
        # if row is None:
        #     db.execute("INSERT INTO user_unit_state SET MAP_X=?, MAP_Y=?, NOW_HP=? WHERE UNIT_NAME='{unit_name}'", (map_x, map_y, param.hp))
        # else:
            db.execute("UPDATE user_unit_state SET MAP_X=?, MAP_Y=?, MOVED=0 WHERE UNIT_NAME='{unit_name}'", (map_x, map_y))