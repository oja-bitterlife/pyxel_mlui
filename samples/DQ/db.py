# DBはサンプルでは使わないので固定値で
import dataclasses

from xmlui.ext.db import XUXMemoryDB

game_db = XUXMemoryDB.load("assets/data/game.db")
user_db = XUXMemoryDB.load("assets/data/user.db")


# システムデータ
# *****************************************************************************
# システムインフォ。コンフィグがメイン
class SystemInfoTable:
    def __init__(self):
        self.msg_spd = 1.0
system_info = SystemInfoTable()


# ユーザーデータ
# *****************************************************************************
# セーブデータ。といいつつサンプルではセーブしないので適当で
class UserSave:
    def __init__(self):
        self.name = "おじゃ　"
        self.level = 1

        # 初期HPはmaxを設定
        level_data = dict(game_db.execute("SELECT * from level_data where level=?", [self.level]).fetchone())
        self.hp = level_data["max_hp"]
        self.mp = level_data["max_mp"]
user_save = UserSave()

# ユーザーステータスデータアクセス
class UserData:
    def reload_db(self):
        user_data = dict(user_db.execute("SELECT * from user_data").fetchone())
        level_data = dict(game_db.execute("SELECT * from level_data where level=?", [user_data["level"]]).fetchone())
        self.data = user_data | level_data

        # 残り経験値
        self.data["rem_exp"] = self.data["need_exp"] - self.data["exp"]

    def __init__(self):
        # セーブデータからの復帰
        user_db.execute("UPDATE user_data SET name=?,level=?,hp=?,mp=?", [user_save.name, user_save.level, user_save.hp, user_save.mp])
        self.reload_db()

    @property
    def hp(self):
        return self.data["hp"]
    @hp.setter
    def hp(self, value):
        user_db.execute("UPDATE user_data SET hp=?", [value])
        user_db.connection.commit()
        self.reload_db()

    @property
    def mp(self):
        return self.data["mp"]
    @mp.setter
    def mp(self, value):
        user_db.execute("UPDATE user_data SET mp=?", [value])
        user_db.connection.commit()
        self.reload_db()

    def set_level(self, level):
        user_db.execute("UPDATE user_data SET level=?", [level])
        user_db.connection.commit()
        self.reload_db()

user_data = UserData()


# エネミーデータ
# *****************************************************************************
class EnemyData:
    def reload(self):
        self.data = dict(game_db.execute("SELECT * from enemy_data where id=?", [self.id]).fetchone())

    def __init__(self, id:int) -> None:
        self.id = id
        self.reload()

enemy_data = EnemyData(1)


# NPCデータ
# *****************************************************************************
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


