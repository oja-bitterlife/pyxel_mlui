from xmlui.ext.db import XUXMemoryDB

game_db = XUXMemoryDB.load("assets/data/game.db")
user_db = XUXMemoryDB.load("assets/data/user.db")

# ユーザーデータ
# *****************************************************************************
# セーブデータ。といいつつサンプルではセーブしないので適当で
class UserSave:
    def __init__(self, name:str):
        self.pc = [
            {"lv":1, "name":"おじゃ１", "hp":1, "mp":3, "fb":0},
            {"lv":1, "name":"おじゃ２", "hp":2, "mp":2, "fb":0},
            {"lv":1, "name":"おじゃ３", "hp":3, "mp":1, "fb":1},
            {"lv":1, "name":"おじゃ４", "hp":4, "mp":0, "fb":1},
        ]
        self.gil = 123456
 
user_save = UserSave("おじゃ１")

# ユーザーステータスデータアクセス
class UserData:
    def reload_db(self):
        sql = """
            SELECT * from user_data
            INNER JOIN _level_data ON user_data.lv == _level_data.lv
        """
        self.player_data = [dict(data) for data in user_db.execute(sql).fetchall()]
        self.party_data = dict(user_db.execute("SELECT * from party_data").fetchone())

    def __init__(self):
        # セーブデータからの復帰
        for pc in user_save.pc:
            user_db.execute("INSERT INTO user_data (lv, name, hp, mp, fb) VALUES (?, ?, ?, ?, ?)", [pc["lv"], pc["name"], pc["hp"], pc["mp"], pc["fb"]])
        user_db.execute("INSERT INTO party_data (gil) VALUES (?)", [user_save.gil])

        self.reload_db()

    @property
    def gil(self):
        return self.party_data["gil"]
    @gil.setter
    def gil(self, value):
        user_db.execute("UPDATE party_data SET gil=?", [value])
        user_db.connection.commit()
        self.reload_db()

user_data = UserData()

#print(user_data.player_data)


# エネミーデータアクセス
class EnemyData:
    def __init__(self, party_id):
        sql = """
            SELECT name,size,x,y FROM enemy_party
            INNER JOIN enemy_data ON enemy_party.enemy_id = enemy_data.id 
            WHERE party_id = ?
        """
        self.data = [dict(data) for data in game_db.execute(sql, [party_id]).fetchall()]

enemy_data = EnemyData(1)

#print(enemy_data.data)
