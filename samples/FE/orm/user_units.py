from orm import db
from orm.user_unit_state import USER_UNIT_STATE

class USER_UNITS:
    @classmethod
    def load(cls, unit_name:str) -> USER_UNIT_STATE:
        return USER_UNIT_STATE(unit_name)

    @classmethod
    def get_unit_names(cls):
        sql = f"""
            SELECT UNIT_NAME FROM user_unit_params
        """
        return [row[0] for row in db.cursor.execute(sql).fetchall()]

    @classmethod
    def reset_unit_hps(cls):
        for unit_name in cls.get_unit_names():
            state = cls.load(unit_name)
            state.reset_hp()
