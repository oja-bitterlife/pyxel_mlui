from xmlui.ext.db import XUEMemoryDB

print("load_database")

# DBの読み込み
db = XUEMemoryDB.empty()
db.attach("assets/data/game.db")
db.attach("assets/data/user.db")

# CSVの読み込み
csvs = [
    "data_item",
    "data_unit_class",
    "data_unit_init",
    "data_unit_levelup",
]
for csv_name in csvs:
    db.import_csv(csv_name, f"assets/data/{csv_name}.csv")

