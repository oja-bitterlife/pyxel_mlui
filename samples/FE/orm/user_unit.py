from orm import db,XUEMemoryDB
import dataclasses

# @dataclasses.dataclass
# class USER_UNIT_ITEM:

class USER_UNITS:
    def __init__(self, unit_name:str):
        self.unit_name = unit_name
        self.cursor = db.cursor

    def load(self):
        sql = f"""
            SELECT * FROM user_unit_params
        """
        row = self.cursor.execute(sql).fetchone()
        print(row)
