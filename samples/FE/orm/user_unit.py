from orm import db,XUEMemoryDB
import dataclasses

@dataclasses.dataclass
class USER_UNIT_PARAM:
    unit_name:str

class USER_UNITS:
    def __init__(self, unit_name:str):
        self.unit_name = unit_name
        self.cursor = db.cursor

    def load(self):
        sql = f"""
            SELECT * FROM user_unit_params WHERE UNIT_NAME='{self.unit_name}'
        """
        data = dict(self.cursor.execute(sql).fetchone())
        return USER_UNIT_PARAM(unit_name=data["UNIT_NAME"])

    @classmethod
    def get_all_names(cls):
        sql = f"""
            SELECT UNIT_NAME FROM user_unit_params
        """
        return [row[0] for row in db.cursor.execute(sql).fetchall()]
