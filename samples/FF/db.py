from xmlui.ext.db import XUXMemoryDB

game_db = XUXMemoryDB.load("assets/data/game.db")
user_db = XUXMemoryDB.load("assets/data/user.db")

# ユーザーデータ
# *****************************************************************************
# セーブデータ。といいつつサンプルではセーブしないので適当で
class UserSave:
    def __init__(self, name:str):
        self.pc = [
            {"lv":1, "name":"おじゃ１", "hp":1, "mp":3},
            {"lv":1, "name":"おじゃ２", "hp":2, "mp":2},
            {"lv":1, "name":"おじゃ３", "hp":3, "mp":1},
            {"lv":1, "name":"おじゃ４", "hp":4, "mp":0},
        ]
        self.gil = 123456
 
user_save = UserSave("おじゃ１")

# ユーザーステータスデータアクセス
class UserData:
    def reload_db(self):
        self.user_data = [dict(data) for data in user_db.execute("SELECT * from user_data").fetchall()]
        # level_data = dict(game_db.execute("SELECT * from level_data where level=?", [user_data["lv"]]).fetchone())
        self.party_data = dict(user_db.execute("SELECT * from party_data").fetchone())

    def __init__(self):
        # セーブデータからの復帰
        for pc in user_save.pc:
            user_db.execute("INSERT INTO user_data (lv, name, hp, mp) VALUES (?, ?, ?, ?)", [pc["lv"], pc["name"], pc["hp"], pc["mp"]])
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
