# DBはサンプルでは使わないので固定値で
import dataclasses
import sqlite3
from typing import Self

class XUXDB:
    @classmethod
    def memory(cls) -> "XUXDB":
        return XUXDB(":memory:")

    def __init__(self, db_path:str):
        with open(db_path, "rb") as f:
            db_data = f.read()
            self.conn = sqlite3.connect(":memory:")
            self.conn.deserialize(db_data)

    def __del__(self):
        self.conn.close()

    def prepare(self, sql:str) -> Self:
        self.sql = sql
        self.params = []
        return self

    def bind(self, **params) -> Self:
        self.params = params
        return self

    def execute(self):
        cur = self.conn.cursor()
        try:
            if self.params:
                cur.execute(self.sql, *self.params)
            else:
                cur.conn.execute(self.sql)
        except:
            pass
            # cur.rollback()
        data = cur.fetchall()
        cur.close()
        return data

class SystemInfoTable:
    def __init__(self):
        self.msg_spd = 1.0
system_info = SystemInfoTable()

class UserDataTable:
    def __init__(self):
        self.name = "おじゃ　"
        self.lv = 1
        self.hp = 12
        self.mp = 123
        self.gold = 1234
        self.exp = 12345
        self.rem_exp = 10
user_data = UserDataTable()

class EnemyDataTable:
    def __init__(self):
        self.name = "ヌライム"
        self.hp = 12
        self.atk = 1
        self.gold = 1
        self.exp = 1
enemy_data = UserDataTable()

@dataclasses.dataclass
class NPCData:
    name: str
    x: int
    y: int
    anim_pat: list[int]
    talk: str
npc_data = [
    NPCData("king", 8, 8, [16, 17], "{name}が　つぎのれべるになるには\nあと　{rem_exp}ポイントの\nけいけんが　ひつようじゃ\\pでは　また　あおう！\nゆうしゃ　{name}よ！"),
    NPCData("knight1", 8, 11, [0, 1], "とびらのまえで　とびら　をせんたくしてね"),
    NPCData("knight2", 10, 11, [0, 1], "とびらのさきに　かいだんがある"),
    NPCData("knighg3", 12, 9, [0, 1], "たからばこ？\nとっちゃだめだだよ？"),
]

@dataclasses.dataclass
class FieldObjData:
    name: str
    x: int
    y: int
    anim_pat: int
    movable: bool
    visible: bool
    talk: str
field_obj_data = [
    FieldObjData("tresure1", 9, 9, 4, True, True, "やくそう"),
    FieldObjData("tresure2", 10, 9, 4, True, True, "100G"),
    FieldObjData("tresure3", 11, 6, 4, True, True, "10G"),
    FieldObjData("door", 9, 12, 36, False, True, ""),
]


