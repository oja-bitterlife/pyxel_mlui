from orm import db
from orm.user_enemy_state import UserEnemyState

class UserUnits:
    @classmethod
    def get_unit_names(cls) -> list[str]:
        sql = f"""
            SELECT UNIT_NAME FROM data_unit_init
        """
        return [row[0] for row in db.execute(sql).fetchall()]

    @classmethod
    def get_unit_id(cls, unit_name:str) -> int:
        sql = f"""
            SELECT UNIT_ID FROM data_unit_init WHERE UNIT_NAME=?
        """
        return db.execute(sql, (unit_name,)).fetchone()[0]

    @classmethod
    def get_map_enemies(cls, map_id:int) -> list[UserEnemyState]:
        sql = f"""
            SELECT ENEMY_ID FROM data_enemy_init WHERE MAP_ID=?
        """
        return [UserEnemyState(data[0]) for data in db.execute(sql, (map_id,)).fetchall()]
