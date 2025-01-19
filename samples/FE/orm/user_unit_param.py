import dataclasses

from orm import db

@dataclasses.dataclass
class USER_UNIT_PARAM:
    unit_id:int
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
        data = dict(db.execute(sql).fetchone())

        self.unit_id = data["UNIT_ID"]
        self.unit_name = data["UNIT_NAME"]
        self.class_name = data["CLASS_NAME"]
        self.lv = data["LV"]
        self.hp = data["HP"]
        self.power = data["POWER"]
        self.skil = data["SKIL"]
        self.speed = data["SPEED"]
        self.defense = data["DEFENSE"]
        self.move = data["MOVE"]
