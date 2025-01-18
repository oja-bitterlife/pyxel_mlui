from orm import db,XUEMemoryDB
import dataclasses

@dataclasses.dataclass()
class USER_UNIT_STOCK_ITEM:
    unit_name:str
    item_name:str
    equip:bool|None

    def save(self, db:XUEMemoryDB):
        db.cursor.execute(f"INSERT INTO USER_UNIT_STOCKS VALUES (?, ?, ?)", (self.unit_name, self.item_name, self.equip))

# ユニットの所持品を調べる
class USER_UNIT_STOCKS:
    def __init__(self, unit_name:str):
        self.unit_name = unit_name
        self.cursor = db.cursor

    @property
    def stocks(self) -> list[USER_UNIT_STOCK_ITEM]:
        rows = self.cursor.execute(f"SELECT * FROM USER_UNIT_STOCKS WHERE unit_name = '{self.unit_name}'").fetchall()
        return [USER_UNIT_STOCK_ITEM(item["UNIT_NAME"], item["ITEM_NAME"], item["EQUIP"]) for item in rows]

    @property
    def equiped(self) -> USER_UNIT_STOCK_ITEM | None:
        for stock in self.stocks:
            if stock.equip:
                return stock
        return None
