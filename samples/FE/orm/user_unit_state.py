import dataclasses

from orm import db
from orm.user_unit_stocks import UserUnitStocks

# 現在の状態(書き換え可)
@dataclasses.dataclass
class UserUnitState:
    unit_id:int
    unit_name:str
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
        self.unit_name = unit_name

        # 現在のデータ取得
        sql = f"""
            SELECT * FROM user_unit_state
                WHERE UNIT_ID=(SELECT UNIT_ID FROM data_unit_init WHERE UNIT_NAME=?)

        """
        data = db.execute(sql, (unit_name,)).fetchone()
        # データが無ければ初期データを引っ張ってきておく
        if data is None:
            self.initialize(unit_name)
            data = db.execute(sql, (unit_name, )).fetchone()

        # 取得したデータを設定
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

    # DBに状態を保存する
    def save(self):
        sql = f"""
            UPDATE user_unit_state
                SET MAP_X=?, MAP_Y=?, NOW_HP=?, CLASS_NAME=?, LV=?,
                    HP=?, POWER=?, SKIL=?, SPEED=?, DEFENSE=?, MOVE=?,
                    EXP=?, MOVED=?, DEAD=?
                WHERE UNIT_ID=?
        """
        db.execute(sql, (self.map_x, self.map_y, self.now_hp, self.class_name, self.lv,
            self.hp, self.power, self.skil, self.speed, self.defense, self.move,
            self.exp, self.moved, self.dead,
            self.unit_id
        ))

    # マップ開始時のリセット
    def reset(self, map_x:int, map_y:int):
        self.now_hp = self.hp
        self.map_x = map_x
        self.map_y = map_y
        self.save()

    @classmethod
    def initialize(cls, unit_name:str):
        # 各パラメータをstate側に移す
        sql = f"""
            INSERT INTO user_unit_state (UNIT_ID,MAP_X,MAP_Y,NOW_HP,CLASS_NAME,LV,HP,POWER,SKIL,SPEED,DEFENSE,MOVE,EXP) 
                SELECT UNIT_ID,0,0,HP,CLASS_NAME,LV,HP,POWER,SKIL,SPEED,DEFENSE,MOVE,EXP FROM data_unit_init
                    WHERE UNIT_ID=(SELECT UNIT_ID FROM data_unit_init WHERE UNIT_NAME=?)
        """
        db.execute(sql, (unit_name,))

        # アイテムも保存しておく
        sql = f"""
            SELECT UNIT_ID,ITEM1,ITEM2,ITEM3 FROM data_unit_init WHERE UNIT_NAME=?
        """
        row = db.execute(sql, (unit_name,)).fetchone()
        if row is not None:
            if row["ITEM1"] is not None:
                UserUnitStocks.append(row["UNIT_ID"], row["ITEM1"], True)
            if row["ITEM2"] is not None:
                UserUnitStocks.append(row["UNIT_ID"], row["ITEM2"])
            if row["ITEM3"] is not None:
                UserUnitStocks.append(row["UNIT_ID"], row["ITEM2"])
