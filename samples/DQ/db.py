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

    def __init__(self, id:int):
        self.id = id
        self.reload()

enemy_data = EnemyData(1)


# NPCデータ
# *****************************************************************************
class NPCData:
    def reload(self):
        sql = """SELECT * from npc_place
                    INNER JOIN npc_data ON npc_place.npc_id = npc_data.id
                    INNER JOIN npc_graph ON npc_data.graph_id = npc_graph.id
                    where field_id=?"""
        self.data = [dict(row) for row in game_db.execute(sql, [self.field_id]).fetchall()]

        for data in self.data:
            data["anim_pat"] = list(map(int, data["anim_pat"].split(",")))
            data["talk"] = data["talk"].replace("\r\n", "\n")

    def __init__(self, field_id:int):
        self.field_id = field_id
        self.reload()

npc_data = NPCData(1)


# フィールドオブジェクトデータ
# *****************************************************************************
class FieldObjData:
    def reload(self):
        sql = """SELECT * from fieldobj_place
                    INNER JOIN fieldobj_data ON fieldobj_place.fieldobj_id = fieldobj_data.id
                    where field_id=?"""
        self.data = [dict(row) for row in game_db.execute(sql, [self.field_id]).fetchall()]

        for i,data in enumerate(self.data):
            data["closed"] = i not in self.opened_ids

    def __init__(self, field_id:int):
        self.field_id = field_id
        self.opened_ids = []
        self.reload()

    # 宝箱やとびらを開く
    def open(self, id):
        self.opened_ids.append(id)
        self.reload()

fieldobj_data = FieldObjData(1)

