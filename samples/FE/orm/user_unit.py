from typing import Any

from orm import db
import dataclasses

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
class USER_UNIT_STATE:
    param:USER_UNIT_PARAM  # paramへのアクセスもできるようにしておく

    map_x:int
    map_y:int
    now_hp:int
    now_exp:int

    def __init__(self, param:USER_UNIT_PARAM):
        self.param = param

        sql = f"""
            SELECT * FROM user_unit_state WHERE UNIT_NAME='{param.unit_name}'
        """
        data = dict(db.cursor.execute(sql).fetchone())

        self.map_x=data["MAP_X"]
        self.map_y=data["MAP_Y"]
        self.now_hp=data["NOW_HP"]
        self.now_exp=data["NOW_EXP"]

class USER_UNITS:
    @classmethod
    def load_param(cls, unit_name:str) -> USER_UNIT_PARAM:
        return USER_UNIT_PARAM(unit_name)

    @classmethod
    def load_state(cls, unit_name:str) -> USER_UNIT_STATE:
        param = cls.load_param(unit_name)
        return USER_UNIT_STATE(param)

    @classmethod
    def get_unit_names(cls):
        sql = f"""
            SELECT UNIT_NAME FROM user_unit_params
        """
        return [row[0] for row in db.cursor.execute(sql).fetchall()]
