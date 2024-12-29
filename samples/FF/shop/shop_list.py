from db import game_db,user_db

# アイテムデータ
# *****************************************************************************
class BuyList:
    def __init__(self, shop_id:int):
        self.shop_id = shop_id
        sql = """
            SELECT name,buy from shop_item
            INNER JOIN item_data ON shop_item.item_id = item_data.id
            WHERE shop_id = ?
        """
        self.data = [dict(row) for row in game_db.execute(sql, [self.shop_id]).fetchall()]

class SellList:
    # 空欄にはNoneが入る
    def __init__(self, shop_id:int):
        sql = """
            SELECT item_id,COUNT(item_id) as num FROM has_items GROUP BY item_id
        """
        self.data = [dict(data) for data in user_db.execute(sql).fetchall()]
        for data in self.data:
            data |= dict(game_db.execute("SELECT name,sell FROM item_data WHERE id = ?", [data["item_id"]]).fetchone())

print(SellList(1))