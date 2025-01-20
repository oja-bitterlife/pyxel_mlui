from orm import db
import dataclasses

@dataclasses.dataclass()
class UserUnitStockItem:
    unit_id:str
    item_name:str
    equip:bool

# ユニットの所持品を調べる
class UserUnitStocks:
    def __init__(self, unit_id:int):
        self.unit_id = unit_id

    @property
    def stocks(self) -> list[UserUnitStockItem]:
        rows = db.execute(f"SELECT * FROM USER_UNIT_STOCKS WHERE UNIT_ID=?", (self.unit_id,)).fetchall()
        return [UserUnitStockItem(item["UNIT_ID"], item["ITEM_NAME"], item["EQUIP"]) for item in rows]

    @property
    def equiped(self) -> UserUnitStockItem | None:
        for stock in self.stocks:
            if stock.equip:
                return stock
        return None

    @classmethod
    def append(cls, unit_id:int, item_name:str, equip:bool=False):
        db.execute(f"INSERT INTO USER_UNIT_STOCKS (UNIT_ID, ITEM_NAME, EQUIP) VALUES (?, ?, ?)", (unit_id, item_name, equip))
