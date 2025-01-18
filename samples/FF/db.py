from xmlui.ext.db import XUEMemoryDB

game_db = XUEMemoryDB.load("assets/data/game.db").cursor
user_db = XUEMemoryDB.load("assets/data/user.db").cursor

# ユーザーデータ
# *****************************************************************************
# セーブデータ。といいつつサンプルではセーブしないので適当で
class UserSave:
    def __init__(self, name:str):
        self.pc = [
            {"id":1, "lv":1, "name":"おじゃあ", "hp":1, "mp":3, "fb":0},
            {"id":2, "lv":1, "name":"おじゃい", "hp":2, "mp":2, "fb":0},
            {"id":3, "lv":1, "name":"おじゃう", "hp":3, "mp":1, "fb":1},
            {"id":4, "lv":1, "name":"おじゃえ", "hp":4, "mp":0, "fb":1},
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

    def get_lives(self):
        return [data for data in self.player_data if data["hp"] > 0]

    def set_hp(self, index, hp):
        id = self.player_data[index]["id"]
        user_db.execute("UPDATE user_data SET hp=? WHERE id=?", [hp, id])
        user_db.connection.commit()
        self.reload_db()

user_data = UserData()

#print(user_data.player_data)


# エネミーデータアクセス
class EnemyData:
    def __init__(self, party_id):
        sql = """
            SELECT name,size,x,y,next_l,next_r,next_u,next_d FROM enemy_party
            INNER JOIN enemy_data ON enemy_party.enemy_id = enemy_data.id
            INNER JOIN enemy_arrange ON enemy_party.arrange_id = enemy_arrange.id and enemy_party.arrange_no = enemy_arrange.no
            WHERE party_id = ?
        """
        self.data = [dict(data) for data in game_db.execute(sql, [party_id]).fetchall()]

enemy_data = EnemyData(1)
#print(enemy_data.data)
