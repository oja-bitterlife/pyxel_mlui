import dataclasses

from orm import db

# 現在の状態(書き換え可)
@dataclasses.dataclass
class USER_UNIT_STATE:
    unit_id:int
    map_x:int
    map_y:int
    now_hp:int
    class_name:str
    lv:int
    hp:int
    power:int
    skil:int
    speed:int
    defense:int
    move:int
    exp:int
    moved:bool
    dead:bool

    def __init__(self, unit_name:str):
        sql = f"""
            SELECT * FROM user_unit_state
                WHERE UNIT_ID=(SELECT UNIT_ID FROM data_unit_init WHERE UNIT_NAME=?)

        """
        data = dict(db.execute(sql, (unit_name,)).fetchone())

        self.unit_id = data["UNIT_ID"]
        self.map_x = data["MAP_X"]
        self.map_y = data["MAP_Y"]
        self.now_hp = data["NOW_HP"]
        self.class_name = data["CLASS_NAME"]
        self.lv = data["LV"]
        self.hp = data["HP"]
        self.power = data["POWER"]
        self.skil = data["SKIL"]
        self.speed = data["SPEED"]
        self.defense = data["DEFENSE"]
        self.move = data["MOVE"]
        self.exp = data["EXP"]
        self.moved = data["MOVED"]
        self.dead = data["DEAD"]

    def set_hp(self, hp:int):
        self.now_hp = hp
        sql = f"""
            UPDATE user_unit_state SET NOW_HP=? WHERE UNIT_ID=?
        """
        db.execute(sql, (hp, self.unit_id))

    @classmethod
    def reset(cls, unit_name:str, map_x:int, map_y:int):
        sql = f"""
            SELECT COUNT(*) FROM user_unit_state
                WHERE UNIT_ID=(SELECT UNIT_ID FROM data_unit_init WHERE UNIT_NAME=?)
        """
        row = db.execute(sql, (unit_name,)).fetchone()
        if row[0] == 0:
            sql = f"""
                INSERT INTO user_unit_state (UNIT_ID,MAP_X,MAP_Y,NOW_HP,CLASS_NAME,LV,HP,POWER,SKIL,SPEED,DEFENSE,MOVE,EXP) 
                    SELECT UNIT_ID,?,?,HP,CLASS_NAME,LV,HP,POWER,SKIL,SPEED,DEFENSE,MOVE,EXP FROM data_unit_init
                        WHERE UNIT_ID=(SELECT UNIT_ID FROM data_unit_init WHERE UNIT_NAME=?)
            """
            db.execute(sql, (map_x, map_y, unit_name))
        # else:
        #     db.execute(f"UPDATE user_unit_state SET MAP_X=?, MAP_Y=?, MOVED=0 WHERE UNIT_ID='{param.unit_id}'", (map_x, map_y))
