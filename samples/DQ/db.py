# DBはサンプルでは使わないので固定値で

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
