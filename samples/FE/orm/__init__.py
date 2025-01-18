from xmlui.ext.db import XUEMemoryDB

print("start load database")

# DBの読み込み
db = XUEMemoryDB.empty()
db.attach("assets/data/game.db")
db.attach("assets/data/user.db")

# 読み込んだテーブルの一覧
print("loaded tables:")
raws = db.cursor.execute("SELECT * from sqlite_master where type='table'").fetchall()
for raw in raws:
    print(f"  {raw['name']}")

# CSVの読み込み
csvs = [
    "data_item",
    "data_unit_class",
    "data_unit_levelup",
    "user_unit_params",
    "user_unit_stocks",
]
for csv_name in csvs:
    db.import_csv(csv_name, f"assets/data/{csv_name}.csv")
