import os,os.path
os.chdir(os.path.dirname(__file__))

import sys
sys.path.append("..")
sys.path.append("../..")


from xmlui.ext.db import XUEMemoryDB

db = XUEMemoryDB.empty()
db.attach("assets/data/game.db")
db.attach("assets/data/user.db")

csvs = [
    "data_item",
    "data_unit_class",
    "data_unit_init",
    "data_unit_levelup",
]
for csv_name in csvs:
    print(f"import: {csv_name}")
    db.import_csv(csv_name, f"assets/data/{csv_name}.csv")

