from db import game_db,user_db

# アイテムデータ
# *****************************************************************************
class BuyList:
    @classmethod
    def get(cls, shop_id:int) -> list[dict]:
        sql = """
            SELECT name,buy,item_data.id as item_id FROM shop_item
            INNER JOIN item_data ON shop_item.item_id = item_data.id
            WHERE shop_id = ?
        """
        return [dict(row) for row in game_db.execute(sql, [shop_id]).fetchall()]

    @classmethod
    def add(cls, item_id:int, num:int):
        for _ in range(num):
            user_db.execute("INSERT INTO has_items (item_id) VALUES (?)", [item_id])

class SellList:
    # 空欄にはNoneが入る
    @classmethod
    def get(cls) -> list[dict]:
        sql = """
            SELECT item_id,COUNT(item_id) as num FROM has_items GROUP BY item_id
        """
        data = [dict(data) for data in user_db.execute(sql).fetchall()]
        for item in data:
            item |= dict(game_db.execute("SELECT name,sell FROM item_data WHERE id = ?", [item["item_id"]]).fetchone())

        return data

    @classmethod
    def set(cls, shop_id:int, data:list):
        user_db.execute("DELETE FROM has_items")  # 一旦allクリア
        # insertで入れ直す
        for item_id, num in data:
            for _ in range(num):
                user_db.execute("INSERT INTO has_items (item_id) VALUES (?)", [item_id])
 