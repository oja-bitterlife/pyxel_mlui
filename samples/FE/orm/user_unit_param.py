import dataclasses

from orm import db

@dataclasses.dataclass
class USER_UNIT_PARAM:
    unit_name:str
    class_name:str
    lv:int
    hp:int
    power:int
    skil:int
    speed:int
    defense:int
    move:int

    def __init__(self, unit_name:str):
        sql = f"""
            SELECT * FROM user_unit_params WHERE UNIT_NAME='{unit_name}'
        """
        data = dict(db.cursor.execute(sql).fetchone())

        self.unit_name=unit_name
        self.class_name=data["CLASS_NAME"]
        self.lv=data["LV"]
        self.hp=data["HP"]
        self.power=data["POWER"]
        self.skil=data["SKIL"]
        self.speed=data["SPEED"]
        self.defense=data["DEFENSE"]
        self.move=data["MOVE"]


# 現在の状態(書き換え可)
@dataclasses.dataclass
class USER_UNIT_STATE(USER_UNIT_PARAM):
    map_x:int
    map_y:int
    now_hp:int
    now_exp:int

    def __init__(self, unit_name:str):
        super().__init__(unit_name)

        sql = f"""
            SELECT * FROM user_unit_state WHERE UNIT_NAME='{unit_name}'
        """
        data = dict(db.cursor.execute(sql).fetchone())

        self.map_x=data["MAP_X"]
        self.map_y=data["MAP_Y"]
        self.now_hp=data["NOW_HP"]
        self.now_exp=data["NOW_EXP"]

    def set_hp(self, hp:int):
        self.now_hp = hp
        sql = f"""
            UPDATE user_unit_state SET NOW_HP={hp} WHERE UNIT_NAME='{self.unit_name}'
        """
        db.cursor.execute(sql)

    def reset_hp(self):
        self.set_hp(self.hp)
