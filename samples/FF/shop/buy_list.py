from db import game_db

# ユーザーデータ
# *****************************************************************************
# セーブデータ。といいつつサンプルではセーブしないので適当で
class BuyList:
    def __init__(self, shop_id:int):
        self.shop_id = shop_id
        sql = """
            SELECT * from shop_item
            INNER JOIN item ON shop_item.item_id = item.id
            WHERE shop_id = ?
        """
        self.data = [dict(row) for row in game_db.execute(sql, [self.shop_id]).fetchall()]
