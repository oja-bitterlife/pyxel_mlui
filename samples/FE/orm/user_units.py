from orm import db
from orm.user_unit_state import USER_UNIT_STATE

class USER_UNITS:
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
        return db.execute(sql, (unit_name)).fetchone()[0]
