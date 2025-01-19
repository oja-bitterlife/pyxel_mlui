import dataclasses

from orm import db

# 現在の状態(書き換え可)
@dataclasses.dataclass
class USER_ENEMY_STATE:
    enemy_id:int
    enemy_name:str
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

    def __init__(self, enemy_id:int):
        self.enemy_id = enemy_id

        # 現在のデータ取得
        sql = f"""
            SELECT * FROM user_enemy_state WHERE ENEMY_ID=?
        """
        data = db.execute(sql, (enemy_id,)).fetchone()
        # データが無ければ初期データを引っ張ってきておく
        if data is None:
            self.initialize(enemy_id)
            data = db.execute(sql, (enemy_id,)).fetchone()

        # 取得したデータを設定
        self.unit_id = data["ENEMY_ID"]
        self.enemy_name = data["ENEMY_NAME"]
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
            UPDATE user_enemy_state
                SET MAP_X=?, MAP_Y=?, NOW_HP=?, MOVED=?, DEAD=? WHERE ENEMY_ID=?
        """
        db.execute(sql, (self.map_x, self.map_y, self.now_hp, self.moved, self.dead, self.unit_id))

    @classmethod
    def initialize(cls, enemy_id:int):
        # 各パラメータをstate側に移す
        sql = f"""
            INSERT INTO user_enemy_state (ENEMY_ID,ENEMY_NAME,MAP_X,MAP_Y,NOW_HP,CLASS_NAME,LV,HP,POWER,SKIL,SPEED,DEFENSE,MOVE,EXP) 
                SELECT ENEMY_ID,ENEMY_NAME,MAP_X,MAP_Y,HP,CLASS_NAME,LV,HP,POWER,SKIL,SPEED,DEFENSE,MOVE,EXP FROM data_enemy_init
                    WHERE ENEMY_ID=?
        """
        db.execute(sql, (enemy_id,))

        # アイテムも保存しておく
        # sql = f"""
        #     SELECT ENEMY_ID,ITEM1,ITEM2,ITEM3 FROM data_unit_init WHERE UNIT_NAME=?
        # """
        # row = db.execute(sql, (unit_name,)).fetchone()
        # if row is not None:
        #     if row["ITEM1"] is not None:
        #         USER_UNIT_STOCKS.append(row["ENEMY_ID"], row["ITEM1"], True)
        #     if row["ITEM2"] is not None:
        #         USER_UNIT_STOCKS.append(row["ENEMY_ID"], row["ITEM2"])
        #     if row["ITEM3"] is not None:
        #         USER_UNIT_STOCKS.append(row["ENEMY_ID"], row["ITEM2"])
