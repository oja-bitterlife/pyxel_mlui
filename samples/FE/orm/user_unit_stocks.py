from orm import db
import dataclasses

@dataclasses.dataclass()
class USER_UNIT_STOCK_ITEM:
    unit_id:str
    item_name:str
    equip:bool|None

    def save(self):
        db.execute(f"INSERT INTO USER_UNIT_STOCKS (UNIT_ID, ITEM_NAME, EQUIP) VALUES (?, ?, ?)", (self.unit_id, self.item_name, self.equip))

# ユニットの所持品を調べる
class USER_UNIT_STOCKS:
    def __init__(self, unit_id:int):
        self.unit_id = unit_id
        self.cursor = db.cursor

    @property
    def stocks(self) -> list[USER_UNIT_STOCK_ITEM]:
        rows = db.execute(f"SELECT * FROM USER_UNIT_STOCKS WHERE unit_id='{self.unit_id}'").fetchall()
        return [USER_UNIT_STOCK_ITEM(item["UNIT_ID"], item["ITEM_NAME"], item["EQUIP"]) for item in rows]

    @property
    def equiped(self) -> USER_UNIT_STOCK_ITEM | None:
        for stock in self.stocks:
            if stock.equip:
                return stock
        return None
